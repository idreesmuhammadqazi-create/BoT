@echo off
:: build.bat – compile main.py into a standalone .exe with PyInstaller
:: Usage: Double-click build.bat  OR  run it from Command Prompt

echo [build] Checking for PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [build] Installing PyInstaller...
    pip install pyinstaller
)

echo [build] Checking for python-dotenv...
python -c "import dotenv" 2>nul
if errorlevel 1 (
    echo [build] Installing python-dotenv...
    pip install python-dotenv
)

echo [build] Compiling main.py -^> dist\twitch-storage.exe ...
pyinstaller --onefile --name twitch-storage --hidden-import dotenv main.py

echo.
echo [build] Done!  Binary is at: dist\twitch-storage.exe
echo.
echo Usage examples:
echo   dist\twitch-storage.exe upload path\to\file.png
echo   dist\twitch-storage.exe upload path\to\file.png --chunk-size 300 --delay 2.0
echo   dist\twitch-storage.exe download ^<VOD_ID^> recovered.png
echo.
pause
