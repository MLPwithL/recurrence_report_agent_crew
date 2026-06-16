@echo off
REM setup_env.bat
REM Double click this file to run setup_env.ps1 with PowerShell.

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup_env.ps1"
pause
