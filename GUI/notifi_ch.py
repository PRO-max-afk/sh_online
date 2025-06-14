from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
from datetime import date
import time
import os
import requests

class ExpirationNotifier(QThread):
    new_expired_info = pyqtSignal(list)  # لیستی از دیکشنری‌ها شامل اطلاعات محصولات
    expired_count_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.prev_count = -1

    def run(self):
        while self.running:
            db_config = self.get_db_config()
            if not db_config:
                time.sleep(5)
                continue

            db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
            if not os.path.exists(db_path):
                print("⚠️ مسیر دیتابیس لوکال یافت نشد.")
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
                conn = pymysql.connect(
                    host=db_config["host"],
                    user=db_config["user"],
                    passwd=db_config["password"],
                    database=db_config["database"]
                )
                cursor = conn.cursor()

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

                conn.close()
            except pymysql.MySQLError as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")

            time.sleep(5)

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

