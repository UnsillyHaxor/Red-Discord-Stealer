@echo off


echo Installing dependencies...
pip install pyinstaller pillow pycryptodome requests pywin32


python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b
)


echo Running setter.py...
python setter.py

pause
