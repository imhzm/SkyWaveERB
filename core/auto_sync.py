# الملف: core/auto_sync.py
"""
نظام المزامنة التلقائية (Auto Sync)
يقوم بـ Pull & Push تلقائياً عند بدء البرنامج
"""

import threading
import time
from datetime import datetime
from typing import Optional
import json


class AutoSync:
    """
    ⚡ مدير المزامنة التلقائية - محسّن للسرعة
    - Pull: جلب البيانات من MongoDB إلى SQLite
    - Push: رفع البيانات من SQLite إلى MongoDB
    """
    
    def __init__(self, repository):
        """
        تهيئة المزامنة التلقائية
        
        Args:
            repository: كائن Repository للوصول للبيانات
        """
        self.repository = repository
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_stats = {
            'pulled': 0,
            'pushed': 0,
            'failed': 0
        }
        self._batch_size = 50  # ⚡ حجم الدفعة للمزامنة
    
    def start_auto_sync(self, delay_seconds: int = 3):
        """
        ⚡ بدء المزامنة التلقائية في الخلفية (محسّن)
        
        Args:
            delay_seconds: التأخير قبل بدء المزامنة (بالثواني)
        """
        def sync_worker():
            time.sleep(delay_seconds)
            print("INFO: [AutoSync] ⚡ بدء المزامنة السريعة...")
            self.perform_sync()
        
        # تشغيل في thread منفصل بأولوية منخفضة
        sync_thread = threading.Thread(
            target=sync_worker, 
            daemon=True, 
            name="AutoSyncThread"
        )
        sync_thread.start()
        print(f"INFO: [AutoSync] ⚡ جدولة المزامنة (بعد {delay_seconds} ثانية)")
    
    def perform_sync(self):
        """تنفيذ المزامنة الكاملة (Pull ثم Push)"""
        if self.is_syncing:
            print("WARNING: [AutoSync] المزامنة جارية بالفعل")
            return
        
        self.is_syncing = True
        start_time = time.time()
        
        try:
            # التحقق من الاتصال
            if not self.repository.online:
                print("WARNING: [AutoSync] لا يوجد اتصال بالإنترنت - تم إلغاء المزامنة")
                return
            
            print("=" * 80)
            print("🔄 المزامنة التلقائية")
            print("=" * 80)
            
            # Step 1: Pull (جلب من MongoDB)
            print("\n📥 Step 1: Pull - جلب البيانات من MongoDB...")
            pulled = self._pull_from_mongo()
            self.sync_stats['pulled'] = pulled
            
            # Step 2: Push (رفع إلى MongoDB)
            print("\n📤 Step 2: Push - رفع البيانات إلى MongoDB...")
            pushed = self._push_to_mongo()
            self.sync_stats['pushed'] = pushed
            
            # النتيجة
            elapsed = time.time() - start_time
            self.last_sync_time = datetime.now()
            
            print("\n" + "=" * 80)
            print("✅ اكتملت المزامنة التلقائية")
            print(f"  📥 تم جلب: {pulled} سجل")
            print(f"  📤 تم رفع: {pushed} سجل")
            print(f"  ⏱️ الوقت: {elapsed:.2f} ثانية")
            print("=" * 80)
            
        except Exception as e:
            print(f"ERROR: [AutoSync] فشلت المزامنة: {e}")
            self.sync_stats['failed'] += 1
            import traceback
            traceback.print_exc()
        
        finally:
            self.is_syncing = False
    
    def _pull_from_mongo(self) -> int:
        """
        جلب البيانات من MongoDB إلى SQLite
        
        Returns:
            عدد السجلات المجلوبة
        """
        total_pulled = 0
        
        try:
            # جلب الحسابات
            accounts = list(self.repository.mongo_db.accounts.find())
            for acc in accounts:
                try:
                    acc_dict = dict(acc)
                    mongo_id = str(acc_dict.pop('_id'))
                    
                    # تحويل datetime
                    for key in ['created_at', 'last_modified']:
                        if key in acc_dict and hasattr(acc_dict[key], 'isoformat'):
                            acc_dict[key] = acc_dict[key].isoformat()
                    
                    # تحديث أو إدراج
                    self.repository.sqlite_cursor.execute("""
                        INSERT OR REPLACE INTO accounts 
                        (_mongo_id, name, code, type, parent_id, balance, currency, 
                         description, created_at, last_modified, sync_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                    """, (
                        mongo_id,
                        acc_dict.get('name'),
                        acc_dict.get('code'),
                        acc_dict.get('type'),
                        acc_dict.get('parent_id'),
                        acc_dict.get('balance', 0.0),
                        acc_dict.get('currency', 'EGP'),
                        acc_dict.get('description'),
                        acc_dict.get('created_at'),
                        acc_dict.get('last_modified'),
                    ))
                    total_pulled += 1
                except Exception as e:
                    print(f"  ⚠️ فشل جلب حساب: {e}")
            
            self.repository.sqlite_conn.commit()
            print(f"  ✅ تم جلب {total_pulled} حساب")
            
            # جلب العملاء (مع إصلاح مشكلة cursor)
            try:
                clients_cursor = self.repository.mongo_db.clients.find()
                clients = list(clients_cursor)
                clients_cursor.close()  # إغلاق cursor لتجنب مشكلة recursive use
                
                clients_pulled = 0
                for client in clients:
                    try:
                        c = dict(client)
                        mongo_id = str(c.pop('_id'))
                        
                        # تحويل datetime
                        for key in ['created_at', 'last_modified']:
                            if key in c and hasattr(c[key], 'isoformat'):
                                c[key] = c[key].isoformat()
                        
                        self.repository.sqlite_cursor.execute("""
                            INSERT OR REPLACE INTO clients 
                            (_mongo_id, name, company_name, email, phone, address, country,
                             vat_number, status, client_type, work_field, logo_path,
                             client_notes, created_at, last_modified, sync_status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                        """, (
                            mongo_id,
                            c.get('name'),
                            c.get('company_name'),
                            c.get('email'),
                            c.get('phone'),
                            c.get('address'),
                            c.get('country'),
                            c.get('vat_number'),
                            c.get('status', 'نشط'),
                            c.get('client_type'),
                            c.get('work_field'),
                            c.get('logo_path'),
                            c.get('client_notes'),
                            c.get('created_at'),
                            c.get('last_modified'),
                        ))
                        clients_pulled += 1
                    except Exception as e:
                        print(f"  ⚠️ فشل جلب عميل: {e}")
                
                self.repository.sqlite_conn.commit()
                total_pulled += clients_pulled
                print(f"  ✅ تم جلب {clients_pulled} عميل")
                
            except Exception as e:
                print(f"  ❌ فشل جلب العملاء: {e}")
            
            # جلب المشاريع
            projects = list(self.repository.mongo_db.projects.find())
            projects_pulled = 0
            for proj in projects:
                try:
                    p = dict(proj)
                    mongo_id = str(p.pop('_id'))
                    
                    # تحويل datetime
                    for key in ['created_at', 'last_modified', 'start_date', 'end_date']:
                        if key in p and hasattr(p[key], 'isoformat'):
                            p[key] = p[key].isoformat()
                    
                    # تحويل items إلى JSON
                    items_json = json.dumps(p.get('items', []))
                    
                    self.repository.sqlite_cursor.execute("""
                        INSERT OR REPLACE INTO projects 
                        (_mongo_id, name, client_id, status, description, start_date, end_date,
                         items, subtotal, discount_rate, discount_amount, tax_rate, tax_amount,
                         total_amount, currency, project_notes, created_at, last_modified, sync_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                    """, (
                        mongo_id,
                        p.get('name'),
                        p.get('client_id'),
                        p.get('status', 'نشط'),
                        p.get('description'),
                        p.get('start_date'),
                        p.get('end_date'),
                        items_json,
                        p.get('subtotal', 0.0),
                        p.get('discount_rate', 0.0),
                        p.get('discount_amount', 0.0),
                        p.get('tax_rate', 0.0),
                        p.get('tax_amount', 0.0),
                        p.get('total_amount', 0.0),
                        p.get('currency', 'EGP'),
                        p.get('project_notes'),
                        p.get('created_at'),
                        p.get('last_modified'),
                    ))
                    projects_pulled += 1
                except Exception as e:
                    print(f"  ⚠️ فشل جلب مشروع: {e}")
            
            self.repository.sqlite_conn.commit()
            total_pulled += projects_pulled
            print(f"  ✅ تم جلب {projects_pulled} مشروع")
            
            # جلب الدفعات
            payments = list(self.repository.mongo_db.payments.find())
            payments_pulled = 0
            for pay in payments:
                try:
                    p = dict(pay)
                    mongo_id = str(p.pop('_id'))
                    
                    # تحويل datetime
                    for key in ['created_at', 'last_modified', 'date']:
                        if key in p and hasattr(p[key], 'isoformat'):
                            p[key] = p[key].isoformat()
                    
                    self.repository.sqlite_cursor.execute("""
                        INSERT OR REPLACE INTO payments 
                        (_mongo_id, project_id, client_id, date, amount, account_id, method,
                         created_at, last_modified, sync_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                    """, (
                        mongo_id,
                        p.get('project_id'),
                        p.get('client_id'),
                        p.get('date'),
                        p.get('amount', 0.0),
                        p.get('account_id'),
                        p.get('method'),
                        p.get('created_at'),
                        p.get('last_modified'),
                    ))
                    payments_pulled += 1
                except Exception as e:
                    print(f"  ⚠️ فشل جلب دفعة: {e}")
            
            self.repository.sqlite_conn.commit()
            total_pulled += payments_pulled
            print(f"  ✅ تم جلب {payments_pulled} دفعة")
            
            # جلب القيود المحاسبية (journal entries)
            try:
                journal_entries = list(self.repository.mongo_db.journal_entries.find())
                entries_pulled = 0
                for entry in journal_entries:
                    try:
                        e = dict(entry)
                        mongo_id = str(e.pop('_id'))
                        
                        # تحويل datetime
                        for key in ['created_at', 'last_modified', 'date']:
                            if key in e and hasattr(e[key], 'isoformat'):
                                e[key] = e[key].isoformat()
                        
                        # تحويل lines إلى JSON
                        lines_json = json.dumps(e.get('lines', []))
                        
                        self.repository.sqlite_cursor.execute("""
                            INSERT OR REPLACE INTO journal_entries 
                            (_mongo_id, date, description, lines, related_document_id,
                             created_at, last_modified, sync_status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'synced')
                        """, (
                            mongo_id,
                            e.get('date'),
                            e.get('description', ''),
                            lines_json,
                            e.get('related_document_id'),
                            e.get('created_at'),
                            e.get('last_modified'),
                        ))
                        entries_pulled += 1
                    except Exception as ex:
                        print(f"  ⚠️ فشل جلب قيد محاسبي: {ex}")
                
                self.repository.sqlite_conn.commit()
                total_pulled += entries_pulled
                print(f"  ✅ تم جلب {entries_pulled} قيد محاسبي")
            except Exception as e:
                print(f"  ❌ فشل جلب القيود المحاسبية: {e}")
            
            # جلب الفواتير
            try:
                invoices = list(self.repository.mongo_db.invoices.find())
                invoices_pulled = 0
                for inv in invoices:
                    try:
                        i = dict(inv)
                        mongo_id = str(i.pop('_id'))
                        
                        # تحويل datetime
                        for key in ['created_at', 'last_modified', 'issue_date', 'due_date']:
                            if key in i and hasattr(i[key], 'isoformat'):
                                i[key] = i[key].isoformat()
                        
                        # تحويل items إلى JSON
                        items_json = json.dumps(i.get('items', []))
                        
                        self.repository.sqlite_cursor.execute("""
                            INSERT OR REPLACE INTO invoices 
                            (_mongo_id, invoice_number, client_id, project_id, issue_date, due_date,
                             items, subtotal, discount_rate, discount_amount, tax_rate, tax_amount,
                             total_amount, currency, status, notes, created_at, last_modified, sync_status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                        """, (
                            mongo_id,
                            i.get('invoice_number'),
                            i.get('client_id'),
                            i.get('project_id'),
                            i.get('issue_date'),
                            i.get('due_date'),
                            items_json,
                            i.get('subtotal', 0.0),
                            i.get('discount_rate', 0.0),
                            i.get('discount_amount', 0.0),
                            i.get('tax_rate', 0.0),
                            i.get('tax_amount', 0.0),
                            i.get('total_amount', 0.0),
                            i.get('currency', 'EGP'),
                            i.get('status', 'مسودة'),
                            i.get('notes'),
                            i.get('created_at'),
                            i.get('last_modified'),
                        ))
                        invoices_pulled += 1
                    except Exception as e:
                        print(f"  ⚠️ فشل جلب فاتورة: {e}")
                
                self.repository.sqlite_conn.commit()
                total_pulled += invoices_pulled
                print(f"  ✅ تم جلب {invoices_pulled} فاتورة")
            except Exception as e:
                print(f"  ❌ فشل جلب الفواتير: {e}")
            
        except Exception as e:
            print(f"ERROR: [AutoSync] فشل Pull: {e}")
        
        return total_pulled
    
    def _push_to_mongo(self) -> int:
        """
        رفع البيانات من SQLite إلى MongoDB
        
        Returns:
            عدد السجلات المرفوعة
        """
        total_pushed = 0
        
        try:
            # رفع السجلات الجديدة أو المعدلة
            self.repository.sqlite_cursor.execute("""
                SELECT * FROM clients 
                WHERE sync_status IN ('new_offline', 'modified_offline')
            """)
            
            new_clients = self.repository.sqlite_cursor.fetchall()
            for row in new_clients:
                try:
                    client_dict = dict(row)
                    client_id = client_dict.pop('id')
                    mongo_id = client_dict.pop('_mongo_id', None)
                    client_dict.pop('sync_status', None)
                    
                    # تحويل datetime
                    for key in ['created_at', 'last_modified']:
                        if key in client_dict and isinstance(client_dict[key], str):
                            try:
                                client_dict[key] = datetime.fromisoformat(client_dict[key])
                            except (ValueError, TypeError, AttributeError):
                                pass
                    
                    if mongo_id:
                        # تحديث
                        from bson import ObjectId
                        self.repository.mongo_db.clients.update_one(
                            {'_id': ObjectId(mongo_id)},
                            {'$set': client_dict}
                        )
                    else:
                        # إدراج جديد
                        result = self.repository.mongo_db.clients.insert_one(client_dict)
                        mongo_id = str(result.inserted_id)
                        
                        # تحديث SQLite بالـ mongo_id
                        self.repository.sqlite_cursor.execute(
                            "UPDATE clients SET _mongo_id = ? WHERE id = ?",
                            (mongo_id, client_id)
                        )
                    
                    # تحديث sync_status
                    self.repository.sqlite_cursor.execute(
                        "UPDATE clients SET sync_status = 'synced' WHERE id = ?",
                        (client_id,)
                    )
                    
                    total_pushed += 1
                except Exception as e:
                    print(f"  ⚠️ فشل رفع عميل: {e}")
            
            self.repository.sqlite_conn.commit()
            if new_clients:
                print(f"  ✅ تم رفع {len(new_clients)} عميل")
            
        except Exception as e:
            print(f"ERROR: [AutoSync] فشل Push: {e}")
        
        return total_pushed
