from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import time
import os
import requests

class OrderInformation(QThread):
    new_order_info = pyqtSignal(list)  # لیستی از دیکشنری‌ها شامل اطلاعات محصولات
    order_count_signal = pyqtSignal(int)

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

                cursor.execute("""
                    SELECT id,customer_name, product_name,quantity, area, home_number,phone
                    FROM orders
                    WHERE  user_id = %s
                """, (id_user))
                results = cursor.fetchall()

                products = []
                for row in results:
                    id_order, name, product_name, quantity, area, home_number, phone = row
                    products.append({
                        "id": id_order,
                        "customer_name": name,
                        "product_name": product_name,
                        "quantity": quantity,
                        "area": area,
                        "home_number": home_number,
                        "phone": phone
                    })

                count = len(products)
                if count != self.prev_count:
                    self.prev_count = count
                    self.order_count_signal.emit(count)  # ← اینجا تعداد سفارشات ارسال می‌شود
                    self.new_order_info.emit(products)


                conn.close()
            except pymysql.MySQLError as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")

            time.sleep(5)

    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ JSON معتبر نیست")

            data = response.json()
            if all(k in data for k in ("host", "user", "password", "database")):
                return data
            else:
                raise ValueError("پاسخ JSON ناقص است")
        except Exception as e:
            print("❌ خطا در دریافت کانفیگ:", e)
            return None
