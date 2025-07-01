from PyQt6.QtCore import QThread, pyqtSignal
import os
import sqlite3 
import pymysql
import requests
from message_b import MessageBox

class UserFetchThread(QThread):
    data_ready = pyqtSignal(list)  # لیستی از کاربران را ارسال می‌کند
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            db_info = self.get_db_config()
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            if not db_info:
                print("اتصال به سرور موجود نیست")
                return

            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            conn_sq.close()

            if not res_id:
                self.error.emit("هیچ کاربری در دیتابیس محلی پیدا نشد.")
                return
            id_user = res_id[0]
        except Exception as e:
            self.error.emit(f"خطا در خواندن یوزر محلی: {e}")
            return

        try:
            conn = pymysql.connect(
                host=db_info["host"],
                user=db_info["user"],
                password=db_info["password"],
                database=db_info["database"]
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, name, last_name, approve, denied FROM mobile_user WHERE user_id=%s", (id_user,))
            result = cursor.fetchall()
            conn.close()
            self.data_ready.emit(result)
        except Exception as e:
            self.error.emit(f"خطا در اتصال یا خواندن از سرور: {e}")
    ##
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