نه نشد هیچ مشکل از ترید است مخصوصاً از تابع run است اطلاعات sale_signal را ارسال میکند ولی از buy_signal را ارسال نمیکند بیا و مشکل از ریشه حل کن و برای بررسی دقیق تر اطلاعات buy_signal را بعداز اضافه کردن به دیکشنری چاپ کن:from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import requests
import sqlite3
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
from message_b import MessageBox
import os
import requests
from db_connection import Connection
import jdatetime
import datetime
from datetime import date


class ItemThread(QThread):
    sale_box_signal= pyqtSignal(dict)
    buy_box_signal= pyqtSignal(dict)
    def __init__(self,selected_month=None):
        super().__init__()
        self.selected_month= selected_month
        self.db_connect= Connection().get_connection()
    
    def run(self):
        if self.db_connect:
            if self.selected_month:
                self.sale_signal()
                self.buy_signal()

    
    def sale_signal(self):
        data_connect= Connection().get_connection()
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db path found!")
            return
        if not data_connect:
            print("no online db connection!")
            return
        try:
            conn_sq= sqlite3.connect(db_path)
            cursor_sq= conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result= cursor_sq.fetchone()
            id_user= id_result[0]
        except sqlite3.Error as e:
            print(f"{e} : offline db problem")
            return
        
        try:
            cursor = data_connect.cursor()

            # داده‌های آفلاین (sale_factor)
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS date,COUNT(quantity), product_name
                FROM sale_factor
                WHERE user_id = %s
                GROUP BY date, product_name

            ''', (id_user,))
            offline_data = cursor.fetchall()

            # داده‌های آنلاین (orders)
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y/%%m/%%d') AS date,COUNT(quantity),product_name
                FROM orders
                WHERE user_id = %s
                GROUP BY date, product_name

            ''', (id_user,))
            online_data = cursor.fetchall()

            # آماده‌سازی متغیرها
            monthly_totals = [0] * 12
            sale_stats = {
                "online_sale": 0,
                "offline_sale": 0,
                "best_item": "",
            }
            product_counter = {}

            for row in offline_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year

                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        sale_stats["offline_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)

                    monthly_totals[j_month - 1] += int(quantity)

                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {date_str}")

            for row in online_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("-"))  # ← فرق این‌جا
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year

                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        sale_stats["online_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)

                    monthly_totals[j_month - 1] += int(quantity)

                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آنلاین: {e} → {date_str}")

            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                sale_stats["best_item"] = best_item
                print(f"🔥 پرفروش‌ترین محصول: {best_item} ({product_counter[best_item]})")

            # ارسال اطلاعات فروش این ماه
            self.sale_box_signal.emit(sale_stats)

        except pymysql.Error as e:
            print(f"{e} : online problem")

    def buy_signal(self):
        date_now= datetime.date.today().strftime('%Y/%m/%d')
        data_connect= Connection().get_connection()
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db path found!")
            return
        if not data_connect:
            print("no online db connection!")
            return
        try:
            conn_sq= sqlite3.connect(db_path)
            cursor_sq= conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result= cursor_sq.fetchone()
            id_user= id_result[0]
        except sqlite3.Error as e:
            print(f"{e} : offline db problems")
            return
        
        try:
            cursor = data_connect.cursor()
            ##  تعداد خرید
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventories WHERE user_id = %s
                GROUP BY month
            ''',(id_user,))
            number_result= cursor.fetchall()
            # تاریخ گذشته
            cursor.execute('''
                    SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') as month, COUNT(quantity) as quantity
                    FROM inventories WHERE user_id= %s AND expiration_dates < %s
                    GROUP BY month
            ''',(id_user,date_now))
            expire_result= cursor.fetchall()
            # تکراری ترین خرید
            cursor.execute('''
                SELECT 
                DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month,
                product_name,
                SUM(quantity) AS total_quantity
                FROM inventory_log
                WHERE user_id = %s AND type_save= 'inventory'
                GROUP BY month, product_name
                ORDER BY month, total_quantity DESC;
                ''',(id_user,))
            repeated_reult= cursor.fetchall()
            #اتمام محصول
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventories WHERE user_id = %s AND quantity < 0 
                GROUP BY month
            ''',(id_user,))
            empty_result= cursor.fetchall()

            monthly_total = [0] * 12
            buy_stats= {
                "buy_items" : 0,
                "low_items": 0,
                "repeated_items" : 0,
                "expired_items" : 0
            }
            product_counter={}
            # number of quantity
            for result_set in (number_result, empty_result):
                for row in result_set:
                    try:
                        date_str, quantity = row
                        year, month, day = map(int, date_str.split("/"))
                        g_date = datetime.date(year, month, day)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_month = j_date.month
                        j_year = j_date.year

                        key = f"{j_year:04d} / {j_month:02d}"
                        if self.selected_month and self.selected_month == key:
                            if result_set is number_result:
                                buy_stats["buy_items"] += int(quantity)
                            elif result_set is empty_result:
                                buy_stats["low_items"] += int(quantity)

                        monthly_total[j_month - 1] += int(quantity)
                

                    except Exception as e:
                        print(f"⚠️ error in changing date for quantity {e} → {date_str}")

                # expired product
                for row in expire_result:
                    date_str,quantity= row 
                    try:

                        year,month,day= map(int, date_str.split("/"))
                        g_date= datetime.date(year, month, day)
                        j_date= jdatetime.date.fromgregorian(date=g_date)
                        j_month= j_date.month
                        j_year= j_date.year
                        key=f"{j_year:04d} / {j_month:02d}"
                        if self.selected_month and self.selected_month == key:
                            buy_stats["expired_items"] += int(quantity)

                        monthly_total[j_month -1] += int(quantity)
                    except Exception as e:
                        print(f"⚠️ error in change exp_date {e} → {date_str}")
                    # repeate  buy
                    for row in repeated_reult:
                        date_str, name, quantity = row
                        try:
                            year, month, day = map(int, date_str.split("/"))
                            g_date = datetime.date(year, month, day)
                            j_date = jdatetime.date.fromgregorian(date=g_date)
                            j_month = j_date.month
                            j_year = j_date.year

                            key = f"{j_year:04d} / {j_month:02d}"
                            if self.selected_month and self.selected_month == key:
                                product_counter[name] = product_counter.get(name, 0) + int(quantity)
                            monthly_total[j_month - 1] += int(quantity)
                        except Exception as e:
                            print(f"⚠️ error in repeated buy {e} → {date_str}")

                    if product_counter:
                        best_item = max(product_counter, key=product_counter.get)
                        buy_stats["repeated_items"] = best_item
                        print(f"🔥 تکراری‌ترین خرید: {best_item} ({product_counter[best_item]})")

                    # ✅ حالا فقط یک بار سیگنال بده
                    self.buy_box_signal.emit(buy_stats)


        except pymysql.Error as e:
            print(f"{e} : online db problems")
