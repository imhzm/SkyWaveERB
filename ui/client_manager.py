# الملف: ui/client_manager.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QMessageBox, QGroupBox, QCheckBox,
    QApplication, QDialog
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont
from services.client_service import ClientService
from core import schemas
from typing import List, Optional

from ui.client_editor_dialog import ClientEditorDialog
from ui.styles import BUTTON_STYLES, TABLE_STYLE
import os


class ClientDataLoader(QThread):
    """
    ⚡ Worker Thread لتحميل بيانات العملاء في الخلفية
    يمنع تجميد الواجهة أثناء التحميل
    """
    finished = pyqtSignal(list, dict, dict)  # clients_list, invoices_total, payments_total
    error = pyqtSignal(str)
    
    def __init__(self, client_service, show_archived=False):
        super().__init__()
        self.client_service = client_service
        self.show_archived = show_archived
    
    def run(self):
        """تشغيل عملية التحميل في الخلفية"""
        try:
            print("INFO: [ClientDataLoader] بدء تحميل البيانات...")
            
            # 1. جلب العملاء
            if self.show_archived:
                clients_list = self.client_service.get_archived_clients()
            else:
                clients_list = self.client_service.get_all_clients()
            
            print(f"INFO: [ClientDataLoader] تم جلب {len(clients_list)} عميل")
            
            # 2. جلب كل الفواتير والمدفوعات مرة واحدة
            all_invoices = self.client_service.repo.get_all_invoices()
            all_payments = self.client_service.repo.get_all_payments()
            
            print(f"INFO: [ClientDataLoader] تم جلب {len(all_invoices)} فاتورة و {len(all_payments)} دفعة")
            
            # 3. حساب الإجماليات
            client_invoices_total = {}
            client_payments_total = {}
            
            for inv in all_invoices:
                if inv.status != schemas.InvoiceStatus.VOID:
                    client_invoices_total[inv.client_id] = client_invoices_total.get(inv.client_id, 0) + inv.total_amount
            
            for payment in all_payments:
                client_payments_total[payment.client_id] = client_payments_total.get(payment.client_id, 0) + payment.amount
            
            print(f"INFO: [ClientDataLoader] تم حساب إجماليات {len(client_invoices_total)} عميل")
            
            # 4. إرسال النتيجة
            self.finished.emit(clients_list, client_invoices_total, client_payments_total)
            print("INFO: [ClientDataLoader] تم إرسال البيانات بنجاح")
            
        except Exception as e:
            print(f"ERROR: [ClientDataLoader] خطأ في التحميل: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class ClientManagerTab(QWidget):
    """
    (معدل) التاب الخاص بإدارة العملاء (مع عمود اللوجو)
    """

    def __init__(self, client_service: ClientService, parent=None):
        super().__init__(parent)

        self.client_service = client_service
        self.clients_list: List[schemas.Client] = []
        self.selected_client: Optional[schemas.Client] = None

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("➕ إضافة عميل جديد")
        self.add_button.setStyleSheet(BUTTON_STYLES["success"])
        self.add_button.clicked.connect(lambda: self.open_editor(client_to_edit=None))

        self.edit_button = QPushButton("✏️ تعديل العميل")
        self.edit_button.setStyleSheet(BUTTON_STYLES["warning"])
        self.edit_button.clicked.connect(self.open_editor_for_selected)

        # زر التصدير
        self.export_button = QPushButton("📊 تصدير Excel")
        self.export_button.setStyleSheet(BUTTON_STYLES["success"])
        self.export_button.clicked.connect(self.export_clients)

        # زر الاستيراد
        self.import_button = QPushButton("📥 استيراد Excel")
        self.import_button.setStyleSheet(BUTTON_STYLES["info"])
        self.import_button.clicked.connect(self.import_clients)

        # زرار التحديث
        self.refresh_button = QPushButton("🔄 تحديث")
        self.refresh_button.setStyleSheet(BUTTON_STYLES["secondary"])
        self.refresh_button.clicked.connect(self.load_clients_data)

        self.show_archived_checkbox = QCheckBox("إظهار العملاء المؤرشفين")
        self.show_archived_checkbox.clicked.connect(self.load_clients_data)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.import_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.show_archived_checkbox)

        main_layout.addLayout(buttons_layout)

        table_groupbox = QGroupBox("قايمة العملاء")
        table_layout = QVBoxLayout()
        table_groupbox.setLayout(table_layout)

        # استخدام الجدول العادي (مؤقتاً حتى يتم حل مشكلة LazyTableWidget)
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(8)
        self.clients_table.setHorizontalHeaderLabels(["اللوجو", "الاسم", "الشركة", "الهاتف", "الإيميل", "💰 إجمالي الفواتير", "✅ إجمالي المدفوعات", "الحالة"])
        
        # === UNIVERSAL SEARCH BAR ===
        from ui.universal_search import UniversalSearchBar
        self.search_bar = UniversalSearchBar(
            self.clients_table,
            placeholder="🔍 بحث (الاسم، الشركة، الهاتف، الإيميل)..."
        )
        table_layout.addWidget(self.search_bar)
        # === END SEARCH BAR ===
        
        self.clients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clients_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.clients_table.setAlternatingRowColors(True)
        self.clients_table.verticalHeader().setDefaultSectionSize(60)
        self.clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.clients_table.setColumnWidth(0, 70)
        self.clients_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.clients_table.setColumnWidth(5, 150)
        self.clients_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.clients_table.setColumnWidth(6, 150)
        self.clients_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        self.clients_table.itemSelectionChanged.connect(self.on_client_selection_changed)
        
        # إضافة دبل كليك للتعديل
        self.clients_table.itemDoubleClicked.connect(self.open_editor_for_selected)

        table_layout.addWidget(self.clients_table)
        main_layout.addWidget(table_groupbox, 1)

        self.load_clients_data()
        self.update_buttons_state(False)
    
    def export_clients(self):
        """تصدير العملاء إلى Excel"""
        try:
            # الحصول على خدمة التصدير من النافذة الرئيسية
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'export_service'):
                main_window = main_window.parent()
            
            export_service = getattr(main_window, 'export_service', None) if main_window else None
            
            if not export_service:
                QMessageBox.warning(self, "خدمة التصدير غير متوفرة", "يرجى تثبيت pandas: pip install pandas openpyxl")
                return
            
            # تصدير العملاء
            filepath = export_service.export_clients_to_excel(self.clients_list)
            
            if filepath:
                reply = QMessageBox.question(
                    self,
                    "تم التصدير",
                    f"تم تصدير {len(self.clients_list)} عميل بنجاح إلى:\n{filepath}\n\nهل تريد فتح الملف؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    export_service.open_file(filepath)
            else:
                QMessageBox.warning(self, "خطأ", "فشل في تصدير البيانات")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في التصدير:\n{str(e)}")
    
    def import_clients(self):
        """استيراد العملاء من ملف Excel"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            # الحصول على خدمة التصدير من النافذة الرئيسية
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'export_service'):
                main_window = main_window.parent()
            
            export_service = getattr(main_window, 'export_service', None) if main_window else None
            
            if not export_service:
                QMessageBox.warning(self, "خدمة الاستيراد غير متوفرة", "يرجى تثبيت pandas: pip install pandas openpyxl")
                return
            
            # اختيار ملف Excel
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "اختر ملف Excel للاستيراد",
                "",
                "Excel Files (*.xlsx *.xls)"
            )
            
            if not filepath:
                return
            
            # استيراد البيانات
            clients_data, errors = export_service.import_clients_from_excel(filepath)
            
            if errors:
                error_msg = "\n".join(errors[:10])  # عرض أول 10 أخطاء
                if len(errors) > 10:
                    error_msg += f"\n... و {len(errors) - 10} خطأ آخر"
                
                reply = QMessageBox.question(
                    self,
                    "تحذير",
                    f"تم العثور على {len(errors)} خطأ:\n\n{error_msg}\n\nهل تريد المتابعة باستيراد البيانات الصحيحة ({len(clients_data)} عميل)؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            if not clients_data:
                QMessageBox.warning(self, "لا توجد بيانات", "لم يتم العثور على بيانات صحيحة للاستيراد")
                return
            
            # استيراد العملاء
            success_count = 0
            failed_count = 0
            
            for client_dict in clients_data:
                try:
                    # إنشاء عميل جديد
                    client = schemas.Client(**client_dict)
                    self.client_service.create_client(client)
                    success_count += 1
                except Exception as e:
                    print(f"ERROR: فشل استيراد عميل {client_dict.get('name')}: {e}")
                    failed_count += 1
            
            # تحديث الجدول
            self.load_clients_data()
            
            # عرض النتيجة
            result_msg = f"✅ تم استيراد {success_count} عميل بنجاح"
            if failed_count > 0:
                result_msg += f"\n❌ فشل استيراد {failed_count} عميل"
            
            QMessageBox.information(self, "نتيجة الاستيراد", result_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في الاستيراد:\n{str(e)}")

    def update_buttons_state(self, has_selection: bool):
        self.edit_button.setEnabled(has_selection)

    def on_client_selection_changed(self):
        selected_rows = self.clients_table.selectedIndexes()
        if selected_rows:
            selected_index = selected_rows[0].row()
            if 0 <= selected_index < len(self.clients_list):
                self.selected_client = self.clients_list[selected_index]
                self.update_buttons_state(True)
                return
        self.selected_client = None
        self.update_buttons_state(False)

    def load_clients_data(self):
        """⚡ تحميل بيانات العملاء باستخدام Threading (لا تجميد)"""
        print("INFO: [ClientManager] جاري تحميل بيانات العملاء...")
        
        # تعطيل الأزرار أثناء التحميل
        self.add_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        
        # عرض رسالة تحميل
        self.clients_table.setRowCount(1)
        loading_item = QTableWidgetItem("⏳ جاري تحميل البيانات...")
        loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_item.setFont(QFont("Cairo", 12, QFont.Weight.Bold))
        loading_item.setForeground(QColor("#2454a5"))
        self.clients_table.setItem(0, 0, loading_item)
        self.clients_table.setSpan(0, 0, 1, 8)
        
        # بدء التحميل في الخلفية
        self.loader_thread = ClientDataLoader(
            self.client_service,
            self.show_archived_checkbox.isChecked()
        )
        self.loader_thread.finished.connect(self._on_data_loaded)
        self.loader_thread.error.connect(self._on_load_error)
        self.loader_thread.start()
    
    def _on_data_loaded(self, clients_list, client_invoices_total, client_payments_total):
        """معالجة البيانات بعد التحميل"""
        try:
            print(f"INFO: [ClientManager] استلام البيانات: {len(clients_list)} عميل")
            self.clients_list = clients_list
            self.clients_table.setRowCount(0)
            
            # إزالة الـ span
            self.clients_table.clearSpans()

            for index, client in enumerate(self.clients_list):
                self.clients_table.insertRow(index)

                # اللوجو
                logo_label = QLabel()
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if client.logo_path and os.path.exists(client.logo_path):
                    pixmap = QPixmap(client.logo_path)
                    scaled_pixmap = pixmap.scaled(
                        QSize(50, 50),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_label.setPixmap(scaled_pixmap)
                else:
                    logo_label.setText("🚫")
                    logo_label.setStyleSheet("font-size: 20px; color: #888;")
                self.clients_table.setCellWidget(index, 0, logo_label)

                # البيانات الأساسية
                self.clients_table.setItem(index, 1, QTableWidgetItem(client.name or ""))
                self.clients_table.setItem(index, 2, QTableWidgetItem(client.company_name or ""))
                self.clients_table.setItem(index, 3, QTableWidgetItem(client.phone or ""))
                self.clients_table.setItem(index, 4, QTableWidgetItem(client.email or ""))

                client_id = client._mongo_id if hasattr(client, '_mongo_id') and client._mongo_id else str(client.id)
                
                # إجمالي الفواتير
                total_invoices = client_invoices_total.get(client_id, 0)
                total_item = QTableWidgetItem(f"{total_invoices:,.0f} ج.م")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total_item.setForeground(QColor("#2454a5"))
                total_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
                self.clients_table.setItem(index, 5, total_item)

                # إجمالي المدفوعات
                total_payments = client_payments_total.get(client_id, 0)
                payment_item = QTableWidgetItem(f"{total_payments:,.0f} ج.م")
                payment_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                payment_item.setForeground(QColor("#00a876"))
                payment_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
                self.clients_table.setItem(index, 6, payment_item)

                # الحالة
                status_item = QTableWidgetItem(client.status.value)
                if client.status == schemas.ClientStatus.ARCHIVED:
                    status_item.setBackground(QColor("#ef4444"))
                    status_item.setForeground(QColor("white"))
                else:
                    status_item.setBackground(QColor("#10b981"))
                    status_item.setForeground(QColor("white"))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.clients_table.setItem(index, 7, status_item)

            print(f"✅ [ClientManager] تم تحميل {len(self.clients_list)} عميل بنجاح")
            self.selected_client = None
            self.update_buttons_state(False)
            
        except Exception as e:
            print(f"ERROR: [ClientManager] فشل معالجة البيانات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل معالجة البيانات:\n{str(e)}")
        
        finally:
            # إعادة تفعيل الأزرار
            self.add_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.import_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
    
    def _on_load_error(self, error_msg):
        """معالجة الأخطاء"""
        print(f"ERROR: [ClientManager] فشل تحميل العملاء: {error_msg}")
        QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات:\n{error_msg}")
        
        # إعادة تفعيل الأزرار
        self.add_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.import_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        
        # مسح رسالة التحميل
        self.clients_table.setRowCount(0)

    def open_editor(self, client_to_edit: Optional[schemas.Client]):
        dialog = ClientEditorDialog(
            client_service=self.client_service,
            client_to_edit=client_to_edit,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients_data()

    def open_editor_for_selected(self):
        if not self.selected_client:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد عميل من الجدول أولاً.")
            return
        self.open_editor(self.selected_client)
