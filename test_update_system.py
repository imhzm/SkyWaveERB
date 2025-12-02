#!/usr/bin/env python3
# ملف اختبار نظام التحديث
# يمكن تشغيله للتأكد من أن جميع المكونات تعمل بشكل صحيح

import os
import sys
import json
from pathlib import Path


def test_version_file():
    """اختبار ملف version.py"""
    print("=" * 60)
    print("🔍 اختبار ملف version.py")
    print("=" * 60)
    
    try:
        from version import CURRENT_VERSION, APP_NAME, UPDATE_CHECK_URL
        
        print(f"✅ تم تحميل ملف version.py بنجاح")
        print(f"   📱 اسم التطبيق: {APP_NAME}")
        print(f"   🔢 الإصدار الحالي: {CURRENT_VERSION}")
        print(f"   🌐 رابط الفحص: {UPDATE_CHECK_URL}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحميل version.py: {e}")
        print()
        return False


def test_updater_file():
    """اختبار وجود ملف updater.py"""
    print("=" * 60)
    print("🔍 اختبار ملف updater.py")
    print("=" * 60)
    
    if os.path.exists("updater.py"):
        print("✅ ملف updater.py موجود")
        
        # التحقق من وجود updater.exe
        if os.path.exists("updater.exe"):
            print("✅ ملف updater.exe موجود")
            size = os.path.getsize("updater.exe") / 1024 / 1024
            print(f"   📦 حجم الملف: {size:.2f} MB")
        else:
            print("⚠️  ملف updater.exe غير موجود")
            print("   💡 قم بتشغيل build_updater.bat لإنشائه")
        
        print()
        return True
    else:
        print("❌ ملف updater.py غير موجود")
        print()
        return False


def test_update_service():
    """اختبار خدمة التحديث"""
    print("=" * 60)
    print("🔍 اختبار خدمة التحديث")
    print("=" * 60)
    
    try:
        from services.update_service import UpdateService, UpdateChecker, UpdateDownloader
        
        print("✅ تم تحميل update_service بنجاح")
        print("   📦 الفئات المتاحة:")
        print("      - UpdateService")
        print("      - UpdateChecker")
        print("      - UpdateDownloader")
        print()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحميل update_service: {e}")
        print()
        return False


def test_settings_tab():
    """اختبار تاب الإعدادات"""
    print("=" * 60)
    print("🔍 اختبار تاب الإعدادات")
    print("=" * 60)
    
    try:
        # قراءة ملف settings_tab.py
        with open("ui/settings_tab.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # التحقق من وجود الدوال المطلوبة
        required_methods = [
            "setup_update_tab",
            "check_for_updates",
            "download_update",
            "install_update"
        ]
        
        all_found = True
        for method in required_methods:
            if f"def {method}" in content:
                print(f"✅ الدالة {method} موجودة")
            else:
                print(f"❌ الدالة {method} غير موجودة")
                all_found = False
        
        print()
        return all_found
        
    except Exception as e:
        print(f"❌ خطأ في قراءة settings_tab.py: {e}")
        print()
        return False


def test_version_json_example():
    """اختبار ملف version.json.example"""
    print("=" * 60)
    print("🔍 اختبار ملف version.json.example")
    print("=" * 60)
    
    if os.path.exists("version.json.example"):
        try:
            with open("version.json.example", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print("✅ ملف version.json.example موجود وصالح")
            print(f"   🔢 الإصدار: {data.get('version', 'غير محدد')}")
            print(f"   🔗 الرابط: {data.get('url', 'غير محدد')}")
            print()
            return True
            
        except json.JSONDecodeError:
            print("❌ ملف version.json.example تالف")
            print()
            return False
    else:
        print("⚠️  ملف version.json.example غير موجود")
        print()
        return False


def test_documentation():
    """اختبار وجود ملفات التوثيق"""
    print("=" * 60)
    print("🔍 اختبار ملفات التوثيق")
    print("=" * 60)
    
    docs = {
        "BUILD_UPDATER.md": "دليل بناء النظام",
        "AUTO_UPDATE_GUIDE.md": "دليل المستخدم",
        "build_updater.bat": "سكريبت البناء"
    }
    
    all_found = True
    for file, desc in docs.items():
        if os.path.exists(file):
            print(f"✅ {file} موجود ({desc})")
        else:
            print(f"❌ {file} غير موجود ({desc})")
            all_found = False
    
    print()
    return all_found


def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "🔄 اختبار نظام التحديث التلقائي" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # تشغيل الاختبارات
    results.append(("ملف version.py", test_version_file()))
    results.append(("ملف updater.py", test_updater_file()))
    results.append(("خدمة التحديث", test_update_service()))
    results.append(("تاب الإعدادات", test_settings_tab()))
    results.append(("ملف version.json.example", test_version_json_example()))
    results.append(("ملفات التوثيق", test_documentation()))
    
    # عرض النتائج
    print("=" * 60)
    print("📊 ملخص النتائج")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {name}")
    
    print()
    print(f"النتيجة النهائية: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print()
        print("🎉 ممتاز! جميع الاختبارات نجحت!")
        print()
        print("الخطوات التالية:")
        print("1. قم بتشغيل build_updater.bat لإنشاء updater.exe")
        print("2. أنشئ ملف version.json على GitHub")
        print("3. حدث رابط UPDATE_CHECK_URL في version.py")
        print("4. جرب نظام التحديث من داخل البرنامج")
    else:
        print()
        print("⚠️  بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إلغاء الاختبار")
    except Exception as e:
        print(f"\n\n❌ خطأ فادح: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nاضغط Enter للخروج...")
