@echo off
rem Copyright 2026 The Aimium Authors
rem Use of this source code is governed by a BSD-style license.
if not defined AIMIUM_PYTHON (
  echo Aimium: selected Python interpreter is missing. 1>&2
  exit /b 1
)
"%AIMIUM_PYTHON%" %*
exit /b %errorlevel%
