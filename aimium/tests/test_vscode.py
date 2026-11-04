# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Exercise task handoff without invoking a native build or a compiler."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]


class VSCodeTaskTest(unittest.TestCase):
    def test_default_build_is_manual_and_preserves_windows_ninja_output(self):
        config = json.loads((REPO / ".vscode/tasks.json").read_text(encoding="utf-8"))
        builds = [task for task in config["tasks"]
                  if isinstance(task.get("group"), dict)
                  and task["group"].get("kind") == "build"
                  and task["group"].get("isDefault")]
        self.assertEqual(1, len(builds))
        task = builds[0]
        arguments = task["windows"]["args"]
        self.assertEqual("win-x64", arguments[arguments.index("--target") + 1])
        self.assertEqual("out/Aimium/win-x64-ninja",
                         arguments[arguments.index("--out-dir") + 1])
        self.assertIn("--browser-tests", arguments)
        self.assertEqual(1, task["runOptions"]["instanceLimit"])
        for configured in config["tasks"]:
            self.assertNotEqual("folderOpen", configured.get("runOptions", {}).get("runOn"))


@unittest.skipUnless(os.name == "nt", "Windows cmd.exe launcher integration")
class WindowsPythonLauncherTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="aimium vscode space ")
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name)
        self.source = self.workspace / "src"
        self.tools = self.source / "aimium/tools"
        self.tools.mkdir(parents=True)
        self.launcher = self.tools / "python.cmd"
        shutil.copyfile(REPO / "aimium/tools/python.cmd", self.launcher)
        self.probe = self.workspace / "argument probe.py"
        self.result = self.workspace / "probe result.json"
        self.probe.write_text(
            "import json, os, pathlib, sys\n"
            "pathlib.Path(sys.argv[1]).write_text(json.dumps({"
            "'args': sys.argv[2:], 'env': os.environ.get('AIMIUM_TEST_ENV'), "
            "'path': os.environ.get('PATH', '')}))\n"
            "sys.exit(27)\n", encoding="utf-8")
        self.environment = os.environ.copy()
        for name in ("AIMIUM_LOCAL_ENV", "AIMIUM_PYTHON", "AIMIUM_TEST_ENV"):
            self.environment.pop(name, None)

    def run_probe(self):
        # Same cmd.exe/call boundary as the VS Code Windows shell tasks.
        command = (f'call "{self.launcher}" "{self.probe}" '
                   f'"{self.result}" "an argument with spaces"')
        return subprocess.run(
            # cmd.exe parses /c itself; list2cmdline would add C-runtime-style
            # backslash quoting which cmd.exe does not understand.
            f'"{os.environ.get("ComSpec", "cmd.exe")}" /d /v:off /c {command}',
            cwd=self.source, env=self.environment, capture_output=True, text=True,
            timeout=30)

    def write_environment(self, path, marker):
        path.write_text(
            f'@echo off\nset "AIMIUM_PYTHON={sys.executable}"\n'
            f'set "AIMIUM_TEST_ENV={marker}"\n', encoding="utf-8")

    def test_sibling_environment_and_quoted_arguments_with_exit_status(self):
        self.write_environment(self.workspace / "env.cmd", "sibling")
        result = self.run_probe()
        self.assertEqual(27, result.returncode, result.stdout + result.stderr)
        observed = json.loads(self.result.read_text())
        self.assertEqual(["an argument with spaces"], observed["args"])
        self.assertEqual("sibling", observed["env"])

    def test_explicit_environment_overrides_sibling(self):
        self.write_environment(self.workspace / "env.cmd", "sibling")
        selected = self.workspace / "selected environment.cmd"
        self.write_environment(selected, "explicit")
        self.environment["AIMIUM_LOCAL_ENV"] = str(selected)
        result = self.run_probe()
        self.assertEqual(27, result.returncode, result.stdout + result.stderr)
        self.assertEqual("explicit", json.loads(self.result.read_text())["env"])

    def test_missing_explicit_environment_does_not_run_python(self):
        self.environment["AIMIUM_LOCAL_ENV"] = str(self.workspace / "missing.cmd")
        self.environment["AIMIUM_PYTHON"] = sys.executable
        result = self.run_probe()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("AIMIUM_LOCAL_ENV does not exist", result.stderr)
        self.assertFalse(self.result.exists())

    def test_inherited_python_without_environment_file(self):
        self.environment["AIMIUM_PYTHON"] = sys.executable
        result = self.run_probe()
        self.assertEqual(27, result.returncode, result.stdout + result.stderr)
        self.assertIsNone(json.loads(self.result.read_text())["env"])

    def test_explicit_depot_tools_is_prepended_to_path(self):
        self.environment["AIMIUM_PYTHON"] = sys.executable
        depot = self.workspace / "local depot tools"
        depot.mkdir()
        self.environment["AIMIUM_DEPOT_TOOLS"] = str(depot)
        result = self.run_probe()
        self.assertEqual(27, result.returncode, result.stdout + result.stderr)
        self.assertEqual(str(depot), json.loads(self.result.read_text())["path"].split(";")[0])


if __name__ == "__main__":
    unittest.main()
