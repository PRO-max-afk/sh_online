from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import requests
import sqlite3
import time
import os

class NotificationChecker(QThread):
    new_message = pyqtSignal(str, str)  # ارسال همزمان product_name و message

    def __init__(self):
        super().__init__()
        self.running = True
        self.shown_messages = set()  # پیام‌های نمایش داده‌شده

    def run(self):
        while self.running:
            db_config = self.get_db_config()
            if not db_config:
                time.sleep(5)
                continue

            db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
            if not os.path.exists(db_path):
                print("مسیر پایگاه‌داده لوکال پیدا نشد")
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
                cursor.execute("""
                    SELECT product_name, product_message 
                    FROM inventories 
                    WHERE denied=1 AND user_id=%s 
                    ORDER BY user_id DESC 
                    LIMIT 1;
                """, (id_user,))
                result = cursor.fetchone()

                if result:
                    pro_name = result[0]
                    message = result[1]
                    unique_key = f"{pro_name}::{message}"

                    if unique_key not in self.shown_messages:
                        self.shown_messages.add(unique_key)
                        self.new_message.emit(pro_name, message)

                conn.close()
            except pymysql.MySQLError as e:
                print(f"{e} : خطا در اتصال یا کوئری به دیتابیس")

            time.sleep(2)  # بررسی هر ۲ ثانیه

    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data
        except Exception as e:
            print("خطا در دریافت config:", e)
            return None
