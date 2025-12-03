@echo off
echo ========================================
echo بناء سريع لـ Sky Wave ERP
echo ========================================
echo.

echo جاري البناء...
python -m PyInstaller SkyWaveERP_simple.spec --clean --noconfirm

echo.
echo ========================================
echo تم البناء!
echo ========================================
echo.
echo الملف: dist\SkyWaveERP\SkyWaveERP.exe
echo.
pause
