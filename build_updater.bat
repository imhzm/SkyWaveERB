@echo off
echo ========================================
echo   Sky Wave ERP - Updater Builder
echo ========================================
echo.

echo [1/3] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)
echo.

echo [2/3] Building updater.exe...
pyinstaller --onefile --console --name updater --icon=icon.ico updater.py
echo.

echo [3/3] Copying updater.exe to main directory...
if exist dist\updater.exe (
    copy /Y dist\updater.exe .
    echo.
    echo ========================================
    echo   SUCCESS! updater.exe is ready!
    echo ========================================
    echo.
    echo The updater.exe file has been created in the main directory.
    echo You can now use the auto-update feature.
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR: Failed to build updater.exe
    echo ========================================
    echo.
)

echo Cleaning up build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist updater.spec del /q updater.spec

echo.
echo Done!
pause
