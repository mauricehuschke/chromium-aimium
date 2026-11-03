#!/usr/bin/env python3
# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Plan and run native development builds in an already prepared checkout.

This tool never clones, fetches, syncs, or resets source. Provision host tools
and dependencies beforehand. The underlying Chromium/depot_tools commands can
populate their hermetic runtime caches, including vpython's test environment.
`plan` is portable; `check` and `build --dry-run` require native prerequisites.
The presence checks find common incomplete checkouts. GN/build still validate
SDK compatibility and dependency contents; passing preflight is not a build.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tempfile

SOURCE_ROOT = Path(__file__).resolve().parents[2]
MIN_FREE_GIB = 100
BROWSER_TEST_FILTER = "AimiumUIBrowserTest.*:AimiumUIDisabledBrowserTest.*"
DEPENDENCY_MARKERS = (
    "base/BUILD.gn",
    "third_party/blink/renderer/BUILD.gn",
    "v8/include/v8.h",
    "third_party/skia/include/core/SkCanvas.h",
    "third_party/boringssl/src/include/openssl/ssl.h",
)


class BuildError(Exception):
    """A readable failure before a build can safely continue."""


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError(f"Cannot read {path}: {exc}") from exc


def load_target(root, name):
    config = read_json(root / "aimium/build/targets.json")
    if name not in config["targets"]:
        raise BuildError(f"Unsupported target {name!r}; choose {', '.join(config['targets'])}.")
    target = dict(config["targets"][name])
    target["id"] = name
    target["gn_args"] = dict(config["common_gn_args"],
                             target_os=target["target_os"],
                             target_cpu=target["target_cpu"])
    return target


def render_gn_args(arguments):
    # JSON strings and booleans have the GN spelling required by these values.
    return "".join(f"{key} = {json.dumps(value)}\n"
                   for key, value in sorted(arguments.items()))


def output_directory(root, value, target):
    root = root.resolve()
    relative = Path(value or f"out/Aimium/{target['id']}")
    if relative.is_absolute() or ".." in relative.parts:
        raise BuildError("--out-dir must be a relative directory below out/ without '..'.")
    result = (root / relative).resolve()
    permitted = (root / "out").resolve()
    # Reject an out/ symlink leaving the source tree, too.
    if not permitted.is_relative_to(root) or not result.is_relative_to(permitted) or result == permitted:
        raise BuildError("--out-dir must stay inside this checkout's out/ directory.")
    return result


def git(root, *arguments):
    try:
        result = subprocess.run(["git", "-C", str(root), *arguments],
                                capture_output=True, text=True, check=True,
                                timeout=60)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise BuildError(f"Cannot inspect source with git {' '.join(arguments)}: {exc}") from exc


