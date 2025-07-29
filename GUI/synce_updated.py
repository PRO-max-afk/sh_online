from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import requests
import sqlite3
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import jdatetime
from datetime import datetime
import datetime
from message_b import MessageBox
import os
from db_connection import Connection

class UpdateThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            self.synced_to_server()
    ##
    def synced_to_server(self):
        db_connect = Connection().get_connection()
        if not db_connect:
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
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

        try:
            
            cursor = db_connect.cursor()

            for product in unsynced_products:
                (name,barcode, buy_date, buy_price,
                sale_price, big_price, quantity, expire_date,new_price,discount_percent,expire_discount,big_sub,
                total,final_total, type_save,user_id,update_at) = product

                # بررسی وجود محصول
                cursor.execute("SELECT COUNT(*) FROM inventories WHERE barcode = %s AND user_id = %s", (barcode, user_id))
                exists = cursor.fetchone()[0]

                if exists:
                    # بروزرسانی
                    cursor.execute('''
                        UPDATE inventories SET
                            product_name=%s,
                            barcode= %s,
                            quantity = %s,
                            buy_price = %s,
                            buy_date = %s,
                            sell_price = %s,
                            big_price = %s,
                            expiration_dates = %s,
                            new_price= %s,
                            discount_percent = %s,
                            expir_discount = %s,
                            big_sub= %s,
                            total = %s,
                            final_total= %s,
                            type_save= %s,
                            updated_at = %s
                        WHERE barcode = %s AND user_id = %s
                    ''', (
                        name,barcode,quantity, buy_price, buy_date,
                        sale_price, big_price, expire_date,new_price,discount_percent,expire_discount,big_sub,
                        total,final_total,type_save,update_at ,barcode, user_id
                    ))
                    print(f"✅ محصول {barcode} بروزرسانی شد")
                else:
                    print(f"⚠️ محصول {barcode} در سرور پیدا نشد")

            db_connect.commit()


            # بروزرسانی SQLite
            cursor_sq.execute("UPDATE products SET is_synced = 1 WHERE is_synced = 0")
            conn_sq.commit()

        except Exception as e:
            print("❌ خطا در همگام‌سازی:", e)

        finally:
            conn_sq.close()
            if db_connect:
                db_connect.close()
    ##