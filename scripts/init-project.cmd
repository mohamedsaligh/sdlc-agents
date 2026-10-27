@echo off
REM Windows wrapper: double-click or run from cmd.exe. Forwards all arguments to init-project.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0init-project.ps1" %*
