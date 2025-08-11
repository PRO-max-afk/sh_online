from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
import datetime
from db_connection import Connection
import time
import os
from message_b import MessageBox

class ExpirationNotifier(QThread):
    new_expired_info = pyqtSignal(list)
    expired_count_signal = pyqtSignal(int)
    empty_count = pyqtSignal(int)
    discount_expire = pyqtSignal(int)
    new_discount_expired = pyqtSignal(list)
    empty_list = pyqtSignal(list)
    changing_list= pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True
        self.db_config = None

        # حافظه برای مقایسه مقادیر قبلی
        self.prev_expired_products = None
        self.prev_discount_list = None
        self.prev_empty_list = None
        self.prev_empty_count = None
        self.prev_discount_count = None
        self.prev_expired_count = None
        self.prev_changed_items= None

    def run(self):
        self.db_config = Connection().get_connection()
        if self.db_config:
            # اجرای فوری برای بار اول
            self.select_notifi_info()
            while self.running:
                time.sleep(2)
                self.select_notifi_info()
        else:
            self.select_offline_notifi_info()


    def has_changed(self, prev_data, new_data):
        if prev_data is None:
            return True  # اولین بار یا هیچ داده‌ای قبلاً ذخیره نشده
        return prev_data != new_data

    def select_notifi_info(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        if not self.db_config:
            print("⚠ self.db_config is None")
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

                # محصولات منقضی‌شده
                cursor.execute("""
                    SELECT product_name, quantity, expiration_dates, product_image
                    FROM inventories
                    WHERE expiration_dates < %s AND user_id = %s
                """, (today, id_user))
                results = cursor.fetchall()

                products = [{
                    "product_name": name,
                    "quantity": quantity,
                    "expiration_dates": exp_date,
                    "product_image": image_path or ""
                } for name, quantity, exp_date, image_path in results]

                if self.prev_expired_count != len(products) or self.prev_expired_count is None:
                    self.expired_count_signal.emit(len(products))
                    self.prev_expired_count = len(products)

                if self.has_changed(self.prev_expired_products, products):
                    self.new_expired_info.emit(products)
                    self.prev_expired_products = products

                # محصولات تمام‌شده
                cursor.execute('''
                    SELECT COUNT(quantity) FROM inventories WHERE quantity <= 20 AND user_id= %s
                ''', (id_user,))
                empty_result = cursor.fetchone()
                empty_number = empty_result[0] if empty_result else 0

                if self.prev_empty_count != empty_number or self.prev_empty_count is None:
                    self.empty_count.emit(empty_number)
                    self.prev_empty_count = empty_number

                cursor.execute('''
                    SELECT product_name, quantity, expiration_dates, product_image 
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

                if self.has_changed(self.prev_empty_list, empty_lists):
                    self.empty_list.emit(empty_lists)
                    self.prev_empty_list = empty_lists

                # تخفیف‌های منقضی‌شده
                cursor.execute('''
                    SELECT COUNT(discount_percent) FROM inventories 
                    WHERE user_id= %s AND expir_discount = 0
                ''', (id_user,))
                expire_disc_result = cursor.fetchone()
                expired_discount = expire_disc_result[0] if expire_disc_result else 0

                if self.prev_discount_count != expired_discount or self.prev_discount_count is None:
                    self.discount_expire.emit(expired_discount)
                    self.prev_discount_count = expired_discount

                cursor.execute('''
                    SELECT product_name, quantity, discount_percent, product_image
                    FROM inventories
                    WHERE expir_discount = 0 AND user_id = %s
                ''', (id_user,))
                discount_result = cursor.fetchall()
                discount_list = [{
                    "name": p_name,
                    "quantity": qty,
                    "discount_percent": round(disc) if disc is not None else 0,
                    "product_image": img or ""
                } for p_name, qty, disc, img in discount_result]

                if self.has_changed(self.prev_discount_list, discount_list):
                    self.new_discount_expired.emit(discount_list)
                    self.prev_discount_list = discount_list
                ##
                cursor.execute('''
                    SELECT 
                        i.invent_id,
                        i.product_name,i.barcode,i.expiration_dates,i.product_image,
                        pd.weight,pd.production_date,pd.brand,
                        pd.production_place,pd.product_state,pd.more_detail,pd.keep_place
                    FROM inventories i
                    JOIN product_details pd 
                        ON i.invent_id = pd.invent_id
                    WHERE i.user_id=%s and denied =1;  -- اینجا آیدی مورد نظر را بگذار
                ''',(id_user,))
                auto_msg= cursor.fetchall()
                msg_list = [{
                    "id" : invent_id,
                    "name": pro_name,
                    "barcode" : barcode,
                    "exp_date": expire_dates,
                    "img": img or "",
                    "weight": weight,
                    "pro_date": pro_date,
                    "brand": brand,
                    "place" : pro_place,
                    "pro_state": pro_state,
                    "more_details": details,
                    "keep_p" : keep_p    
                } for invent_id,pro_name,barcode,expire_dates,img,weight,pro_date,brand,pro_place,pro_state,details,keep_p in auto_msg ]
                if self.has_changed(self.prev_changed_items, msg_list):
                    self.changing_list.emit(msg_list)
                    self.prev_changed_items= msg_list

            except pymysql.Error as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")
            except Exception as e:
                print(f"خطای کلی: {e}")

            #time.sleep(1)

    def select_offline_notifi_info(self):
        while self.running:
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
                    continue
                id_user = res_id[0]
            except Exception as e:
                print(f"{e}: خطا در خواندن دیتابیس لوکال")
                continue

            try:
                today = datetime.date.today().strftime("%Y/%m/%d")

                # محصولات منقضی‌شده
                cursor_sq.execute("""
                    SELECT name, quantity, expire_date, image_path
                    FROM products
                    WHERE expire_date < ? AND user_id = ?
                """, (today, id_user))
                results = cursor_sq.fetchall()
                products = [{
                    "product_name": name,
                    "quantity": round(quantity),
                    "expiration_dates": exp_date,
                    "product_image": image_path or ""
                } for name, quantity, exp_date, image_path in results]

                if self.prev_expired_count != len(products) or self.prev_expired_count is None:
                    self.expired_count_signal.emit(len(products))
                    self.prev_expired_count = len(products)

                if self.has_changed(self.prev_expired_products, products):
                    self.new_expired_info.emit(products)
                    self.prev_expired_products = products

                # محصولات تمام‌شده
                cursor_sq.execute('''
                    SELECT COUNT(quantity) FROM products WHERE quantity <= 20 AND user_id= ?
                ''', (id_user,))
                empty_result = cursor_sq.fetchone()
                empty_number = empty_result[0] if empty_result else 0

                if self.prev_empty_count != empty_number or self.prev_empty_count is None:
                    self.empty_count.emit(empty_number)
                    self.prev_empty_count = empty_number

                cursor_sq.execute('''
                    SELECT name, quantity, expire_date, image_path FROM products
                    WHERE quantity <= 20 AND user_id = ?
                ''', (id_user,))
                empty_info = cursor_sq.fetchall()
                empty_lists = [{
                    "name": name,
                    "quantity": quantity,
                    "exp_date": exp_date,
                    "product_image": image_path
                } for name, quantity, exp_date, image_path in empty_info]

                if self.has_changed(self.prev_empty_list, empty_lists):
                    self.empty_list.emit(empty_lists)
                    self.prev_empty_list = empty_lists

                # تخفیف‌های منقضی‌شده
                cursor_sq.execute('''
                    SELECT COUNT(discount_percent) FROM products 
                    WHERE user_id = ? AND expire_discount = 0
                ''', (id_user,))
                expire_disc_result = cursor_sq.fetchone()
                expired_discount = expire_disc_result[0] if expire_disc_result else 0

                if self.prev_discount_count != expired_discount or self.prev_discount_count is None:
                    self.discount_expire.emit(expired_discount)
                    self.prev_discount_count = expired_discount

                cursor_sq.execute('''
                    SELECT name, quantity, discount_percent, image_path
                    FROM products
                    WHERE expire_discount = 0 AND user_id = ?
                ''', (id_user,))
                discount_result = cursor_sq.fetchall()
                discount_list = [{
                    "name": name,
                    "quantity": round(quantity),
                    "discount_percent": round(disc),
                    "product_image": image or ""
                } for name, quantity, disc, image in discount_result]

                if self.has_changed(self.prev_discount_list, discount_list):
                    self.new_discount_expired.emit(discount_list)
                    self.prev_discount_list = discount_list

            except sqlite3.Error as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")
            finally:
                if conn_sq:
                    conn_sq.close()

            time.sleep(2)
