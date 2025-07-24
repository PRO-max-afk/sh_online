from PyQt6.QtCore import QThread, pyqtSignal
import os
import sqlite3 
import pymysql
import requests
from message_b import MessageBox
from db_connection import Connection

class UserFetchThread(QThread):
    data_ready = pyqtSignal(list)  # لیستی از کاربران را ارسال می‌کند
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            db_info = Connection().get_connection()
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
            cursor = db_info.cursor()
            cursor.execute("SELECT id, username, name, last_name, approve, denied FROM mobile_user WHERE user_id=%s", (id_user,))
            result = cursor.fetchall()
            db_info.close()
            self.data_ready.emit(result)
        except Exception as e:
            self.error.emit(f"خطا در اتصال یا خواندن از سرور: {e}")
    