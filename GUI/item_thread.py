from PyQt6.QtCore import QThread, pyqtSignal
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
    ##
    day_sale_signal= pyqtSignal(dict)
    day_buy_signal= pyqtSignal(dict)
    ##
    sale_table_data= pyqtSignal(dict)
    buy_table_data= pyqtSignal(dict)
    ##
    sale_table_data_day= pyqtSignal(dict)
    buy_table_data_day= pyqtSignal(dict)

    def __init__(self,selected_month=None,selected_date= None):
        super().__init__()
        self.selected_month= selected_month
        self.selected_date= selected_date
        
    
    def run(self):
            if self.selected_month:
                self.offline_sale_month()
                self.offline_sale_table()
                self.offline_buy_month()
                self.excecute_buy_table_offline_month()
            if self.selected_date:
                self.offline_sale_day()
                self.offline_buy_day()
                self.offline_sale_table_day()
                self.excecute_buy_table_day_offline()
            


    
    def sale_signal(self):
        data_connect = Connection().get_connection()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        print(f"{db_path}: offline db_path")

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        if not data_connect:
            print("⚠️ no online db connection!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result = cursor_sq.fetchone()
            id_user = id_result[0]
        except sqlite3.Error as e:
            print(f"❌ {e} : offline db problem")
            return

        try:
            cursor = data_connect.cursor()

            # آفلاین (sale_factor)
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS date, COUNT(quantity), product_name
                FROM sale_factor
                WHERE user_id = %s
                GROUP BY date, product_name
            ''', (id_user,))
            offline_data = cursor.fetchall()

            # آنلاین (orders)
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y/%%m/%%d') AS date, COUNT(quantity), product_name
                FROM orders
                WHERE user_id = %s
                GROUP BY date, product_name
            ''', (id_user,))
            online_data = cursor.fetchall()

            # خروجی‌ها
            monthly_totals = [0] * 12
            sale_stats = {
                "online_sale": 0,
                "offline_sale": 0,
                "best_item": "خالی",
            }


            product_counter = {}

            # آفلاین
            for row in offline_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key_month:
                        sale_stats["offline_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                    monthly_totals[j_month - 1] += int(quantity)


                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {date_str}")

            # آنلاین
            for row in online_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key_month:
                        sale_stats["online_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                    monthly_totals[j_month - 1] += int(quantity)

                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آنلاین: {e} → {date_str}")

            # انتخاب بهترین کالا
            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                sale_stats["best_item"] = best_item
            
            self.sale_box_signal.emit(sale_stats)
            print(f"📦 ماهانه ارسال شد: {sale_stats}")
        
        except pymysql.Error as e:
            print(f"❌ MySQL error: {e}")


    def buy_signal(self):
        date_now = datetime.date.today().strftime('%Y/%m/%d')
        data_connect = Connection().get_connection()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        if not data_connect:
            print("⚠️ no online db connection!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result = cursor_sq.fetchone()
            id_user = id_result[0]
        except sqlite3.Error as e:
            print(f"❌ {e} : offline db problems")
            return

        try:
            cursor = data_connect.cursor()

            # تعداد خرید
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventory_log WHERE user_id = %s AND type_save= 'inventory'
                GROUP BY month
            ''', (id_user,))
            number_result = cursor.fetchall()

            # تاریخ گذشته
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') as month, COUNT(quantity) as quantity
                FROM inventory_log WHERE user_id = %s AND expiration_dates < %s AND type_save= 'inventory'
                GROUP BY month
            ''', (id_user, date_now))
            expire_result = cursor.fetchall()

            # تکراری‌ترین خرید
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, product_name, SUM(quantity) AS total_quantity
                FROM inventory_log
                WHERE user_id = %s AND type_save= 'inventory'
                GROUP BY month, product_name
                ORDER BY month, total_quantity DESC
            ''', (id_user,))
            repeated_result = cursor.fetchall()

            # اتمام محصول
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventories WHERE user_id = %s AND quantity < 0 
                GROUP BY month
            ''', (id_user,))
            empty_result = cursor.fetchall()

            # پردازش نتایج
            monthly_total = [0] * 12
            buy_stats = {
                "buy_items": 0,
                "low_items": 0,
                "repeated_items": "خالی",
                "expired_items": 0
            }

            product_counter = {}

            # تعداد خرید و اتمام محصول
            for result_set in (number_result, empty_result):
                for row in result_set:
                    try:
                        date_str, quantity = row
                        year, month, day = map(int, date_str.split("/"))
                        g_date = datetime.date(year, month, day)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_month = j_date.month
                        j_year = j_date.year

                        key = f"{j_year:04d}/{j_month:02d}"

                        if self.selected_month and self.selected_month == key:
                            if result_set is number_result:
                                buy_stats["buy_items"] += int(quantity)
                            elif result_set is empty_result:
                                buy_stats["low_items"] += int(quantity)

                    except Exception as e:
                        print(f"⚠️ error in quantity convert: {e} → {row}")

            # تاریخ گذشته
            for row in expire_result:
                try:
                    date_str, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        buy_stats["expired_items"] += int(quantity)

                except Exception as e:
                    print(f"⚠️ error in expired convert: {e} → {row}")

            # تکراری‌ترین خرید
            for row in repeated_result:
                try:
                    date_str, name, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                except Exception as e:
                    print(f"⚠️ error in repeated convert: {e} → {row}")

            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                buy_stats["repeated_items"] = best_item

            print(f"📦 ماهانه buy_stats → {buy_stats}")
            self.buy_box_signal.emit(buy_stats)


        except pymysql.Error as e:
            print(f"❌ {e} : MySQL execution error")

    ################## day_signals    
    def sale_day_signal(self):
        data_connect = Connection().get_connection()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        if not data_connect:
            print("⚠️ no online db connection!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result = cursor_sq.fetchone()
            id_user = id_result[0]
        except sqlite3.Error as e:
            print(f"❌ {e} : offline db problem")
            return

        try:
            cursor = data_connect.cursor()

            # آفلاین (sale_factor)
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS date, COUNT(quantity), product_name
                FROM sale_factor
                WHERE user_id = %s
                GROUP BY date, product_name
            ''', (id_user,))
            offline_data = cursor.fetchall()

            # آنلاین (orders)
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y/%%m/%%d') AS date, COUNT(quantity), product_name
                FROM orders
                WHERE user_id = %s
                GROUP BY date, product_name
            ''', (id_user,))
            online_data = cursor.fetchall()
            # خروجی‌ها
            sale_day_stats = {
                "online_sale": 0,
                "offline_sale": 0,
                "best_item": "خالی",
            }


            product_counter = {}

            # آفلاین
            for row in offline_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست

                    if self.selected_date and self.selected_date == key_day:
                        sale_day_stats["offline_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)

                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {date_str}")

            # آنلاین
            for row in online_data:
                date_str, quantity, name = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست

                    if self.selected_date and self.selected_date == key_day:
                        sale_day_stats["online_sale"] += int(quantity)
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)


                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آنلاین: {e} → {date_str}")

            # انتخاب بهترین کالا
            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                sale_day_stats["best_item"] = best_item
            
            self.day_sale_signal.emit(sale_day_stats)
            print(f"📦 ماهانه ارسال شد: {sale_day_stats}")
        
        except pymysql.Error as e:
            print(f"❌ MySQL error: {e}")

    def buy_day_signal(self):
        date_now = datetime.date.today().strftime('%Y/%m/%d')
        data_connect = Connection().get_connection()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        if not data_connect:
            print("⚠️ no online db connection!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result = cursor_sq.fetchone()
            id_user = id_result[0]
        except sqlite3.Error as e:
            print(f"❌ {e} : offline db problems")
            return

        try:
            cursor = data_connect.cursor()

            # تعداد خرید
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventories WHERE user_id = %s
                GROUP BY month
            ''', (id_user,))
            number_result = cursor.fetchall()

            # تاریخ گذشته
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') as month, COUNT(quantity) as quantity
                FROM inventories WHERE user_id = %s AND expiration_dates < %s
                GROUP BY month
            ''', (id_user, date_now))
            expire_result = cursor.fetchall()

            # تکراری‌ترین خرید
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, product_name, SUM(quantity) AS total_quantity
                FROM inventory_log
                WHERE user_id = %s AND type_save= 'inventory'
                GROUP BY month, product_name
                ORDER BY month, total_quantity DESC
            ''', (id_user,))
            repeated_result = cursor.fetchall()

            # اتمام محصول
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS month, COUNT(quantity) as quantity 
                FROM inventories WHERE user_id = %s AND quantity < 0 
                GROUP BY month
            ''', (id_user,))
            empty_result = cursor.fetchall()

            # نتایج روزانه
            buy_day_stats= {
                "buy_items": 0,
                "low_items": 0,
                "repeated_items": "خالی",
                "expired_items": 0
            }
            product_counter = {}

            # تعداد خرید و اتمام محصول
            for result_set in (number_result, empty_result):
                for row in result_set:
                    try:
                        date_str, quantity = row
                        year, month, day = map(int, date_str.split("/"))
                        g_date = datetime.date(year, month, day)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_month = j_date.month
                        j_year = j_date.year
                        j_day= j_date.day

                        key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست


                        if self.selected_date and self.selected_date == key:
                            if result_set is number_result:
                                buy_day_stats["buy_items"] += int(quantity)
                            elif result_set is empty_result:
                                buy_day_stats["low_items"] += int(quantity)

                    except Exception as e:
                        print(f"⚠️ error in quantity convert: {e} → {row}")

            # تاریخ گذشته
            for row in expire_result:
                try:
                    date_str, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    j_day= j_date.day
                    key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست


                    if self.selected_date and self.selected_date == key:
                        buy_day_stats["expired_items"] += int(quantity)

                except Exception as e:
                    print(f"⚠️ error in expired convert: {e} → {row}")

            # تکراری‌ترین خرید
            for row in repeated_result:
                try:
                    date_str, name, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    j_day= j_date.day
                    key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست

                    if self.selected_date and self.selected_date == key:
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                except Exception as e:
                    print(f"⚠️ error in repeated convert: {e} → {row}")

            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                buy_day_stats["repeated_items"] = best_item

            print(f"📦 ماهانه buy_day_stats → {buy_day_stats}")
            self.day_buy_signal.emit(buy_day_stats)


        except pymysql.Error as e:
            print(f"❌ {e} : MySQL execution error")
    ###### table info
    def excecute_sale_table(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor_sq.fetchone()
            id_user = rest_id[0]
        except sqlite3.Error as e:
            print(f'{e}: offline db table problem')
            return

        try:
            cursor = self.db_connect.cursor()
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS month_date,
                    product_name, quantity, product_type, total, sale_type
                FROM sale_factor
                WHERE user_id = %s
            ''', (id_user,))
            sale_info = cursor.fetchall()

            row_data = {}
            row_index = 0

            for row in sale_info:
                date_str, product_name, quantity, product_type, total, sale_type = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_month and self.selected_month == key_month:
                        if sale_type == "عمده":
                            # واکشی big_quantity برای این محصول
                            cursor.execute('''
                                SELECT big_quantity FROM inventories
                                WHERE user_id = %s AND product_name = %s
                                LIMIT 1
                            ''', (id_user, product_name))
                            bg_result = cursor.fetchone()
                            if bg_result and bg_result[0] > 0:
                                big_quantity = bg_result[0]
                                best_quantity = quantity / big_quantity
                            else:
                                print(f"⚠️ مقدار big_quantity برای '{product_name}' یافت نشد یا صفر است.")
                                best_quantity = quantity  # fallback
                        else:
                            best_quantity = quantity

                        row_data[row_index] = [product_name, best_quantity, product_type, total]
                        row_index += 1

                except Exception as e:
                    print(f"⚠️ خطا در پردازش ردیف فروش: {e} → {row}")
                ## orders:
                cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS order_month, product_name,
                quantity,price,product_unit FROM orders  
                WHERE user_id= %s AND approve=1
            ''',(id_user,))
                order_result= cursor.fetchall()
                for row in order_result:
                    date_r, pro_name,quanties,price,product_unit= row
                    try:
                        year,month,day= map(int, date_r.split("-"))
                        g_dates= datetime.date(year,month,day)
                        j_dates= jdatetime.date.fromgregorian(date=g_dates)
                        j_years= j_dates.year
                        j_monhts= j_dates.month
                        key= f"{j_years:04d}/{j_monhts:02d}"
                        if self.selected_month and self.selected_month== key:
                            row_data[row_index]= [pro_name,quanties,product_unit,price]
                            row_index +=1

                    except Exception as e:
                        print(f'{e}: online db problem sale')

                self.sale_table_data.emit(row_data)


        except pymysql.Error as e:
            print(f"{e} : db online table error")
    ##
    def excecute_sale_table_day(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor_sq.fetchone()
            id_user = rest_id[0]
        except sqlite3.Error as e:
            print(f'{e}: offline db table problem')
            return

        try:
            cursor = self.db_connect.cursor()
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS month_date,
                    product_name, quantity, product_type, total, sale_type
                FROM sale_factor
                WHERE user_id = %s
            ''', (id_user,))
            sale_info = cursor.fetchall()

            row_datas = {}
            row_index = 0

            for row in sale_info:
                date_str, product_name, quantity, product_type, total, sale_type = row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_date and self.selected_date == key_day:
                        if sale_type == "عمده":
                            # واکشی big_quantity برای این محصول
                            cursor.execute('''
                                SELECT big_quantity FROM inventories
                                WHERE user_id = %s AND product_name = %s
                                LIMIT 1
                            ''', (id_user, product_name))
                            bg_result = cursor.fetchone()
                            if bg_result and bg_result[0] > 0:
                                big_quantity = bg_result[0]
                                best_quantity = quantity / big_quantity
                            else:
                                print(f"⚠️ مقدار big_quantity برای '{product_name}' یافت نشد یا صفر است.")
                                best_quantity = quantity  # fallback
                        else:
                            best_quantity = quantity

                        row_datas[row_index] = [product_name, best_quantity, product_type, total]
                        row_index += 1

                except Exception as e:
                    print(f" sale factor: {e} → {row}")
                ## orders:
                cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS order_month, product_name,
                quantity,price,product_unit FROM orders  
                WHERE user_id= %s AND approve=1
            ''',(id_user,))
                order_result= cursor.fetchall()
                for row in order_result:
                    date_r, pro_name,quanties,price,product_unit= row
                    try:
                        year,month,day= map(int, date_r.split("-"))
                        g_dates= datetime.date(year,month,day)
                        j_dates= jdatetime.date.fromgregorian(g_dates)
                        j_years= j_dates.year
                        j_monhts= j_dates.month
                        j_day= j_dates.day
                        key= f"{j_years:04d}/{j_monhts:02d}/{j_day:02d}"

                        if self.selected_date and self.selected_date== key:
                            row_datas[row_index]= [pro_name,quanties,product_unit,price]
                            row_index +=1

                    except Exception as e:
                        print(f'{e}: online db problem sale')

                self.sale_table_data_day.emit(row_datas)


        except pymysql.Error as e:
            print(f"{e} : db online table error")

    ############today
    def excecute_buy_table(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor_sq.fetchone()
            id_user = rest_id[0]
        except sqlite3.Error as e:
            print(f'{e}: offline db table problem')
            return

        try:
            cursor = self.db_connect.cursor()
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS month_date,
                    product_name, big_sub,big_category,total
                FROM inventory_log
                WHERE user_id = %s AND type_save= 'inventory'
            ''', (id_user,))
            sale_info = cursor.fetchall()

            row_data = {}
            row_index = 0

            for row in sale_info:
                date_str, product_name, big_sub, big_category, total,  = row
                try:
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_month and self.selected_month == key_month:
                        row_data[row_index] = [product_name, big_sub, big_category, total]
                        row_index += 1

                except Exception as e:
                    print(f" table month problem for buying: {e} → {row}")
               
                self.buy_table_data.emit(row_data)


        except pymysql.Error as e:
            print(f"{e} : db online table error")
    ##
    def excecute_buy_table_day(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor_sq.fetchone()
            id_user = rest_id[0]
        except sqlite3.Error as e:
            print(f'{e}: offline db table problem')
            return

        try:
            cursor = self.db_connect.cursor()
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS month_date,
                    product_name, big_sub, big_category, total
                FROM inventory_log
                WHERE user_id = %s AND type_save= 'inventory'
            ''', (id_user,))
            buy_info = cursor.fetchall()

            row_datas = {}
            row_index = 0

            for row in buy_info:
                date_str, product_name, big_sub, big_category, total = row
                try:
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_date and self.selected_date == key_day:
                        row_datas[row_index] = [product_name, big_sub, big_category, total]
                        row_index += 1

                except Exception as e:
                    print(f" day table problem: {e} → {row}")
                ### sending signal
                self.buy_table_data_day.emit(row_datas)


        except pymysql.Error as e:
            print(f"{e} : db online table error")
    ##############offline mode
    def offline_sale_month(self):
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline month sale db found")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_result = cursor.fetchone()
            id_user = id_result[0]
            cursor.execute(''' 
                SELECT
                strftime('%Y/%m/%d', REPLACE(sale_date, '/', '-')) AS month_sale,
                COUNT(quantity),
                product_name
                FROM sale_factor
                WHERE user_id = ?
                GROUP BY month_sale, product_name;
            ''',(id_user,))
            offline_result= cursor.fetchall()

            monthly_totals= [0] *12
            product_Counter= {}
            sale_stats_off= {
                "online_sale": 0,
                "offline_sale": 0,
                "best_item": "خالی",
            }

            for row in offline_result:
                date_str,quantity,pro_name= row
                try:
                    year,month,day= map(int, date_str.split("/"))
                    g_date= datetime.date(year,month,day)
                    j_date= jdatetime.date.fromgregorian(date=g_date)
                    j_year= j_date.year
                    j_month= j_date.month

                    key_month= f"{j_year:04d}/{j_month:02d}"
                    if self.selected_month and self.selected_month== key_month:
                        sale_stats_off["offline_sale"] += int(quantity)
                        product_Counter[pro_name] = product_Counter.get(pro_name,0) + int(quantity)
                    monthly_totals[key_month -1] += int(quantity)
                except Exception as e:
                    print(f"⚠️db خطا در تبدیل تاریخ آفلاین: {e} → {date_str}")
                ##
                if product_Counter:
                    best_item= max(product_Counter, key=product_Counter.get)
                    sale_stats_off["best_item"] = best_item
                ##
                print(f'month sale offline :{sale_stats_off}')
                self.sale_box_signal.emit(sale_stats_off)
                

        except sqlite3.Error as e:
            print(f"{e}: offline month db problem")
    ##
    def offline_sale_day(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("select id from users limit 1")
            id_result = cursor_sq.fetchone()
            id_user = id_result[0]
            cursor_sq.execute('''
                SELECT 
                strftime('%Y/%m/%d', REPLACE(sale_date, '/', '-')) as day_sale,
                COUNT(quantity),
                product_name
                FROM sale_factor
                WHERE user_id = ?
                GROUP BY day_sale, product_name;
            ''',(id_user,))
            offline_day_result= cursor_sq.fetchall()
            ##
            sale_day_stats_off = {
                "online_sale": 0,
                "offline_sale": 0,
                "best_item": "خالی"}
            
            product_counter= {}

            for row in offline_day_result:
                date_str, quantity, pro_name =row
                try:
                    year, month, day= map(int, date_str.split("/"))
                    g_date= datetime.date(year,month,day)
                    j_date= jdatetime.date.fromgregorian(date= g_date)
                    j_year= j_date.year
                    j_month= j_date.month
                    j_day= j_date.day
                    key_day= f'{j_year:04d}/{j_month:02d}/{j_day:02d}'
                    if self.selected_date and self.selected_date== key_day:
                        sale_day_stats_off["offline_sale"] += int(quantity)
                        product_counter[pro_name] = product_counter.get(pro_name,0) + int(quantity)
                except Exception as e:
                    print(f"⚠️  db_dayخطا در تبدیل تاریخ آفلاین: {e} → {date_str}")
                ##
            if product_counter:
                best_item= max(product_counter, key=product_counter.get)
                sale_day_stats_off["best_item"] = best_item
            self.day_sale_signal.emit(sale_day_stats_off)

        except sqlite3.Error as e:
            print(f'offline day problem: {e}')
    ##
    def offline_sale_table(self):
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline month sale db found")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_result = cursor.fetchone()
            id_user = id_result[0]
            cursor.execute(''' 
                SELECT strftime('%Y/%m/%d', REPLACE(sale_date, '/', '-')) AS month_sale,
                product_name,quantity,product_type,total,sale_type
                FROM sale_factor
                WHERE user_id = ?
                GROUP BY month_sale, product_name;
            ''',(id_user,))
            offline_result_table= cursor.fetchall()
            
            row_data= {}
            row_index= 0

            for row in offline_result_table:
                date_str, product_name,quantity,product_type,total,sale_type= row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"
                    
                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_month and self.selected_month == key_month:
                        if sale_type == "عمده":
                            # واکشی big_quantity برای این محصول
                            cursor.execute('''
                                SELECT big_quantity FROM sale_factor
                                WHERE user_id= ? AND product_name= ?
                            ''',(id_user,product_name))
                            bg_result = cursor.fetchone()
                            if bg_result and bg_result[0] > 0:
                                big_quantity = bg_result[0]
                                best_quantity = quantity / big_quantity
                            else:
                                print(f"⚠️ مقدار big_quantity برای '{product_name}' یافت نشد یا صفر است.")
                                best_quantity = quantity  # fallback
                        else:
                            best_quantity = quantity

                        row_data[row_index] = [product_name, best_quantity, product_type, total]
                        row_index += 1


                except Exception as e:
                    print(f"⚠️ db tableخطا در پردازش ردیف فروش: {e} → {row}")
            ##
            print(f"offline sale table info month: {row_data}")
            self.sale_table_data.emit(row_data)
        except pymysql.Error as e:
            print(f"{e} : db online table error")
    ######### buy_date
    def offline_buy_month(self):
        date_now = datetime.date.today().strftime('%Y/%m/%d')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_result = cursor.fetchone()
            id_user = id_result[0]
            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-')) AS month_buy, COUNT(quantity) as quantity
                FROM products_log
                GROUP BY month_buy
            ''')
            number_result= cursor.fetchall()
            ##
            cursor.execute('''
                SELECT strftime('%Y/%m/%d', REPLACE(buy_date, '/', '-'))  AS month_buy, COUNT(quantity) as quantity
                FROM products WHERE user_id= ? AND expire_date < ?
                GROUP BY month_buy
                ''',(id_user,date_now))
            expire_result= cursor.fetchall()
            ##
            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-'))  AS month_buy, name, SUM(quantity) as quantity
                FROM products_log 
                GROUP BY month_buy,name
                ORDER BY month_buy,quantity DESC
                ''')
            repeated_result= cursor.fetchall()
            # اتمام محصول
            cursor.execute('''
                SELECT strftime('%Y/%m/%d', REPLACE(buy_date, '/', '-'))  AS month, COUNT(quantity) as quantity 
                FROM products WHERE user_id = ? AND quantity < 0 
                GROUP BY month
            ''', (id_user,))
            empty_result = cursor.fetchall()

            # پردازش نتایج
            monthly_total = [0] * 12
            buy_stats_offline = {
                "buy_items": 0,
                "low_items": 0,
                "repeated_items": "خالی",
                "expired_items": 0}
            
            product_counter = {}

            # تعداد خرید و اتمام محصول
            for result_set in (number_result, empty_result):
                for row in result_set:
                    try:
                        date_str, quantity = row

                        # تشخیص فرمت تاریخ
                        if "-" in date_str:
                            g_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        elif "/" in date_str:
                            g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        else:
                            raise ValueError(f"Unknown date format: {date_str}")

                        # تبدیل به تاریخ شمسی
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_month = j_date.month
                        j_year = j_date.year

                        key = f"{j_year:04d}/{j_month:02d}"

                        if self.selected_month and self.selected_month == key:
                            if result_set is number_result:
                                buy_stats_offline["buy_items"] += int(quantity)
                            elif result_set is empty_result:
                                buy_stats_offline["low_items"] += int(quantity)

                        monthly_total[j_month - 1] += int(quantity)

                    except Exception as e:
                        print(f"⚠️ error in quantity convert: {e} → {row}")


            # تاریخ گذشته
            for row in expire_result:
                try:
                    date_str, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        buy_stats_offline["expired_items"] += int(quantity)
                    monthly_total[j_month -1] += int(quantity)

                except Exception as e:
                    print(f"⚠️ error in expired convert: {e} → {row}")

            # تکراری‌ترین خرید
            for row in repeated_result:
                try:
                    date_str, name, quantity = row
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    key = f"{j_year:04d}/{j_month:02d}"

                    if self.selected_month and self.selected_month == key:
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                    monthly_total[j_month -1] += int(quantity)
                except Exception as e:
                    print(f"⚠️ error in repeated convert: {e} → {row}")

            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                buy_stats_offline["repeated_items"] = best_item

            print(f"📦 ماهانه buy_stats → {buy_stats_offline}")
            self.buy_box_signal.emit(buy_stats_offline)

        except pymysql.Error as e:
            print(f"{e} : db online table error")
    ##
    def offline_buy_day(self):
        date_now = datetime.date.today().strftime('%Y/%m/%d')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("⚠️ no offline db path found!")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_result = cursor.fetchone()
            id_user = id_result[0]
            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-'))  AS month_buy, COUNT(quantity) as quantity
                FROM products_log
                GROUP BY month_buy
            ''')
            number_result= cursor.fetchall()
            ##
            cursor.execute('''
                SELECT 
                strftime('%Y/%m/%d', REPLACE(buy_date, '/', '-')) AS month_buy,
                SUM(quantity) as quantity
                FROM products
                WHERE user_id = ? AND expire_date < ?
                GROUP BY month_buy;
                ''',(id_user,date_now))
            expire_result= cursor.fetchall()
            ##
            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-'))  AS month_buy, name, SUM(quantity) as quantity
                FROM products_log 
                GROUP BY month_buy,name
                ORDER BY month_buy,quantity DESC
                ''')
            repeated_result= cursor.fetchall()
            # اتمام محصول
            cursor.execute('''
                SELECT strftime('%Y/%m/%d', REPLACE(buy_date, '/', '-'))  AS month, COUNT(quantity) as quantity 
                FROM products WHERE user_id = ? AND quantity < 0 
                GROUP BY month
            ''', (id_user,))
            empty_result = cursor.fetchall()

            # پردازش نتایج
            buy_stats_offline_day = {
                "buy_items": 0,
                "low_items": 0,
                "repeated_items": "خالی",
                "expired_items": 0}
            
            product_counter = {}

            # تعداد خرید و اتمام محصول
            for result_set in (number_result, empty_result):
                for row in result_set:
                    try:
                        date_str, quantity = row
                        if "-" in date_str:
                            g_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        elif "/" in date_str:
                            g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        else:
                            raise ValueError(f"Unknown date format: {date_str}")

                        # 👇 اینجا تاریخ شمسی رو بساز
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_year = j_date.year
                        j_month = j_date.month
                        j_day = j_date.day

                        key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"

                        if self.selected_date and self.selected_date == key:
                            if result_set is number_result:
                                buy_stats_offline_day["buy_items"] += int(quantity)
                            elif result_set is empty_result:
                                buy_stats_offline_day["low_items"] += int(quantity)

                    except Exception as e:
                        print(f"⚠️ error in quantity convert: {e} → {row}")


            # تاریخ گذشته
            for row in expire_result:
                try:
                    date_str, quantity = row
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    j_day= j_date.day
                    key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست

                    if self.selected_date and self.selected_date == key:
                        buy_stats_offline_day["expired_items"] += int(quantity)

                except Exception as e:
                    print(f"⚠️ error in expired convert: {e} → {row}")

            # تکراری‌ترین خرید
            for row in repeated_result:
                try:
                    date_str, name, quantity = row
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    j_year = j_date.year
                    j_day= j_date.day
                    key = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"  # درست

                    if self.selected_date and self.selected_date == key:
                        product_counter[name] = product_counter.get(name, 0) + int(quantity)
                except Exception as e:
                    print(f"⚠️ error in repeated convert: {e} → {row}")

            if product_counter:
                best_item = max(product_counter, key=product_counter.get)
                buy_stats_offline_day["repeated_items"] = best_item

            print(f"📦 ماهانه buy_stats → {buy_stats_offline_day}")
            self.day_buy_signal.emit(buy_stats_offline_day)

        except pymysql.Error as e:
            print(f"{e} : db online table error")
     ############today
    ##
    def excecute_buy_table_offline_month(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor = conn_sq.cursor()
            cursor.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor.fetchone()
            id_user = rest_id[0]

            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-'))  AS month_date,
                    name, big_sub,big_category,final_total
                FROM products_log
            ''')
            buy_info = cursor.fetchall()

            row_data = {}
            row_index = 0

            for row in buy_info:
                date_str, product_name, big_sub, big_category, total,  = row
                try:
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    key_month = f"{j_year:04d}/{j_month:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_month and self.selected_month == key_month:
                        row_data[row_index] = [product_name, big_sub, big_category, total]
                        row_index += 1

                except Exception as e:
                    print(f" table month problem for buying: {e} → {row}")
               
                print(f'{row_data} : offline buy table month info')
                self.buy_table_data.emit(row_data)
                


        except sqlite3.Error as e:
            print(f"{e} : db oflline table error")
    ##
    def excecute_buy_table_day_offline(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db found!")
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor = conn_sq.cursor()
            cursor.execute('SELECT id FROM users LIMIT 1;')
            rest_id = cursor.fetchone()
            id_user = rest_id[0]

            cursor.execute('''
                SELECT strftime('%Y-%m-%d', REPLACE(update_at, '/', '-'))  AS month_date,
                name, big_sub, big_category, final_total
                FROM products_log
            ''')
            buy_info = cursor.fetchall()

            row_datas = {}
            row_index = 0

            for row in buy_info:
                date_str, product_name, big_sub, big_category, total = row
                try:
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day:02d}"

                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_date and self.selected_date == key_day:
                        row_datas[row_index] = [product_name, big_sub, big_category, total]
                        row_index += 1

                except Exception as e:
                    print(f" day table problem: {e} → {row}")
            ### sending signal
            self.buy_table_data_day.emit(row_datas)


        except sqlite3.Error as e:
            print(f"{e} : db offline day table error")

    ##
    def offline_sale_table_day(self):
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline month sale db found")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_result = cursor.fetchone()
            id_user = id_result[0]
            cursor.execute(''' 
                SELECT strftime('%Y/%m/%d', REPLACE(sale_date, '/', '-')) AS month_sale,
                product_name,quantity,product_type,total,sale_type
                FROM sale_factor
                WHERE user_id = ?
                GROUP BY month_sale, product_name;
            ''',(id_user,))
            offline_result_table= cursor.fetchall()
            
            row_data= {}
            row_index= 0

            for row in offline_result_table:
                date_str, product_name,quantity,product_type,total,sale_type= row
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_year = j_date.year
                    j_month = j_date.month
                    j_day= j_date.day
                    key_day = f"{j_year:04d}/{j_month:02d}/{j_day}"
                    # فقط اگر ماه مطابق بود ادامه ده
                    if self.selected_date and self.selected_date == key_day:
                        if sale_type == "عمده":
                            # واکشی big_quantity برای این محصول
                            cursor.execute('''
                                SELECT big_quantity FROM products
                                WHERE user_id = ? AND name = ?
                                LIMIT 1
                            ''', (id_user, product_name))
                            bg_result = cursor.fetchone()
                            if bg_result and bg_result[0] > 0:
                                big_quantity = bg_result[0]
                                best_quantity = quantity / big_quantity
                            else:
                                print(f"⚠️ مقدار big_quantity برای '{product_name}' یافت نشد یا صفر است.")
                                best_quantity = quantity  # fallback
                        else:
                            best_quantity = quantity

                        row_data[row_index] = [product_name, best_quantity, product_type, total]
                        row_index += 1

                except Exception as e:
                    print(f"⚠️ db tableخطا در پردازش ردیف فروش: {e} → {row}")
            ##
            print(f"row data day signal table :{row_data}")
            self.sale_table_data_day.emit(row_data)
        except pymysql.Error as e:
            print(f"{e} : db online table error")