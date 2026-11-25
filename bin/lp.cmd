@echo off
rem lp: the low-poly pipeline's command line (lib\lowpoly\cli.py). Finds a Python 3 and runs it isolated.
setlocal
set "LPCLI=%~dp0..\lib\lowpoly\cli.py"
where py >nul 2>nul
if not errorlevel 1 goto withpy
where python >nul 2>nul
if not errorlevel 1 goto withpython
echo lp: needs Python 3.8 or newer on the PATH 1>&2
exit /b 127
:withpy
py -3 -I "%LPCLI%" %*
exit /b %errorlevel%
:withpython
python -I "%LPCLI%" %*
exit /b %errorlevel%
