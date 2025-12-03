# نظام التحديث التلقائي الكامل - Sky Wave ERP

## 📦 الملفات المنشأة

### 1. ملفات النظام الأساسية
- **updater.exe** (7.97 MB) - برنامج التحديث التلقائي
- **updater.py** - الكود المصدري للمحدث
- **auto_updater.py** - نظام التحقق من التحديثات والتحميل
- **version.json** - ملف معلومات الإصدار
- **version.py** - رقم الإصدار في البرنامج

### 2. واجهات المستخدم
- **update_dialog.html** - واجهة HTML جميلة للتحديث
- **update_ui.py** - واجهة PyQt6 مع WebEngine
- **update_dialog_qt.py** - واجهة PyQt6 نقية (موصى بها)

### 3. أدوات البناء والاختبار
- **build_updater_system.bat** - سكربت بناء نظام التحديث
- **test_updater.py** - اختبار شامل للنظام
- **check_version.py** - التحقق من تطابق الإصدارات

## 🚀 الإصدار الحالي

**v1.0.1** - 2025-12-01

## 📋 كيفية الاستخدام

### 1. في البرنامج الرئيسي (main.py)

```python
from update_dialog_qt import show_update_dialog

# عند بدء البرنامج (اختياري)
def check_updates_on_startup():
    """التحقق من التحديثات عند بدء البرنامج"""
    from auto_updater import check_for_updates
    
    has_update, latest_version, download_url, changelog = check_for_updates()
    
    if has_update:
        print(f"✨ يوجد تحديث جديد: v{latest_version}")
        # يمكن عرض إشعار بسيط هنا
    else:
        print(f"✅ البرنامج محدث (v{get_current_version()})")

# عند الضغط على زر "التحقق من التحديثات"
def on_check_updates_clicked():
    """عرض نافذة التحديث"""
    show_update_dialog(auto_check=True)
```

### 2. إضافة زر في القائمة

```python
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction

def create_menu_bar(self):
    """إنشاء شريط القوائم"""
    menubar = self.menuBar()
    
    # قائمة المساعدة
    help_menu = menubar.addMenu("مساعدة")
    
    # زر التحقق من التحديثات
    update_action = QAction("التحقق من التحديثات", self)
    update_action.setShortcut("Ctrl+U")
    update_action.triggered.connect(self.check_for_updates)
    help_menu.addAction(update_action)
    
    # زر حول البرنامج
    about_action = QAction("حول البرنامج", self)
    about_action.triggered.connect(self.show_about)
    help_menu.addAction(about_action)

def check_for_updates(self):
    """التحقق من التحديثات"""
    from update_dialog_qt import show_update_dialog
    show_update_dialog(auto_check=True)
```

### 3. التحقق التلقائي عند بدء البرنامج

```python
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # التحقق من التحديثات بعد 3 ثواني من بدء البرنامج
        QTimer.singleShot(3000, self.auto_check_updates)
    
    def auto_check_updates(self):
        """التحقق التلقائي من التحديثات"""
        from auto_updater import check_for_updates
        
        has_update, latest_version, download_url, changelog = check_for_updates()
        
        if has_update:
            # عرض إشعار بسيط
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "تحديث متوفر",
                f"يوجد تحديث جديد (v{latest_version})\nهل تريد التحديث الآن؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                from update_dialog_qt import show_update_dialog
                show_update_dialog(auto_check=False)
```

## 🔧 البناء والنشر

### 1. بناء updater.exe

```bash
# طريقة 1: استخدام السكربت الجاهز
build_updater_system.bat

# طريقة 2: يدوياً
python -m PyInstaller --onefile --name updater --icon icon.ico updater.py
copy dist\updater.exe .
```

### 2. تحديث رقم الإصدار

قبل بناء البرنامج، قم بتحديث الإصدار في:

```python
# version.py
CURRENT_VERSION = "1.0.2"  # الإصدار الجديد

# version.json
{
    "version": "1.0.2",
    "release_date": "2025-12-04",
    "download_url": "https://github.com/imhzm/SkyWaveERB/releases/download/v1.0.2/SkyWaveERP-Setup.exe",
    "changelog": [
        "✨ ميزة جديدة 1",
        "🐛 إصلاح مشكلة 2",
        "⚡ تحسين الأداء"
    ]
}
```

