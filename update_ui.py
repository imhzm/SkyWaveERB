#!/usr/bin/env python3
"""
واجهة المستخدم لنظام التحديث التلقائي
يستخدم PyQt6 لعرض نافذة تحديث جميلة
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSlot, QObject
from PyQt6.QtWebChannel import QWebChannel
import json

from auto_updater import (
    check_for_updates,
    download_update,
    apply_update,
    get_current_version
)


class UpdateAPI(QObject):
    """
    API للتواصل بين JavaScript و Python
    """
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        self.zip_path = "update_temp.zip"
    
    @pyqtSlot()
    def apply_update(self):
        """تطبيق التحديث"""
        print("🔄 بدء تطبيق التحديث...")
        apply_update(self.zip_path)
    
    @pyqtSlot()
    def remind_later(self):
        """تذكير لاحقاً"""
        print("⏭️ تم تأجيل التحديث")
        self.dialog.close()


class UpdateDialog(QDialog):
    """
    نافذة التحديث
    """
    
    def __init__(self, update_data=None):
        super().__init__()
        self.update_data = update_data or {}
        self.init_ui()
    
    def init_ui(self):
        """تهيئة الواجهة"""
        self.setWindowTitle("Sky Wave ERP - تحديث")
        self.setFixedSize(650, 550)
        
        # إنشاء WebView
        self.web_view = QWebEngineView(self)
        self.web_view.setGeometry(0, 0, 650, 550)
        
        # إعداد Web Channel للتواصل مع JavaScript
        self.channel = QWebChannel()
        self.api = UpdateAPI(self)
        self.channel.registerObject('pyapi', self.api)
        self.web_view.page().setWebChannel(self.channel)
        
        # تحميل HTML
        html_path = os.path.join(os.path.dirname(__file__), 'update_dialog.html')
        
        if os.path.exists(html_path):
            # قراءة HTML وحقن البيانات
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # حقن بيانات التحديث
            update_data_json = json.dumps(self.update_data, ensure_ascii=False)
            html_content = html_content.replace(
                'const updateData = {',
                f'const updateData = {update_data_json}; const _oldData = {{'
            )
            
            self.web_view.setHtml(html_content, QUrl.fromLocalFile(html_path))
        else:
            # HTML بديل بسيط
            self.web_view.setHtml(self.get_fallback_html())
    
    def get_fallback_html(self):
        """HTML بديل في حالة عدم وجود الملف"""
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #0f172a;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    background: #1e293b;
                    padding: 40px;
                    border-radius: 10px;
                }}
                button {{
                    padding: 10px 20px;
                    margin: 10px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                .primary {{ background: #0ea5e9; color: white; }}
                .secondary {{ background: #475569; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 تحديث جديد متوفر</h2>
                <p>الإصدار الحالي: {self.update_data.get('currentVersion', '1.0.1')}</p>
                <p>الإصدار الجديد: {self.update_data.get('latestVersion', '1.0.3')}</p>
                <button class="primary" onclick="window.location.href='update'">تحديث الآن</button>
                <button class="secondary" onclick="window.close()">لاحقاً</button>
            </div>
        </body>
        </html>
        """


def show_update_dialog(auto_check=True):
    """
    عرض نافذة التحديث
    
    Args:
        auto_check: التحقق التلقائي من التحديثات
        
    Returns:
        bool: True إذا تم العثور على تحديث
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # التحقق من التحديثات
    if auto_check:
        has_update, latest_version, download_url, changelog = check_for_updates()
    else:
        # بيانات تجريبية
        has_update = True
        latest_version = "1.0.3"
        download_url = "https://github.com/imhzm/SkyWaveERB/releases/download/v1.0.3/SkyWaveERP-Setup.exe"
        changelog = [
            "⚡ إضافة المزامنة التلقائية (Auto Sync)",
            "✅ إضافة الترتيب بالضغط على رأس الجدول",
            "⚡ تحسين الأداء بنسبة 90%+",
            "🖨️ تسريع الطباعة (فورية)",
            "📄 إصلاح قالب الفاتورة ليكون صفحة واحدة A4"
        ]
    
    # إعداد بيانات التحديث
    update_data = {
        "hasUpdate": has_update,
        "currentVersion": get_current_version(),
        "latestVersion": latest_version,
        "changelog": changelog,
        "downloadUrl": download_url
    }
    
    # عرض النافذة
    dialog = UpdateDialog(update_data)
    dialog.exec()
    
    return has_update


def main():
    """الدالة الرئيسية للاختبار"""
    print("=" * 60)
    print("🎨 واجهة التحديث - Sky Wave ERP")
    print("=" * 60)
    
    show_update_dialog(auto_check=False)


if __name__ == "__main__":
    main()
