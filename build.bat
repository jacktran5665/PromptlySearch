@echo off
echo Building SearchHotKey executable...
echo.

:: Install PyInstaller if not present
pip install pyinstaller

:: Build the executable
pyinstaller --onefile --noconsole --name "SearchHotKey" --icon=NONE search_hotkey.py

:: Copy the executable to main folder
if exist "dist\SearchHotKey.exe" (
    copy "dist\SearchHotKey.exe" "SearchHotKey.exe"
    echo.
    echo ✓ Build successful! 
    echo ✓ SearchHotKey.exe created in current folder
    echo.
    echo You can now double-click SearchHotKey.exe to run the app!
) else (
    echo ✗ Build failed!
)

pause