### 3. رفع الإصدار على GitHub

```bash
# 1. Commit التغييرات
git add .
git commit -m "Release v1.0.2"

# 2. إنشاء Tag
git tag v1.0.2
git push origin v1.0.2

# 3. رفع version.json
git push origin main

# 4. إنشاء Release على GitHub
# - اذهب إلى: https://github.com/imhzm/SkyWaveERB/releases/new
# - اختر Tag: v1.0.2
# - أضف عنوان: Sky Wave ERP v1.0.2
# - أضف الوصف من changelog
# - ارفع ملف: SkyWaveERP-Setup.exe
# - انشر Release
```

### 4. التحقق من الرابط

تأكد من أن الرابط في version.json صحيح:

```
https://raw.githubusercontent.com/imhzm/SkyWaveERB/main/version.json
```

## 🧪 الاختبار

### 1. اختبار النظام الكامل

```bash
python test_updater.py
```

النتيجة المتوقعة:
```
✅ نجح: 3/3
❌ فشل: 0/3
🎉 جميع الاختبارات نجحت!
```

### 2. اختبار الواجهة

```bash
python update_dialog_qt.py
```

### 3. التحقق من الإصدارات

```bash
python check_version.py
```

النتيجة المتوقعة:
```
✅ version.json: v1.0.1
✅ version.py: v1.0.1
✅ auto_updater.py: v1.0.1
```

## 📱 واجهة المستخدم

### الميزات:
- ✨ تصميم حديث وجميل
- 🎨 ألوان Sky Blue & Dark Navy
- 📊 شريط تقدم التحميل
- 📋 عرض قائمة التغييرات
- ⚡ سريعة وسلسة
- 🌐 دعم كامل للعربية (RTL)

### الأزرار:
- **تحديث الآن** - تحميل وتطبيق التحديث
- **تذكيري لاحقاً** - تأجيل التحديث
- **إغلاق** - إغلاق النافذة (عند عدم وجود تحديث)

## 🔄 آلية عمل النظام

### 1. التحقق من التحديثات
```
البرنامج → auto_updater.py → GitHub (version.json) → مقارنة الإصدارات
```

### 2. تحميل التحديث
```
تحميل ZIP → حفظ في update_temp.zip → عرض التقدم
```

### 3. تطبيق التحديث
```
تشغيل updater.exe → إغلاق البرنامج → فك الضغط → استبدال الملفات → تشغيل البرنامج الجديد
```

## 📝 ملاحظات مهمة

### ✅ تم إنجازه:
- نظام تحديث تلقائي كامل
- واجهة مستخدم جميلة
- updater.exe جاهز للعمل
- اختبارات شاملة
- توثيق كامل

### ⚠️ قبل الاستخدام:
1. رفع version.json على GitHub
2. إنشاء Release على GitHub
3. رفع ملف SkyWaveERP-Setup.exe
4. التأكد من صحة الروابط

### 🔮 تحسينات مستقبلية:
- إضافة تحديثات تلقائية في الخلفية
- دعم التحديثات الجزئية (Delta Updates)
- إضافة نظام Rollback للعودة للإصدار السابق
- إضافة توقيع رقمي للتحديثات
- دعم قنوات تحديث متعددة (Stable, Beta, Dev)

## 🆘 استكشاف الأخطاء

### المشكلة: "404 Not Found"
**الحل:** تأكد من رفع version.json على GitHub في المسار الصحيح

### المشكلة: "updater.exe not found"
**الحل:** قم ببناء updater.exe باستخدام `build_updater_system.bat`

### المشكلة: "فشل التحميل"
**الحل:** تحقق من:
- اتصال الإنترنت
- صحة رابط التحميل في version.json
- وجود ملف SkyWaveERP-Setup.exe على GitHub Release

### المشكلة: "الإصدارات غير متطابقة"
**الحل:** استخدم `check_version.py` للتحقق وتحديث جميع الملفات

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- GitHub Issues: https://github.com/imhzm/SkyWaveERB/issues
- Email: support@skywave.com

---

**تم إنشاء النظام بنجاح! 🎉**

الإصدار الحالي: **v1.0.1**
التاريخ: **2025-12-03**
