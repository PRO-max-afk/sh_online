from PyQt6.QtCore import QThread
import sqlite3
import os
from PyQt6.QtCore import QThread
import sqlite3
from datetime import datetime
import datetime
from message_b import MessageBox
import os
from db_connection import Connection

class UpdateThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect = Connection().get_connection()
        if self.db_connect:
            self.delete_from_server()  # 🗑 بررسی و حذف محصولات که در آفلاین حذف شده‌اند
            self.synced_to_server()    # 🔄 همگام‌سازی باقی محصولات
            self.delete_from_server_sale()

    def delete_from_server(self):
        db_connect = Connection().get_connection()
        if not db_connect:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        # اتصال به SQLite
        conn_sq = sqlite3.connect(db_path)
        cursor_sq = conn_sq.cursor()

        # گرفتن همه بارکدهای آفلاین
        cursor_sq.execute("SELECT barcode FROM products")
        offline_barcodes = {row[0] for row in cursor_sq.fetchall()}

        try:
            cursor = db_connect.cursor()

            # گرفتن همه بارکدهای آنلاین
            cursor.execute("SELECT barcode, user_id FROM inventories")
            online_products = cursor.fetchall()

            for barcode, user_id in online_products:
                if barcode not in offline_barcodes:
                    cursor.execute("DELETE FROM inventories WHERE barcode = %s AND user_id = %s", (barcode, user_id))
                    print(f"🗑 محصول {barcode} از سرور حذف شد")

            db_connect.commit()

        except Exception as e:
            print("❌ خطا در حذف محصول از سرور:", e)

        finally:
            conn_sq.close()
            if db_connect:
                db_connect.close()
    
    def delete_from_server_sale(self):
        db_connect = Connection().get_connection()
        if not db_connect:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        # اتصال به SQLite
        conn_sq = sqlite3.connect(db_path)
        cursor_sq = conn_sq.cursor()
        cursor_sq.execute("SELECT factor_number, user_id, barcode FROM sale_factor")
        offline_data = set(cursor_sq.fetchall())  # تبدیل به set برای مقایسه سریع‌تر

        try:
            cursor = db_connect.cursor()
            cursor.execute("SELECT factor_number, user_id, barcode FROM sale_factor")
            online_sale = cursor.fetchall()

            for factor_number, user_id, barcode in online_sale:
                if (factor_number, user_id, barcode) not in offline_data:
                    cursor.execute("""
                        DELETE FROM sale_factor
                        WHERE factor_number=%s AND user_id=%s AND barcode=%s
                    """, (factor_number, user_id, barcode))
                    print(f"🗑 رکورد {barcode} (factor: {factor_number}, user: {user_id}) از سرور حذف شد")

            db_connect.commit()

        except Exception as e:
            print("❌ خطا در حذف محصول از سرور:", e)

        finally:
            conn_sq.close()
            if db_connect:
                db_connect.close()



    def synced_to_server(self):
        update_time= datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
        db_connect = Connection().get_connection()
        if not db_connect:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        conn_sq = sqlite3.connect(db_path)
        cursor_sq = conn_sq.cursor()

        cursor_sq.execute('''SELECT name,barcode,
                            buy_date, buy_price, sale_price, big_price,
                            quantity, expire_date,new_price,discount_percent,expire_discount,big_sub, total,final_total,type_save,user_id,update_at
                            FROM products WHERE is_synced = 0''')

        unsynced_products = cursor_sq.fetchall()
        cursor_sq.execute('''
            SELECT weight,brand,production_date,production_place,product_state,
                        more_details,keep_place from product_details
            ''')
        un_sypro= cursor_sq.fetchall()

        try:
            cursor = db_connect.cursor()

            for product in unsynced_products:
                (name, barcode, buy_date, buy_price,
                sale_price, big_price, quantity, expire_date, new_price, discount_percent, expire_discount, big_sub,
                total, final_total, type_save, user_id, update_at) = product

                cursor.execute("SELECT COUNT(*) FROM inventories WHERE barcode = %s AND user_id = %s", (barcode, user_id))
                exists = cursor.fetchone()[0]

                if exists:
                    cursor.execute('''
                        UPDATE inventories SET
                            product_name=%s,
                            barcode=%s,
                            quantity=%s,
                            buy_price=%s,
                            buy_date=%s,
                            sell_price=%s,
                            big_price=%s,
                            expiration_dates=%s,
                            new_price=%s,
                            discount_percent=%s,
                            expir_discount=%s,
                            big_sub=%s,
                            total=%s,
                            final_total=%s,
                            type_save=%s,
                            updated_at=%s,
                            denied=0
                        WHERE barcode=%s AND user_id=%s
                    ''', (
                        name, barcode, quantity, buy_price, buy_date,
                        sale_price, big_price, expire_date, new_price, discount_percent, expire_discount, big_sub,
                        total, final_total, type_save, update_at, barcode, user_id
                    ))
                    
                    ##
                    cursor.execute('''
                        SELECT invent_id from inventories where barcode=%s and user_id=%s
                        ''',(barcode,user_id))
                    invent_id= cursor.fetchone()[0]
                    for details in un_sypro:
                        (weight,brand,product_date,production_place,product_state,
                        more_details,keep_place) = details
                        cursor.execute('''
                            UPDATE product_details SET
                                weight=%s,
                                brand= %s,
                                production_date=%s,
                                production_place=%s,
                                product_state=%s,
                                more_detail=%s,
                                keep_place= %s,
                                updated_at= %s
                                WHERE invent_id=%s
                        ''',(weight,brand,product_date,production_place,product_state,
                        more_details,keep_place,update_time,invent_id))

                    print(f"✅ محصول {barcode} بروزرسانی شد")
                    cursor_sq.execute("UPDATE products SET is_synced = 1 WHERE is_synced = 0")
                    cursor_sq.execute("UPDATE product_details SET is_synced=1 WHERE is_synced=0")
                    conn_sq.commit()
                else:
                    print(f"⚠️ محصول {barcode} در سرور پیدا نشد")
                

            db_connect.commit()
            

        except Exception as e:
            print("❌ خطا در همگام‌سازی:", e)

        finally:
            conn_sq.close()
            if db_connect:
                db_connect.close()
