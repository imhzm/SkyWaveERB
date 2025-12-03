# حل مشكلة: البرنامج .exe لا يفتح

## المشكلة
عند تشغيل `SkyWaveERP.exe` يظهر خطأ:
```
[PYI-38652:ERROR] Failed to start embedded python interpreter: Failed to import encodings module
```

## الأسباب المحتملة
1. ملفات Python الأساسية مفقودة
2. مشكلة في PyInstaller spec
3. مكتبات مفقودة أو غير متوافقة

## الحلول

### الحل 1: استخدام spec مبسط ✅ (موصى به)

```bash
# استخدم ملف spec المبسط
python -m PyInstaller SkyWaveERP_simple.spec --clean --noconfirm
```

أو استخدم السكربت الجاهز:
```bash
build_quick.bat
```

### الحل 2: إعادة بناء من الصفر

```bash
# 1. حذف المجلدات القديمة
rmdir /s /q build dist
del /q *.spec

# 2. بناء جديد
python -m PyInstaller main.py ^
    --name SkyWaveERP ^
    --icon icon.ico ^
    --noconsole ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "services;services" ^
    --add-data "ui;ui" ^
    --add-data "logo.png;." ^
    --add-data "icon.ico;." ^
    --add-data "version.json;." ^
    --hidden-import pymongo ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import jinja2 ^
    --hidden-import reportlab ^
    --hidden-import arabic_reshaper ^
    --hidden-import bidi.algorithm ^
    --hidden-import PIL._imaging ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import requests ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module tkinter
```

### الحل 3: تشغيل من Python مباشرة

إذا كان البناء يأخذ وقت طويل، يمكنك تشغيل البرنامج مباشرة:

```bash
python main.py
```

### الحل 4: التحقق من المكتبات

```bash
# تحديث المكتبات
pip install --upgrade pyinstaller
pip install --upgrade PyQt6
pip install --upgrade pymongo

# إعادة البناء
python -m PyInstaller SkyWaveERP_simple.spec --clean
```

## اختبار البرنامج

### 1. اختبار Python مباشرة
```bash
python main.py
```

### 2. اختبار EXE
```bash
cd dist\SkyWaveERP
.\SkyWaveERP.exe
```

### 3. التحقق من الملفات المطلوبة
```bash
dir dist\SkyWaveERP
```

يجب أن تجد:
- SkyWaveERP.exe
- _internal/ (مجلد المكتبات)
- assets/ (إذا كان موجود)
- logo.png
- icon.ico
- version.json

## ملاحظات مهمة

### ✅ نصائح للبناء الناجح:

1. **استخدم spec مبسط**: `SkyWaveERP_simple.spec` أسرع وأقل مشاكل

2. **استبعد المكتبات غير المستخدمة**:
   ```python
   excludes=[
       'matplotlib',  # إذا لم تستخدمها
       'scipy',
       'tkinter',
       'IPython',
       'notebook',
   ]
   ```

3. **console=False**: لإخفاء نافذة CMD السوداء
   ```python
   console=False  # للإصدار النهائي
   console=True   # للتطوير والتصحيح
   ```

4. **تحديد المكتبات المخفية**:
   ```python
   hiddenimports=[
       'pymongo',
       'bson',
       'PyQt6.QtCore',
       'PyQt6.QtGui',
       'PyQt6.QtWidgets',
       # ... إلخ
   ]
   ```

### ⚠️ مشاكل شائعة:

#### المشكلة: "DLL load failed"
**الحل**: تأكد من تثبيت Visual C++ Redistributable

#### المشكلة: "Module not found"
**الحل**: أضف المكتبة إلى `hiddenimports`

#### المشكلة: "البرنامج يفتح ويغلق فوراً"
**الحل**: 
1. استخدم `console=True` لرؤية الأخطاء
2. أو شغل من CMD: `.\SkyWaveERP.exe`

#### المشكلة: "الملفات مفقودة (assets, logo, etc.)"
**الحل**: تحقق من `datas` في spec file

## البناء السريع (موصى به)

للحصول على أفضل نتيجة:

```bash
# 1. تنظيف
rmdir /s /q build dist

# 2. بناء سريع
build_quick.bat

# 3. اختبار
cd dist\SkyWaveERP
.\SkyWaveERP.exe
```

## إذا استمرت المشكلة

### خيار 1: تشغيل من Python
```bash
# إنشاء shortcut
echo python main.py > run_skywave.bat
```

### خيار 2: استخدام PyInstaller بدون spec
```bash
pyinstaller --onedir --windowed --icon=icon.ico main.py
```

### خيار 3: استخدام أداة بناء أخرى
- **cx_Freeze**: بديل لـ PyInstaller
- **py2exe**: خاص بـ Windows
- **Nuitka**: يحول Python إلى C++

## الدعم

إذا واجهت مشاكل:
1. تحقق من logs في `build/SkyWaveERP/warn-SkyWaveERP.txt`
2. شغل مع `console=True` لرؤية الأخطاء
3. جرب `python main.py` للتأكد من عمل البرنامج

---

**تم إنشاء الحلول! 🔧**
