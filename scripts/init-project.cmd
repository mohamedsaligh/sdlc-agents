@echo off
REM Windows wrapper for the one-time initialisation. Forwards all arguments to scripts\init-project.py.
REM   scripts\init-project.cmd                      (interactive)
REM   scripts\init-project.cmd --set PLATFORM_NAME=PayCore --set DEVCTL=pctl --set AI_PLATFORM=Atlas --set CODE_ROOT=D:\work\paycore --set DESIGN_DOCS_ROOT=D:\work\design-docs
REM   scripts\init-project.cmd --verify
where python >nul 2>nul || (echo Python 3.8+ is required ^(python not found on PATH^). & exit /b 1)
python "%~dp0init-project.py" %*
