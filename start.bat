@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Video Compressor v12

echo ============================================
echo   Video Compressor v12
echo   Browser will open http://127.0.0.1:8765
echo   Close this window to stop the tool.
echo   CLI batch mode:
echo     python video_compressor.py --cli --help
echo ============================================
echo.

if not exist "video_compressor.py" (
  echo [ERROR] video_compressor.py not found in:
  echo   %~dp0
  echo.
  pause
  exit /b 1
)

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo [ERROR] Python 3 not found.
  echo         Install Python 3 from https://www.python.org/downloads/
  echo         and make sure "Add Python to PATH" is checked.
  echo.
  pause
  exit /b 1
)

%PY% video_compressor.py
if errorlevel 1 (
  echo.
  echo [ERROR] Failed to start. Please check the message above.
)
echo.
pause
