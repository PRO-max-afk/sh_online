from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import requests
import sqlite3
import time
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
import time
import os
import requests
from message_b import MessageBox

class NotificationChecker(QThread):
    new_message = pyqtSignal(str, str)  # ارسال همزمان product_name و message
    new_count = pyqtSignal(int)
    
    

    def __init__(self):
        super().__init__()
        self.running = True
        self.shown_messages = set()
        self.count_ms = set()

    def run(self):
        while self.running:
            db_config = self.get_db_config()
            if not db_config:
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
                id_user = res_id[0]
            except Exception as e:
                print(f"{e}: خطا در دیتابیس لوکال")
                return

            try:
                conn = pymysql.connect(
                    host=db_config["host"],
                    user=db_config["user"],
                    passwd=db_config["password"],
                    database=db_config["database"]
                )
                cursor = conn.cursor()

                # پیام محصول
                cursor.execute("""
                    SELECT product_name, product_message 
                    FROM inventories 
                    WHERE denied=1 AND user_id=%s 
                    ORDER BY user_id DESC 
                    LIMIT 1;
                """, (id_user,))
                result = cursor.fetchone()

                # تعداد پیام‌ها
                cursor.execute("""
                    SELECT COUNT(product_message) 
                    FROM inventories 
                    WHERE denied=1 AND user_id=%s;
                """, (id_user,))
                m_count = cursor.fetchone()[0]

                # تعداد تاریخ‌های انقضا معتبر
                jalali_date = datetime.date.today().strftime("%Y/%m/%d")
                cursor.execute("""
                    SELECT COUNT(expiration_dates) 
                    FROM inventories 
                    WHERE expiration_dates < %s AND user_id=%s;
                """, (jalali_date, id_user))
                e_count = cursor.fetchone()[0]
                ##
                cursor.execute('''
                    SELECT COUNT(discount_percent) FROM inventories 
                    WHERE user_id= %s AND expir_discount= 0
                ''',(id_user,))
                expire_disc_result= cursor.fetchone()
                if expire_disc_result:
                    exp_count= expire_disc_result[0]
                
                ##
                cursor.execute('''
                    SELECT COUNT(quantity) as quanity from inventories WHERE quantity < 0  and user_id= %s
                    ''',(id_user,))
                empty_result= cursor.fetchone()
                if empty_result:
                    empty_count= empty_result[0]
                


                total_count = m_count + e_count + empty_count + exp_count

                if total_count not in self.count_ms:
                    self.count_ms.add(total_count)
                    self.new_count.emit(total_count)  # ارسال مقدار عددی


                if result:
                    pro_name, message = result
                    unique_key = f"{pro_name}::{message}"
                    if unique_key not in self.shown_messages:
                        self.shown_messages.add(unique_key)
                        self.new_message.emit(pro_name, message)
                

                conn.close()
            except pymysql.MySQLError as e:
                print(f"{e} : خطا در اتصال یا کوئری به دیتابیس")

            time.sleep(2)

    def get_db_config(self):

        url = "https://aryaict.com/connect.php"

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        cookies = {
            'humans_21909': '1'
        }

        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=60)

            if response.status_code != 200:
                print("⚠️ خطای ارتباطی:", response.status_code, response.text)
                response.raise_for_status()

            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست! محتوای پاسخ:\n" + response.text)

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است:\n" + str(data))

            return data

        except Exception as e:
            print("❌ خطا در دریافت کانفیگ:", e)
            return None

