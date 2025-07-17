from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
from datetime import date
from db_connection import Connection
import time
import os
import requests
from message_b import MessageBox

class ExpirationNotifier(QThread):
    new_expired_info = pyqtSignal(list)  # لیستی از دیکشنری‌ها شامل اطلاعات محصولات
    expired_count_signal = pyqtSignal(int)
    empty_count= pyqtSignal(int)
    discount_expire= pyqtSignal(int)
    new_discount_expired = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True
        self.prev_count = -1

    def run(self):
        while self.running:
            self.db_config = Connection().get_connection()
            if not self.db_config:
                time.sleep(5)
                continue

            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            try:
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users;")
                res_id = cursor_sq.fetchone()
                if not res_id:
                    continue
                id_user = res_id[0]
            except Exception as e:
                print(f"{e}: خطا در خواندن دیتابیس لوکال")
                continue

            try:
                cursor = self.db_config.cursor()

                today = datetime.date.today().strftime("%Y/%m/%d")
                #print(today)

                cursor.execute("""
                    SELECT product_name, quantity, expiration_dates, product_image
                    FROM inventories
                    WHERE expiration_dates < %s AND user_id = %s
                """, (today, id_user))
                results = cursor.fetchall()

                products = []
                for row in results:
                    name, quantity, exp_date, image_path = row
                    products.append({
                        "product_name": name,
                        "quantity": quantity,
                        "expiration_dates": exp_date,
                        "product_image": image_path or ""
                    })

                count = len(products)
                if count != self.prev_count:
                    self.prev_count = count
                    self.expired_count_signal.emit(count)
                    self.new_expired_info.emit(products)
                ## empty items number
                cursor.execute('''
                    SELECT COUNT(quantity) as quanity from inventories WHERE quantity < 0  and user_id= %s
                    ''',(id_user,))
                empty_result= cursor.fetchone()
                if empty_result:
                    empty_number= empty_result[0] 
                self.empty_count.emit(empty_number)
                ##expired date discount
                cursor.execute('''
                    SELECT COUNT(discount_percent) FROM inventories 
                    WHERE user_id= %s AND expir_discount= 0
                ''',(id_user,))
                expire_disc_result= cursor.fetchone()
                if expire_disc_result:
                    expired_discount= expire_disc_result[0]
                self.discount_expire.emit(expired_discount)
                ##
                cursor.execute('''
                    SELECT product_name, quantity,discount_percent,product_image
                    FROM inventories
                    WHERE expir_discount=0 and user_id= %s
                ''',(id_user,))
                discount_result= cursor.fetchall()
                discount_list= []
                if discount_result:
                    for discount in discount_result:
                        (product_name, quantities,discount_percent,product_image) = discount
                        discount_list.append({
                            "name" :product_name,
                            "quantity" : quantities,
                            "discount_percent" :discount_percent,
                            "product_image" :product_image or ""
                        })
                self.new_discount_expired.emit(discount_list)
                self.db_config.close()
            except pymysql.Error as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")

            time.sleep(5)
