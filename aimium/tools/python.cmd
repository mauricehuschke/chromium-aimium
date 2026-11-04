@echo off
rem Copyright 2026 The Aimium Authors
rem Use of this source code is governed by a BSD-style license.
rem Local Windows Python launcher for manually invoked VS Code tasks.
setlocal
set "AIMIUM_DEFAULT_ENV=%~dp0..\..\..\env.cmd"
if defined AIMIUM_LOCAL_ENV (
  if not exist "%AIMIUM_LOCAL_ENV%" (
    echo Aimium: AIMIUM_LOCAL_ENV does not exist. 1>&2
    exit /b 1
  )
  call "%AIMIUM_LOCAL_ENV%"
  if errorlevel 1 exit /b 1
) else if exist "%AIMIUM_DEFAULT_ENV%" (
  call "%AIMIUM_DEFAULT_ENV%"
  if errorlevel 1 exit /b 1
)
if defined AIMIUM_DEPOT_TOOLS (
  set "PATH=%AIMIUM_DEPOT_TOOLS%;%PATH%"
)
if not defined AIMIUM_PYTHON set "AIMIUM_PYTHON=python"
"%AIMIUM_PYTHON%" "%~dp0run_python.py" %*
exit /b %errorlevel%
