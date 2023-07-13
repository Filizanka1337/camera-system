@echo off

REM Checking Python version
python --version | findstr /C:"Python 3.9" >nul

IF %errorlevel% NEQ 0 (
    REM Python 3.9 is not installed, using winget to install
    winget install Python3 --exact --version 3.9.* -e
)

REM Reading the "requirements.txt" file
setlocal enabledelayedexpansion
for /f "delims=" %%i in (requirements.txt) do (
    REM Installing libraries using pip
    python -m pip install %%i
)

echo Installation completed.
