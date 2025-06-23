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
import time
import os
import requests

class SaleThread(QThread):
    online_sale = pyqtSignal(float)
    ofline_sale = pyqtSignal(float)
    total_sale = pyqtSignal(float)
    monthly_sale = pyqtSignal(list,float)  # لیستی از فروش ماهانه ۱۲ ماه

    def __init__(self):
        super().__init__()

    def run(self):
        self.ofline_sa()  # این خط حیاتی است تا thread واقعاً کاری انجام دهد
        
    def ofline_sa(self):
        db_data= self.get_db_config()
        if not db_data:
            print("server errors😣")
            return
        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            print("مسیر پایگاه‌داده لوکال پیدا نشد")
            return
        try:
            conn_sq= sqlite3.connect(db_path)
            cursor_sq= conn_sq.cursor()
            cursor_sq.execute("select id from users LIMIT 1;")
            result= cursor_sq.fetchone()
            id_user= result[0]
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
            return
        
        try:
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

            # 🔹 آفلاین (بدون استفاده از پارامتر اشتباه)
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m') AS month, SUM(total)
                FROM sale_factor
                WHERE user_id = %s
                GROUP BY month
            ''', (id_user,))
            of_result = cursor.fetchall()

            total = 0
            if of_result:
                for row in of_result:
                    total += float(row[1]) if row[1] else 0
                self.ofline_sale.emit(total)
                print(f"✅ مجموع فروش آفلاین: {total}")
            else:
                print("⚠️ هیچ فروش آفلاین یافت نشد")

            # 🔹 آنلاین
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month, SUM(price)
                FROM orders
                WHERE approve = 1 AND user_id = %s
                GROUP BY month
            ''', (id_user,))
            on_result = cursor.fetchall()

            online_result = 0
            if on_result:
                for row in on_result:
                    online_result += float(row[1]) if row[1] else 0
                self.online_sale.emit(online_result)
                print(f"✅ مجموع فروش آنلاین: {online_result}")
            else:
                print("⚠️ هیچ فروش آنلاین یافت نشد")

            # 🔹 مجموع نهایی
            final_total = total + online_result
            print(f"🔷 مجموع فروش کل: {final_total}")
            self.total_sale.emit(final_total)
            
            
            # 🔹 ساخت لیست فروش هر ماه
            monthly_totals = [0] * 12

            # ← اول آفلاین‌ها
            for row in of_result:
                date_str = row[0]  # مثل "2025/01"
                amount = float(row[1]) if row[1] else 0
                try:
                    year, month = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, 1)
                    j_month = jdatetime.date.fromgregorian(date=g_date).month
                    monthly_totals[j_month - 1] += amount
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} -> {date_str}")

            # ← حالا آنلاین‌ها
            for row in on_result:
                date_str = row[0]  # مثل "2025-01"
                amount = float(row[1]) if row[1] else 0
                try:
                    year, month = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, 1)
                    j_month = jdatetime.date.fromgregorian(date=g_date).month
                    monthly_totals[j_month - 1] += amount
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آنلاین: {e} -> {date_str}")



            # ارسال فروش ماهانه
            self.monthly_sale.emit(monthly_totals,final_total)
            print(monthly_totals)

        except pymysql.Error as e:
            print(f'{e}: خطا در اتصال یا اجرای کوئری به پایگاه داده')


    
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


        

    