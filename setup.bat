@echo off

:: Install the required libraries
echo Installing dependencies...
pip install pyinstaller pillow pycryptodome requests pywin32

:: Check if Python is installed
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b
)

:: Open setter.py in the same directory as the batch file
echo Running setter.py...
python setter.py

pause