def file_hash(path):
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_identity(root):
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise BuildError("--source-root must be the root of the Chromium Git checkout.")
    upstream = read_json(root / "aimium/upstream.json")
    if (not isinstance(upstream, dict) or upstream.get("schema_version") != 1
            or not isinstance(upstream.get("commit"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", upstream["commit"])):
        raise BuildError("aimium/upstream.json requires schema_version 1 and a full commit SHA.")
    parts = {}
    try:
        for line in (root / "chrome/VERSION").read_text(encoding="utf-8").splitlines():
            key, value = line.split("=", 1)
            parts[key] = value
        version = ".".join(parts[key] for key in ("MAJOR", "MINOR", "BUILD", "PATCH"))
    except (OSError, ValueError, KeyError) as exc:
        raise BuildError("Cannot read chrome/VERSION from this checkout.") from exc
    if version != upstream.get("version"):
        raise BuildError("chrome/VERSION differs from aimium/upstream.json; review the upstream pin first.")
    status = git(root, "status", "--porcelain=v1", "--untracked-files=normal")
    return {
        "root": str(root.resolve()),
        "commit": git(root, "rev-parse", "HEAD"),
        "dirty": bool(status),
        "version": version,
        "upstream": upstream,
        "deps_sha256": file_hash(root / "DEPS"),
        "gclient_entries_sha256": file_hash(root.parent / ".gclient_entries"),
    }


def check_dependency_graph(root):
    """Read gclient's metadata as data, never execute its Python content."""
    path = root.parent / ".gclient_entries"
    if not path.is_file():
        return False, "Missing parent .gclient_entries; complete gclient sync and hooks explicitly first."
    try:
        if path.stat().st_size > 8 * 1024 * 1024:
            raise ValueError("metadata larger than 8 MiB")
        assignments = ast.parse(path.read_text(encoding="utf-8")).body
        entries = None
        for statement in assignments:
            if (isinstance(statement, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "entries" for t in statement.targets)):
                entries = ast.literal_eval(statement.value)
        if not isinstance(entries, dict) or root.name not in entries:
            raise ValueError(f"no entries dictionary for solution {root.name!r}")
        relevant = []
        for key, value in entries.items():
            if not isinstance(key, str):
                raise ValueError("non-string dependency path")
            path_parts = PurePosixPath(key)
            if path_parts.is_absolute() or ".." in path_parts.parts or "\\" in key:
                raise ValueError("dependency path escapes the gclient workspace")
            if key.startswith(root.name + "/") and value is not None:
                relevant.append(key)
        if not relevant:
            raise ValueError("no dependency entries for this solution")
        missing = [key for key in relevant if not (root.parent / key).exists()]
        if missing:
            return False, f"Missing {len(missing)} gclient dependency paths: {', '.join(missing[:8])}."
        return True, f"{len(relevant)} recorded dependency paths exist; GN still validates their contents."
    except (OSError, ValueError, SyntaxError) as exc:
        return False, f"Invalid .gclient_entries: {exc}"


def normalize_arch(machine):
    return {"amd64": "x64", "x86_64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(machine.lower(), machine.lower())


def tool_paths(root, target, which=shutil.which):
    gclient = which("gclient")
    # Invoke the Python implementation explicitly; Windows .bat shims otherwise
    # introduce shell argument interpretation even when shell=False is used.
    depot = Path(gclient).resolve().parent if gclient else None
    autoninja = depot / "autoninja.py" if depot else None
    return {
        "git": which("git"),
        "gclient": gclient,
        "vpython3": which("vpython3"),
        "autoninja": str(autoninja) if autoninja and autoninja.is_file() else None,
        "gn": str(root / target["gn_binary"]) if (root / target["gn_binary"]).is_file() else None,
        "clang": str(root / target["clang_binary"]) if (root / target["clang_binary"]).is_file() else None,
    }


def preflight(root, target, out, identity, tools, min_free_gib=MIN_FREE_GIB,
              host_os=None, machine=None, free_bytes=None, browser_tests=False):
    host_os = host_os or platform.system()
    machine = normalize_arch(machine or platform.machine())
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    native = host_os == target["host_os"] and machine == target["host_arch"]
    add("native_host", native,
        f"Host {host_os}/{machine}; target requires {target['host_os']}/{target['host_arch']}. Cross-compilation is not configured.")
    add("python", sys.version_info >= (3, 11), "Aimium build tooling requires Python 3.11 or newer.")
    sparse = git(root, "config", "--get", "core.sparseCheckout") if _git_config_present(root, "core.sparseCheckout") else "false"
    add("full_checkout", sparse.lower() != "true", "Sparse editing checkouts cannot build Chromium; provision a separate full gclient checkout.")
    add("gclient_workspace", (root.parent / ".gclient").is_file(), "The source directory must be a solution beneath a prepared .gclient workspace.")
    graph_ok, graph_detail = check_dependency_graph(root)
    add("gclient_dependencies", graph_ok, graph_detail)
    missing = [value for value in DEPENDENCY_MARKERS if not (root / value).is_file()]
    add("dependency_markers", not missing, "Missing: " + ", ".join(missing) if missing else "Required source and dependency markers exist.")
    add("source_clean", not identity["dirty"], "Build receipts require a clean committed source tree, including untracked files. Commit your work or use a clean checkout; this tool never resets it.")
    required_tools = ["git", "gclient", "autoninja", "gn", "clang"]
    if browser_tests and target["host_os"] == "Linux":
        required_tools.append("vpython3")
    for name in required_tools:
        path = tools.get(name)
        add(f"tool_{name}", path is not None, str(path) if path else f"Missing {name}; provision depot_tools and run the Chromium hooks explicitly.")
    if free_bytes is None:
        existing = out
        while not existing.exists():
            existing = existing.parent
        free_bytes = shutil.disk_usage(existing).free
    add("disk_space", free_bytes >= min_free_gib * 1024**3,
        f"{free_bytes / 1024**3:.1f} GiB available; configured minimum {min_free_gib} GiB. This is a capacity check, not a build-size prediction.")
    args_file = out / "args.gn"
    matches = not args_file.exists() or args_file.read_text(encoding="utf-8") == render_gn_args(target["gn_args"])
    add("output_arguments", matches, "Existing args.gn must match the plan exactly; choose a fresh --out-dir for other configurations.")
    if native and host_os == "Linux":
        sysroots = list((root / "build/linux").glob("*_amd64-sysroot/usr/include"))
        add("linux_sysroot", bool(sysroots), "Linux requires the amd64 sysroot installed by Chromium hooks and the host dependencies in docs/linux/build_instructions.md.")
        if browser_tests:
            for executable in ("Xvfb", "openbox"):
                add(f"linux_test_{executable}", bool(shutil.which(executable)),
                    f"Optional native UI tests use Chromium's vpython3/Xvfb wrapper and require {executable}.")
    if native and host_os == "Darwin":
        add("mac_sdk_tools", bool(shutil.which("xcrun") and shutil.which("xcode-select")),
            "Install/select Xcode and the SDK required by this revision; GN validates SDK versions and license acceptance.")
    if native and host_os == "Windows":
        installer = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft Visual Studio/Installer/vswhere.exe"
        installed = os.environ.get("vs2026_install") or os.environ.get("VSINSTALLDIR")
        add("windows_toolchain", bool(installer.is_file() or (installed and Path(installed).is_dir())),
            "Install Visual Studio 2026 C++/ATL/MFC and the SDK required by docs/windows_build_instructions.md. GN validates exact versions; finding vswhere alone is not proof of a compatible installation.")
    return {"ok": all(item["ok"] for item in checks), "checks": checks}


def _git_config_present(root, name):
    result = subprocess.run(["git", "-C", str(root), "config", "--get", name],
                            capture_output=True, timeout=30)
    return result.returncode == 0


def make_plan(root, target, out, identity, tools, jobs=None, browser_tests=False):
    # Both paths must use the same spelling before relative_to(): resolving
    # just the output expands Windows short names and macOS /var symlinks.
    root = root.resolve()
    out = out.resolve()
    gn = tools["gn"] or str(root / target["gn_binary"])
    autoninja = tools["autoninja"] or "<depot_tools>/autoninja.py"
    relative = out.relative_to(root).as_posix()
    compile_args = [sys.executable, autoninja, "-C", relative]
    if jobs is not None:
        compile_args += ["-j", str(jobs)]
    compile_args.append("chrome")
    if browser_tests:
        compile_args.append("browser_tests")
    commands = [
        {"step": "generate", "argv": [gn, "gen", relative, "--fail-on-unused-args"]},
        {"step": "compile", "argv": compile_args},
    ]
    if browser_tests:
        binary = str(out / ("browser_tests.exe" if target["host_os"] == "Windows" else "browser_tests"))
        prefix = [tools.get("vpython3") or "<depot_tools>/vpython3", str(root / "testing/xvfb.py")] if target["host_os"] == "Linux" else []
        test_command = prefix + [binary, f"--gtest_filter={BROWSER_TEST_FILTER}"]
        if target["host_os"] == "Linux":
            test_command.append("--use-xvfb")
        commands.extend([
            {"step": "list_aimium_tests", "argv": test_command + ["--gtest_list_tests"]},
            {"step": "run_aimium_tests", "argv": test_command + ["--test-launcher-jobs=1"]},
        ])
    environment = {"DEPOT_TOOLS_UPDATE": "0", "DEPOT_TOOLS_METRICS": "0"}
    if target["host_os"] == "Windows":
        environment["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    return {
        "schema_version": 1,
        "status": "planned",
        "target": target["id"],
        "build_kind": "development",
        "release_eligible": False,
        "source": identity,
        "gn_args": target["gn_args"],
        "gn_args_text": render_gn_args(target["gn_args"]),
        "output_directory": str(out),
        "expected_executable": str(out / target["executable"]),
        "tools": tools,
        "environment_overrides": environment,
        "commands": commands,
        "native_tests": {"requested": browser_tests, "filter": BROWSER_TEST_FILTER, "status": "not_run"},
        "scope": "Development build. Optional AimiumUI* tests only; no signing, packaging, or integration certification.",
    }


def atomic_json(path, data):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
                                     dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def run_build(root, out, plan):
    if not plan.get("preflight", {}).get("ok"):
        raise BuildError("Build requires a successful preflight.")
    out.mkdir(parents=True, exist_ok=True)
    args_file = out / "args.gn"
    if args_file.exists():
        if args_file.read_text(encoding="utf-8") != plan["gn_args_text"]:
            raise BuildError("args.gn changed after preflight; refusing to overwrite it.")
    else:
        with args_file.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(plan["gn_args_text"])
    plan["status"] = "running"
    plan["started_at"] = datetime.now(timezone.utc).isoformat()
    plan["tool_sha256"] = {name: file_hash(Path(value)) if value else None for name, value in plan["tools"].items()}
    plan["python"] = {"executable": sys.executable, "version": platform.python_version()}
    depot = Path(plan["tools"]["gclient"]).resolve().parent if plan["tools"]["gclient"] else None
    try:
        plan["depot_tools_commit"] = git(depot, "rev-parse", "HEAD") if depot else None
    except BuildError:
        plan["depot_tools_commit"] = None
    plan["dependency_validation"] = "Recorded path presence and DEPS/entries hashes; actual dependency revisions and all SDK versions are not independently certified."
    plan["step_results"] = []
    manifest = out / "aimium-build-manifest.json"
    atomic_json(manifest, plan)
    environment = dict(os.environ, **plan["environment_overrides"])
    exit_code = 1
    try:
        for command in plan["commands"]:
            capture = command["step"] == "list_aimium_tests"
            result = subprocess.run(command["argv"], cwd=root, env=environment, check=False,
                                    capture_output=capture, text=capture)
            plan["step_results"].append({"step": command["step"], "exit_code": result.returncode})
            if capture and result.returncode:
                print(result.stdout, end="")
                print(result.stderr, end="", file=sys.stderr)
            if capture and not result.returncode:
                lines = result.stdout.splitlines()
                has_suite = any(re.match(r"^AimiumUI[^\s]*\.", line) for line in lines)
                has_test = any(re.match(r"^  [A-Za-z0-9_]", line) for line in lines)
                if not has_suite or not has_test:
                    raise BuildError("No AimiumUI* browser tests were discovered; refusing a vacuous test pass.")
            if command["step"] == "run_aimium_tests":
                plan["native_tests"]["status"] = "passed" if result.returncode == 0 else "failed"
            atomic_json(manifest, plan)
            if result.returncode:
                raise BuildError(f"{command['step']} failed with exit code {result.returncode}.")
        executable = Path(plan["expected_executable"])
        if not executable.is_file():
            raise BuildError("Build returned success but the expected browser executable is absent.")
        # A build cannot be attributed to the starting revision if someone changed
        # source during the compile. Keep the result explicitly unverified then.
        end_identity = source_identity(root)
        if end_identity["commit"] != plan["source"]["commit"] or end_identity["dirty"]:
            raise BuildError("Source changed during compilation; the output is not a verified build of the recorded commit.")
        plan["status"] = "built"
        plan["executable_sha256"] = file_hash(executable)
        exit_code = 0
    except (BuildError, OSError, KeyboardInterrupt) as exc:
        plan["status"] = "failed"
        plan["error"] = str(exc) or "Build interrupted."
        print(plan["error"], file=sys.stderr)
    finally:
        plan["finished_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(manifest, plan)
    print(f"Build manifest: {manifest}")
    return exit_code


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "check", "build"))
    parser.add_argument("--target", required=True, help="linux-x64, win-x64, mac-arm64 or mac-x64")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--out-dir", help="relative path below out/; default out/Aimium/<target>")
    parser.add_argument("--jobs", type=positive_integer, help="optional compiler job limit")
    parser.add_argument("--min-free-gib", type=positive_integer, default=MIN_FREE_GIB)
    parser.add_argument("--browser-tests", action="store_true", help="also build browser_tests and run only AimiumUI* tests (Linux requires Xvfb)")
    parser.add_argument("--dry-run", action="store_true", help="perform checks and print the plan without writing files")
    options = parser.parse_args(argv)
    try:
        root = options.source_root.resolve()
        target = load_target(root, options.target)
        out = output_directory(root, options.out_dir, target)
        identity = source_identity(root)
        tools = tool_paths(root, target)
        plan = make_plan(root, target, out, identity, tools, options.jobs, options.browser_tests)
        if options.command != "plan":
            plan["preflight"] = preflight(root, target, out, identity, tools, options.min_free_gib,
                                          browser_tests=options.browser_tests)
        if options.command == "build" and not options.dry_run and plan["preflight"]["ok"]:
            return run_build(root, out, plan)
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if plan.get("preflight", {"ok": True})["ok"] else 2
    except (BuildError, OSError, ValueError) as exc:
        print(f"Aimium build: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
