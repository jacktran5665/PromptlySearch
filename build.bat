@echo off
echo Building Promptly executable...
echo.

pip install pyinstaller

pyinstaller --onefile --noconsole --name "Promptly" --icon=NONE promptly.pyw

if exist "dist\Promptly.exe" (
    copy "dist\Promptly.exe" "Promptly.exe"
    echo.
    echo ✓ Build successful! 
    echo ✓ Promptly.exe created in current folder
    echo.
    echo You can now double-click Promptly.exe to run the app!
) else (
    echo ✗ Build failed!
)

pause