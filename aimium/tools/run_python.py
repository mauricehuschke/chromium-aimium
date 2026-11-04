# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Pass the selected Windows interpreter to Python subprocess commands."""

import os
from pathlib import Path
import subprocess
import sys


def main():
    environment = os.environ.copy()
    environment["AIMIUM_PYTHON"] = sys.executable
    shims = Path(__file__).resolve().parent / "python-bin"
    environment["PATH"] = str(shims) + os.pathsep + environment.get("PATH", "")
    return subprocess.call([sys.executable, *sys.argv[1:]], env=environment)


if __name__ == "__main__":
    sys.exit(main())
