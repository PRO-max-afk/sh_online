from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
from datetime import date
from db_connection import Connection
import time
import os
from message_b import MessageBox

class ExpirationNotifier(QThread):
    new_expired_info = pyqtSignal(list)  # لیستی از دیکشنری‌ها شامل اطلاعات محصولات
    expired_count_signal = pyqtSignal(int)
    empty_count= pyqtSignal(int)
    discount_expire= pyqtSignal(int)
    new_discount_expired = pyqtSignal(list)
    empty_list= pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True
        self.prev_count = -1

    def run(self):
        self.db_config = Connection().get_connection()
        if self.db_config:
            self.select_notifi_info()
        else:
            self.select_offline_notifi_info()

    def select_notifi_info(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
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
                MessageBox(text="هیچ کاربری یافت نشد!", title="❌ خطا", type="error").show()
                return
            id_user = res_id[0]
        except Exception as e:
            print(f"{e}: خطا در خواندن دیتابیس لوکال")
            return
        finally:
            conn_sq.close()

        while self.running:
            try:
                cursor = self.db_config.cursor()

                today = datetime.date.today().strftime("%Y/%m/%d")

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

                self.expired_count_signal.emit(len(products))
                self.new_expired_info.emit(products)

                # empty count
                cursor.execute('''
                    SELECT COUNT(quantity) FROM inventories WHERE quantity <= 20 AND user_id= %s
                ''', (id_user,))
                empty_result = cursor.fetchone()
                empty_number = empty_result[0] if empty_result else 0
                self.empty_count.emit(empty_number)

                # empty list
                cursor.execute('''
                    SELECT product_name, quantity,expiration_dates,product_image 
                    FROM inventories
                    WHERE quantity <= 20 AND user_id= %s
                ''', (id_user,))
                empty_info = cursor.fetchall()
                empty_lists = [{
                    "name": name_p,
                    "quantity": qua,
                    "exp_date": exp_d,
                    "product_image": image
                } for name_p, qua, exp_d, image in empty_info]
                self.empty_list.emit(empty_lists)

                # discount count
                cursor.execute('''
                    SELECT COUNT(discount_percent) FROM inventories 
                    WHERE user_id= %s AND expir_discount = 0
                ''', (id_user,))
                expire_disc_result = cursor.fetchone()
                expired_discount = expire_disc_result[0] if expire_disc_result else 0
                self.discount_expire.emit(expired_discount)

                # discount list
                cursor.execute('''
                    SELECT product_name, quantity, discount_percent, product_image
                    FROM inventories
                    WHERE expir_discount = 0 AND user_id = %s
                ''', (id_user,))
                discount_result = cursor.fetchall()
                discount_list = [{
                    "name": p_name,
                    "quantity": qty,
                    "discount_percent": disc,
                    "product_image": img or ""
                } for p_name, qty, disc, img in discount_result]
                self.new_discount_expired.emit(discount_list)

            except pymysql.Error as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")
            except Exception as e:
                print(f"خطای کلی: {e}")

            time.sleep(5)


    ## offline mode:
    def select_offline_notifi_info(self):
        while self.running:

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

                today = datetime.date.today().strftime("%Y/%m/%d")
                #print(today)

                cursor_sq.execute("""
                    SELECT name, quantity, expire_date, image_path
                    FROM products
                    WHERE expire_date < ? AND user_id = ?
                """, (today, id_user))
                results = cursor_sq.fetchall()

                products = []
                for row in results:
                    name, quantity, exp_date, image_path = row
                    products.append({
                        "product_name": name,
                        "quantity": round(quantity),
                        "expiration_dates": exp_date,
                        "product_image": image_path or ""
                    })

                count = len(products)
                # حذف شرط و ارسال همیشه
                self.expired_count_signal.emit(count)
                self.new_expired_info.emit(products)

                ## empty items number
                cursor_sq.execute('''
                    SELECT COUNT(quantity) as quanity from products WHERE quantity <= 20  and user_id= ?
                    ''',(id_user,))
                empty_result= cursor_sq.fetchone()
                if empty_result:
                    empty_number= empty_result[0] 
                self.empty_count.emit(empty_number)
                ##
                empty_lists=[]
                cursor_sq.execute('''
                SELECT name, quantity,expire_date,image_path from products
                    WHERE quantity <=20 and user_id= ?
                ''',(id_user,))
                empty_info= cursor_sq.fetchall()
                for info in empty_info:
                    name_p,qua,exp_d,image= info
                    empty_lists.append({
                        "name" : name_p,
                        "quantity" : qua,
                        "exp_date" : exp_d,
                        "product_image" : image
                    })
                
                self.empty_list.emit(empty_lists)
                ##expired date discount
                cursor_sq.execute('''
                    SELECT COUNT(discount_percent) FROM products 
                    WHERE user_id= ? AND expire_discount= 0
                ''',(id_user,))
                expire_disc_result= cursor_sq.fetchone()
                if expire_disc_result:
                    expired_discount= expire_disc_result[0]
                self.discount_expire.emit(expired_discount)
                ##
                cursor_sq.execute('''
                    SELECT name, quantity,discount_percent,image_path
                    FROM products
                    WHERE expire_discount=0 and user_id= ?
                ''',(id_user,))
                discount_result= cursor_sq.fetchall()
                discount_list= []
                if discount_result:
                    for discount in discount_result:
                        (product_name, quantities,discount_percent,product_image) = discount
                        discount_list.append({
                            "name" :product_name,
                            "quantity" : round(quantities),
                            "discount_percent" :discount_percent,
                            "product_image" :product_image or ""
                        })
                self.new_discount_expired.emit(discount_list)
            except sqlite3.Error as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")
            finally:
                if conn_sq:
                    conn_sq.close()
            time.sleep(2)