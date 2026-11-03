# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Safety and failure semantics for the build orchestrator (no native builds)."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("aimium_build", REPO / "aimium/tools/build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class BuildFoundationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name)
        self.root = self.workspace / "src"
        (self.root / "aimium/build").mkdir(parents=True)
        shutil.copyfile(REPO / "aimium/build/targets.json", self.root / "aimium/build/targets.json")
        self.target = build.load_target(self.root, "linux-x64")
        self.out = build.output_directory(self.root, None, self.target)
        self.identity = {"commit": "a" * 40, "dirty": False}
        self.tools = {name: None for name in ("git", "gclient", "autoninja", "gn", "clang")}

    def inspect(self, host="Linux", machine="x86_64", sparse=False):
        with mock.patch.object(build, "_git_config_present", return_value=True), \
             mock.patch.object(build, "git", return_value="true" if sparse else "false"):
            return build.preflight(self.root, self.target, self.out, self.identity, self.tools,
                                   host_os=host, machine=machine, free_bytes=200 * 1024**3)

    @staticmethod
    def check(result, name):
        return next(item for item in result["checks"] if item["name"] == name)

    def test_supported_target_plans_have_distinct_native_cpu_and_executable(self):
        expected = {
            "linux-x64": ("linux", "x64", "chrome"),
            "win-x64": ("win", "x64", "chrome.exe"),
            "mac-arm64": ("mac", "arm64", "Chromium.app/Contents/MacOS/Chromium"),
            "mac-x64": ("mac", "x64", "Chromium.app/Contents/MacOS/Chromium"),
        }
        for name, (os_name, cpu, executable) in expected.items():
            with self.subTest(name=name):
                target = build.load_target(self.root, name)
                out = build.output_directory(self.root, None, target)
                plan = build.make_plan(self.root, target, out, self.identity, self.tools)
                self.assertEqual(os_name, plan["gn_args"]["target_os"])
                self.assertEqual(cpu, plan["gn_args"]["target_cpu"])
                self.assertEqual(str(out / executable), plan["expected_executable"])
                self.assertFalse(plan["release_eligible"])
                self.assertNotIn("chrome_pgo_phase", plan["gn_args"])
                self.assertFalse(out.exists())

    def test_unknown_target_is_rejected(self):
        with self.assertRaisesRegex(build.BuildError, "Unsupported target"):
            build.load_target(self.root, "freebsd-x64")

    def test_unsupported_host_is_rejected(self):
        result = self.inspect(host="FreeBSD")
        self.assertFalse(self.check(result, "native_host")["ok"])

    def test_cross_arch_is_rejected_until_explicitly_supported(self):
        result = self.inspect(machine="aarch64")
        self.assertFalse(self.check(result, "native_host")["ok"])

    def test_sparse_and_incomplete_checkout_are_rejected_independently(self):
        result = self.inspect(sparse=True)
        for name in ("full_checkout", "gclient_workspace", "gclient_dependencies", "dependency_markers", "tool_gn"):
            with self.subTest(name=name):
                self.assertFalse(self.check(result, name)["ok"])
        self.assertFalse(self.out.exists())

    def test_gclient_metadata_is_never_executed(self):
        indicator = self.workspace / "executed"
        (self.workspace / ".gclient_entries").write_text(
            f"entries = __import__('pathlib').Path({str(indicator)!r}).touch()\n", encoding="utf-8")
        ok, detail = build.check_dependency_graph(self.root)
        self.assertFalse(ok)
        self.assertIn("Invalid .gclient_entries", detail)
        self.assertFalse(indicator.exists())

    def test_metadata_rejects_path_traversal(self):
        (self.workspace / ".gclient_entries").write_text(
            "entries = {'src': 'origin', 'src/../other': 'origin'}\n", encoding="utf-8")
        ok, _ = build.check_dependency_graph(self.root)
        self.assertFalse(ok)

    def test_dependency_graph_checks_actual_path_presence(self):
        (self.workspace / ".gclient_entries").write_text(
            "entries = {'src': 'origin', 'src/v8': 'origin'}\n", encoding="utf-8")
        ok, detail = build.check_dependency_graph(self.root)
        self.assertFalse(ok)
        self.assertIn("src/v8", detail)
        (self.root / "v8").mkdir()
        self.assertTrue(build.check_dependency_graph(self.root)[0])

    def test_output_cannot_escape_checkout(self):
        for value in ("../elsewhere", "out/../../elsewhere", "out", str(self.workspace / "absolute")):
            with self.subTest(value=value), self.assertRaises(build.BuildError):
                build.output_directory(self.root, value, self.target)

    def test_output_symlink_cannot_escape_checkout(self):
        outside = self.workspace / "outside"
        outside.mkdir()
        try:
            (self.root / "out").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks requires platform privileges.")
        with self.assertRaises(build.BuildError):
            build.output_directory(self.root, None, self.target)

    def test_existing_arguments_are_preserved(self):
        self.out.mkdir(parents=True)
        argument_file = self.out / "args.gn"
        original = "is_debug = true\n"
        argument_file.write_text(original, encoding="utf-8")
        result = self.inspect()
        self.assertFalse(self.check(result, "output_arguments")["ok"])
        self.assertEqual(original, argument_file.read_text(encoding="utf-8"))

    def test_dirty_source_is_explicit_failure(self):
        self.identity["dirty"] = True
        self.assertFalse(self.check(self.inspect(), "source_clean")["ok"])

    def test_dry_run_has_no_writes_or_build_process(self):
        with mock.patch.object(build, "source_identity", return_value=self.identity), \
             mock.patch.object(build, "tool_paths", return_value=self.tools), \
             mock.patch.object(build, "preflight", return_value={"ok": False, "checks": []}), \
             mock.patch.object(build, "run_build") as run, \
             contextlib.redirect_stdout(io.StringIO()):
            code = build.main(["build", "--target", "linux-x64", "--source-root", str(self.root), "--dry-run"])
        self.assertEqual(2, code)
        run.assert_not_called()
        self.assertFalse(self.out.exists())

    def test_build_requires_preflight(self):
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools)
        with self.assertRaisesRegex(build.BuildError, "preflight"):
            build.run_build(self.root, self.out, plan)
        self.assertFalse(self.out.exists())

    def test_failed_gn_stops_before_compilation_and_records_failure(self):
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools)
        plan["preflight"] = {"ok": True}
        with mock.patch.object(build.subprocess, "run", return_value=SimpleNamespace(returncode=7)) as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = build.run_build(self.root, self.out, plan)
        self.assertEqual(1, code)
        self.assertEqual(1, run.call_count)
        receipt = json.loads((self.out / "aimium-build-manifest.json").read_text())
        self.assertEqual("failed", receipt["status"])
        self.assertEqual([{"step": "generate", "exit_code": 7}], receipt["step_results"])
        self.assertFalse(receipt["release_eligible"])

    def test_successful_commands_without_browser_are_not_a_successful_build(self):
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools)
        plan["preflight"] = {"ok": True}
        with mock.patch.object(build.subprocess, "run", return_value=SimpleNamespace(returncode=0)), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, build.run_build(self.root, self.out, plan))
        self.assertEqual("failed", plan["status"])
        self.assertIn("executable is absent", plan["error"])

    def test_browser_test_option_never_runs_the_whole_test_suite(self):
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools, browser_tests=True)
        commands = {entry["step"]: entry["argv"] for entry in plan["commands"]}
        self.assertIn("browser_tests", commands["compile"])
        self.assertIn(f"--gtest_filter={build.BROWSER_TEST_FILTER}", commands["run_aimium_tests"])
        self.assertIn("--test-launcher-jobs=1", commands["run_aimium_tests"])
        self.assertEqual("not_run", plan["native_tests"]["status"])

    def test_linux_ui_tests_use_vpython_and_explicit_xvfb(self):
        self.tools["vpython3"] = "/prepared/depot_tools/vpython3"
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools, browser_tests=True)
        for step in ("list_aimium_tests", "run_aimium_tests"):
            command = next(item["argv"] for item in plan["commands"] if item["step"] == step)
            self.assertEqual(self.tools["vpython3"], command[0])
            self.assertEqual(str(self.root / "testing/xvfb.py"), command[1])
            self.assertIn("--use-xvfb", command)

    def test_linux_ui_test_preflight_rejects_missing_vpython(self):
        with mock.patch.object(build, "_git_config_present", return_value=False):
            result = build.preflight(self.root, self.target, self.out, self.identity, self.tools,
                                     host_os="Linux", machine="x86_64", free_bytes=200 * 1024**3,
                                     browser_tests=True)
        self.assertFalse(self.check(result, "tool_vpython3")["ok"])

    def test_empty_test_filter_result_cannot_pass_as_native_tests(self):
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools, browser_tests=True)
        plan["preflight"] = {"ok": True}
        with mock.patch.object(build.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="")) as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, build.run_build(self.root, self.out, plan))
        self.assertEqual(3, run.call_count)
        self.assertEqual("failed", plan["status"])
        self.assertNotEqual("passed", plan["native_tests"]["status"])
        self.assertIn("No AimiumUI*", plan["error"])

    def test_source_change_during_compile_is_reported_as_unverified_failure(self):
        self.out.mkdir(parents=True)
        (self.out / "chrome").write_bytes(b"unit-test-placeholder")
        plan = build.make_plan(self.root, self.target, self.out, self.identity, self.tools)
        plan["preflight"] = {"ok": True}
        with mock.patch.object(build.subprocess, "run", return_value=SimpleNamespace(returncode=0)), \
             mock.patch.object(build, "source_identity", return_value={"commit": "b" * 40, "dirty": False}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, build.run_build(self.root, self.out, plan))
        self.assertEqual("failed", plan["status"])
        self.assertIn("Source changed", plan["error"])


if __name__ == "__main__":
    unittest.main()
