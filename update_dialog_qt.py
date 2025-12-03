#!/usr/bin/env python3
"""
واجهة تحديث جميلة باستخدام PyQt6 (بدون WebEngine)
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from auto_updater import (
    check_for_updates,
    download_update,
    apply_update,
    get_current_version
)


class DownloadThread(QThread):
    """
    Thread لتحميل التحديث في الخلفية
    """
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url
        self.zip_path = "update_temp.zip"
    
    def run(self):
        """تحميل التحديث"""
        try:
            self.progress.emit(10, "جاري الاتصال بالسيرفر...")
            
            # تحميل الملف
            success = download_update(self.download_url, self.zip_path)
            
            if success:
                self.progress.emit(100, "اكتمل التحميل!")
                self.finished.emit(True, self.zip_path)
            else:
                self.finished.emit(False, "فشل التحميل")
                
        except Exception as e:
            self.finished.emit(False, str(e))


class UpdateDialog(QDialog):
    """
    نافذة التحديث الجميلة
    """
    
    def __init__(self, update_data=None):
        super().__init__()
        self.update_data = update_data or {}
        self.download_thread = None
        self.zip_path = None
        self.init_ui()
    
    def init_ui(self):
        """تهيئة الواجهة"""
        self.setWindowTitle("Sky Wave ERP - تحديث")
        self.setFixedSize(600, 500)
        self.setStyleSheet(self.get_stylesheet())
        
        # Layout رئيسي
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Body
        body = self.create_body()
        main_layout.addWidget(body)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """إنشاء Header"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(150)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # أيقونة
        icon_label = QLabel("🚀")
        icon_label.setObjectName("icon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # العنوان
        if self.update_data.get('hasUpdate', False):
            title = QLabel("تحديث جديد متوفر")
        else:
            title = QLabel("البرنامج محدث")
        
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # الإصدارات
        version_layout = QHBoxLayout()
        version_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        current_version = QLabel(f"الحالي: {self.update_data.get('currentVersion', '1.0.1')}")
        current_version.setObjectName("version-badge")
        version_layout.addWidget(current_version)
        
        if self.update_data.get('hasUpdate', False):
            arrow = QLabel("➜")
            arrow.setObjectName("arrow")
            version_layout.addWidget(arrow)
            
            new_version = QLabel(f"الجديد: {self.update_data.get('latestVersion', '1.0.3')} ✨")
            new_version.setObjectName("new-version")
            version_layout.addWidget(new_version)
        
        layout.addLayout(version_layout)
        header.setLayout(layout)
        
        return header
    
    def create_body(self):
        """إنشاء Body"""
        body = QWidget()
        body.setObjectName("body")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        
        if self.update_data.get('hasUpdate', False):
            # عنوان التغييرات
            changelog_title = QLabel("🎉 ما الجديد في هذا الإصدار؟")
            changelog_title.setObjectName("changelog-title")
            layout.addWidget(changelog_title)
            
            # قائمة التغييرات
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setObjectName("scroll-area")
            scroll.setMaximumHeight(150)
            
            changelog_widget = QWidget()
            changelog_layout = QVBoxLayout()
            changelog_layout.setSpacing(5)
            
            for item in self.update_data.get('changelog', []):
                item_label = QLabel(f"✓ {item}")
                item_label.setObjectName("changelog-item")
                item_label.setWordWrap(True)
                changelog_layout.addWidget(item_label)
            
            changelog_widget.setLayout(changelog_layout)
            scroll.setWidget(changelog_widget)
            layout.addWidget(scroll)
            
            # شريط التقدم
            self.progress_widget = QWidget()
            self.progress_widget.setVisible(False)
            progress_layout = QVBoxLayout()
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setObjectName("progress-bar")
            self.progress_bar.setTextVisible(True)
            progress_layout.addWidget(self.progress_bar)
            
            self.status_label = QLabel("جاري التحميل...")
            self.status_label.setObjectName("status-text")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.status_label)
            
            self.progress_widget.setLayout(progress_layout)
            layout.addWidget(self.progress_widget)
        else:
            # رسالة "البرنامج محدث"
            no_update = QLabel("أنت تستخدم أحدث إصدار من Sky Wave ERP")
            no_update.setObjectName("no-update")
            no_update.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_update)
        
        body.setLayout(layout)
        return body
    
    def create_footer(self):
        """إنشاء Footer"""
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        
        if self.update_data.get('hasUpdate', False):
            # زر "تذكيري لاحقاً"
            self.later_btn = QPushButton("تذكيري لاحقاً")
            self.later_btn.setObjectName("btn-secondary")
            self.later_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.later_btn.clicked.connect(self.remind_later)
            layout.addWidget(self.later_btn)
            
            layout.addStretch()
            
            # زر "تحديث الآن"
            self.update_btn = QPushButton("تحديث الآن (Update)")
            self.update_btn.setObjectName("btn-primary")
            self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.update_btn.clicked.connect(self.start_update)
            layout.addWidget(self.update_btn)
        else:
            layout.addStretch()
            
            # زر "إغلاق"
            close_btn = QPushButton("إغلاق")
            close_btn.setObjectName("btn-secondary")
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(self.close)
            layout.addWidget(close_btn)
            
            layout.addStretch()
        
        footer.setLayout(layout)
        return footer
    
    def start_update(self):
        """بدء التحديث"""
        # إظهار شريط التقدم
        self.progress_widget.setVisible(True)
        self.update_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        
        # بدء التحميل
        download_url = self.update_data.get('downloadUrl', '')
        self.download_thread = DownloadThread(download_url)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, value, status):
        """تحديث شريط التقدم"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def download_finished(self, success, message):
        """انتهى التحميل"""
        if success:
            self.zip_path = message
            self.status_label.setText("اكتمل التحميل! جاري تطبيق التحديث...")
            
            # تطبيق التحديث بعد ثانية
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, self.apply_update_now)
        else:
            self.status_label.setText(f"❌ فشل التحميل: {message}")
            self.update_btn.setEnabled(True)
            self.later_btn.setEnabled(True)
    
    def apply_update_now(self):
        """تطبيق التحديث"""
        if self.zip_path:
            apply_update(self.zip_path)
    
    def remind_later(self):
        """تذكير لاحقاً"""
        print("⏭️ تم تأجيل التحديث")
        self.close()
    
    def get_stylesheet(self):
        """الأنماط CSS"""
        return """
            QDialog {
                background-color: #0f172a;
            }
            
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e3a8a, stop:1 #0f172a);
                border-bottom: 1px solid #334155;
            }
            
            #icon {
                font-size: 36px;
                color: #0ea5e9;
            }
            
            #title {
                font-size: 24px;
                font-weight: bold;
                color: #f1f5f9;
                margin: 10px 0;
            }
            
            #version-badge {
                background-color: rgba(255, 255, 255, 0.05);
                color: #94a3b8;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 14px;
            }
            
            #new-version {
                background-color: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #arrow {
                color: #94a3b8;
                font-size: 16px;
            }
            
            #body {
                background-color: #1e293b;
            }
            
            #changelog-title {
                font-size: 18px;
                color: #0ea5e9;
                margin-bottom: 10px;
            }
            
            #scroll-area {
                background-color: transparent;
                border: none;
            }
            
            #changelog-item {
                color: #cbd5e1;
                font-size: 14px;
                padding: 5px 0;
                border-bottom: 1px solid #334155;
            }
            
            #no-update {
                color: #94a3b8;
                font-size: 16px;
                padding: 40px;
            }
            
            #progress-bar {
                height: 8px;
                border-radius: 4px;
                background-color: #334155;
                border: none;
            }
            
            #progress-bar::chunk {
                background-color: #10b981;
                border-radius: 4px;
            }
            
            #status-text {
                color: #94a3b8;
                font-size: 13px;
                margin-top: 5px;
            }
            
            #footer {
                background-color: rgba(0, 0, 0, 0.2);
            }
            
            #btn-primary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #btn-primary:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #1d4ed8);
            }
            
            #btn-secondary {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #btn-secondary:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
        """


def show_update_dialog(auto_check=True):
    """
    عرض نافذة التحديث
    
    Args:
        auto_check: التحقق التلقائي من التحديثات
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # التحقق من التحديثات
    if auto_check:
        has_update, latest_version, download_url, changelog = check_for_updates()
    else:
        # بيانات تجريبية للاختبار
        has_update = True
        latest_version = "1.0.3"
        download_url = "https://github.com/imhzm/SkyWaveERB/releases/download/v1.0.3/SkyWaveERP-Setup.exe"
        changelog = [
            "⚡ إضافة المزامنة التلقائية (Auto Sync)",
            "✅ إضافة الترتيب بالضغط على رأس الجدول",
            "⚡ تحسين الأداء بنسبة 90%+",
            "🖨️ تسريع الطباعة (فورية)",
            "📄 إصلاح قالب الفاتورة ليكون صفحة واحدة A4",
            "💰 إصلاح عرض إجمالي الفواتير والمدفوعات"
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


def main():
    """الدالة الرئيسية للاختبار"""
    print("=" * 60)
    print("🎨 واجهة التحديث - Sky Wave ERP")
    print("=" * 60)
    
    show_update_dialog(auto_check=False)


if __name__ == "__main__":
    main()
