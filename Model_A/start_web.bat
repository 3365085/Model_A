@echo off
setlocal
cd /d "%~dp0.."
echo Starting Module A web service with the shared Pixi GPU environment...
echo Workspace: %CD%
echo.
pixi run monitor-open-external
echo.
echo Service process exited. Press any key to close this window.
pause >nul
