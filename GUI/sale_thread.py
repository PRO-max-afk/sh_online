from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import jdatetime
from datetime import datetime
import datetime
from message_b import MessageBox
import os
import requests
from db_connection import Connection


class SaleThread(QThread):
    online_sale = pyqtSignal(float)
    ofline_sale = pyqtSignal(float)
    total_sale = pyqtSignal(float)
    monthly_sale = pyqtSignal(list,float)  # لیستی از فروش ماهانه ۱۲ ماه
    monthly_sa = pyqtSignal(dict)
    ###
    weekly_sale= pyqtSignal(list,float)
    week_sales= pyqtSignal(float)
    weekly_sa= pyqtSignal(dict)
    ##
    daily_sale = pyqtSignal(list, float)
    daily_sa = pyqtSignal(dict)
 

    def __init__(self, selected_month=None, selected_week=None,selected_day=None):
        super().__init__()
        self.selected_month = selected_month  # ← ماه انتخاب‌شده، مثلاً "2025/06"
        self.selected_week= selected_week
        self.selected_day= selected_day
        

    def run(self):
            if self.selected_month:
                self.month_sale_offline_only()
                self.day_sale_offline_only()
                self.week_sale_offline_only()
            elif self.selected_week:
                today_j = jdatetime.date.today()
                self.selected_month = f"{today_j.year:04d}/{today_j.month:02d}"
                self.week_sale_offline_only()

            
    
    ###
    def parse_date_safe(self,date_str):
        """
        تبدیل رشته تاریخ (ممکن است با یا بدون زمان باشد) به datetime.date
        """
        if isinstance(date_str, datetime.date):
            return date_str
        if isinstance(date_str, datetime.datetime):
            return date_str.date()

        date_str = str(date_str).strip()
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"فرمت تاریخ ناشناخته: {date_str}")
    ##
    def month_sale(self):
        db_data= Connection().get_connection()
        if not db_data:
            print("server errors😣")
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
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
            cursor = db_data.cursor()

            # 🔹 آفلاین (بدون استفاده از پارامتر اشتباه)
            cursor.execute('''
                SELECT DATE_FORMAT(sale_date, '%%Y/%%m/%%d') AS month, SUM(total),SUM(profit)
                FROM sale_factor
                WHERE user_id = %s
                GROUP BY month
            ''', (id_user,))
            of_result = cursor.fetchall()

            total = 0
            total_f= 0
            if of_result:
                for row in of_result:
                    total += float(row[1]) if row[1] else 0
                    total_f += float(row[2]) if row[2] else 0
                self.ofline_sale.emit(total)
                print(f"✅ مجموع فروش آفلاین: {total}")
            else:
                print("⚠️ هیچ فروش آفلاین یافت نشد")

            # 🔹 آنلاین
            cursor.execute('''
                SELECT DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS month, SUM(price)
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
            
            
            # 🔹 ساخت لیست فروش هر ماه شمسی
            monthly_totals = [0] * 12

            # ← آفلاین‌ها (تاریخ مثل "2025/07/05")
            for row in of_result:
                date_str = row[0]
                amount = float(row[1]) if row[1] else 0
                try:
                    year, month, day = map(int, date_str.split("/"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    monthly_totals[j_month - 1] += amount
                    print(f"[آفلاین] {date_str} → {j_date} (ماه شمسی: {j_month}) → +{amount}")
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {date_str}")

            # ← آنلاین‌ها (تاریخ مثل "2025-07-05")
            for row in on_result:
                date_str = row[0]
                amount = float(row[1]) if row[1] else 0
                try:
                    year, month, day = map(int, date_str.split("-"))
                    g_date = datetime.date(year, month, day)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    monthly_totals[j_month - 1] += amount
                    print(f"[آنلاین] {date_str} → {j_date} (ماه شمسی: {j_month}) → +{amount}")
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آنلاین: {e} → {date_str}")

            # ارسال فروش ماهانه
            self.monthly_sale.emit(monthly_totals,final_total)
            print(monthly_totals)
            
            
            # selected_month مثل "1404/04"
            if self.selected_month:
                try:
                    # استخراج سال و ماه جلالی از selected_month
                    j_year, j_month = map(int, self.selected_month.split("/"))
                    target_prefix = f"{j_year:04d}/{j_month:02d}"
                except Exception as e:
                    print(f"❌ خطا در پردازش selected_month: {self.selected_month} → {e}")
                    return  # از ادامه پردازش جلوگیری کن

                # مقدار اولیه برای هر نوع فروش
                selected_stats = {
                    "offline": 0,
                    "online": 0,
                    "mobile": 0,
                    "total": 0,
                    "profit": 0
                }

                # 🔹 محاسبه فروش آفلاین
                for row in of_result:
                    date_str = row[0]  # مثال: "2025/06/24"
                    try:
                        year, month, day = map(int, date_str.split("/"))
                        g_date = datetime.date(year, month, day)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_prefix = f"{j_date.year:04d}/{j_date.month:02d}"
                        if j_prefix == target_prefix:
                            selected_stats["offline"] += float(row[1]) if row[1] else 0
                            selected_stats["profit"] += float(row[2]) if row[2] else 0
                    except Exception as e:
                        print(f"⚠️ خطا در آمار آفلاین: {e} → {date_str}")

                # 🔹 محاسبه فروش آنلاین
                for row in on_result:
                    date_str = row[0]  # مثال: "2025-06-24"
                    try:
                        year, month, day = map(int, date_str.split("-"))
                        g_date = datetime.date(year, month, day)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        j_prefix = f"{j_date.year:04d}/{j_date.month:02d}"
                        if j_prefix == target_prefix:
                            selected_stats["online"] += float(row[1]) if row[1] else 0
                    except Exception as e:
                        print(f"⚠️ خطا در آمار آنلاین: {e} → {date_str}")

                # 🔹 سایر آمار (در صورت نیاز - مثل mobile, total, profit)
                selected_stats["total"] = selected_stats["offline"] + selected_stats["online"]

                # در نهایت ارسال نتیجه
                self.monthly_sa.emit(selected_stats)



        except pymysql.Error as e:
            print(f'{e}: خطا در اتصال یا اجرای کوئری به پایگاه داده')
    #
    def month_sale_offline_only(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1;")
            result = cursor.fetchone()
            id_user = result[0]

            # 📌 خواندن سفارشات (آنلاین)
            cursor.execute('''
                SELECT created_at, price, profit
                FROM orders 
                WHERE user_id=?
            ''', (id_user,))
            order_result = cursor.fetchall()

            # 📌 خواندن فاکتورها (آفلاین)
            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            results = cursor.fetchall()

            total = 0
            total_profit = 0
            total_online = 0
            total_offline = 0
            monthly_totals = [0] * 12

            # -------------------
            # 🟦 بخش آنلاین (orders)
            # -------------------
            for row in order_result:
                order_date, price, profit = row
                try:
                    g_dates = self.parse_date_safe(order_date)
                    j_dates = jdatetime.date.fromgregorian(date=g_dates)
                    j_months = j_dates.month

                    quantity = float(price) if price else 0
                    profits = float(profit) if profit else 0

                    monthly_totals[j_months - 1] += quantity
                    total_online += quantity
                    total += quantity
                    total_profit += profits
                except Exception as e:
                    print(f'⚠️ error in order db: {e} → {row}')



            # -------------------
            # 🟩 بخش آفلاین (sale_factor)
            # -------------------
            for row in results:
                date_str, value, profit = row
                try:
                    g_date = self.parse_date_safe(date_str)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month

                    amount = float(value) if value else 0
                    profit = float(profit) if profit else 0

                    monthly_totals[j_month - 1] += amount
                    total_offline += amount
                    total += amount
                    total_profit += profit
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {row}")

            # -------------------
            # 📤 ارسال سیگنال‌ها
            # -------------------
            self.ofline_sale.emit(total_offline)
            self.online_sale.emit(total_online)
            self.total_sale.emit(total)
            self.monthly_sale.emit(monthly_totals, total)

            # -------------------
            # 🔎 محاسبه ماه انتخاب‌شده
            # -------------------
            if self.selected_month:
                try:
                    j_year, j_month = map(int, self.selected_month.split("/"))
                    target_prefix = f"{j_year:04d}/{j_month:02d}"
                except:
                    return

                selected_total = 0
                selected_profit = 0
                selected_online = 0
                selected_offline = 0

                # آفلاین
                for row in results:
                    date_str, value, profit = row
                    try:
                        g_date = self.parse_date_safe(date_str)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        prefix = f"{j_date.year:04d}/{j_date.month:02d}"
                        if prefix == target_prefix:
                            selected_offline += float(value) if value else 0
                            selected_total += float(value) if value else 0
                            selected_profit += float(profit) if profit else 0
                    except:
                        continue

                # آنلاین
                for row in order_result:
                    order_date, price, profit = row
                    try:
                        g_date = self.parse_date_safe(order_date)
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        prefix = f"{j_date.year:04d}/{j_date.month:02d}"
                        if prefix == target_prefix:
                            selected_online += float(price) if price else 0
                            selected_total += float(price) if price else 0
                            selected_profit += float(profit) if profit else 0
                    except:
                        continue

                self.monthly_sa.emit({
                    "offline": selected_offline,
                    "online": selected_online,
                    "total": selected_total,
                    "profit": selected_profit
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")

    ##
    def week_sale_off(self):
        db_data = Connection().get_connection()
        if not db_data:
            print("server errors😣")
            return

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
            cursor_sq.execute("select id from users LIMIT 1;")
            result = cursor_sq.fetchone()
            id_user = result[0]
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
            return

        try:
            
            cursor = db_data.cursor()

            # دریافت داده‌های آفلاین
            cursor.execute('''
                SELECT sale_date, total,profit
                FROM sale_factor
                WHERE user_id = %s
            ''', (id_user,))
            of_result = cursor.fetchall()

            # دریافت داده‌های آنلاین
            cursor.execute('''
                SELECT created_at, price
                FROM orders
                WHERE approve = 1 AND user_id = %s
            ''', (id_user,))
            on_result = cursor.fetchall()

            # بررسی selected_month
            if not self.selected_month:
                print("ماه انتخابی مشخص نیست!")
                return
            try:
                j_year, j_month = map(int, self.selected_month.split("/"))
            except Exception as e:
                print(f"❌ selected_month نامعتبر: {self.selected_month} → {e}")
                return

            # آرایه‌ها برای مجموع هفته‌ها
            week_totals = [0, 0, 0, 0]
            offline_week = [0, 0, 0, 0]
            profit_week= [0, 0, 0, 0]
            online_week = [0, 0, 0, 0]

            def handle_rows(rows, is_online=False):
                for row in rows:
                    try:
                        # برای sale_factor (آفلاین) سه ستون داریم: sale_date, total, profit
                        if not is_online:
                            date_str, value, profit_val = row
                        else:
                            date_str, value = row
                            profit_val = 0  # آنلاین profit ندارد در این حالت

                        date_str = str(date_str)
                        if isinstance(date_str, datetime.datetime):
                            g_date = date_str.date()
                        else:
                            date_str = str(date_str)
                            try:
                                g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                            except ValueError:
                                try:
                                    g_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
                                except ValueError:
                                    g_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        if j_date.year == j_year and j_date.month == j_month:
                            week_index = (j_date.day - 1) // 7
                            if 0 <= week_index < 4:
                                amount = float(value) if value else 0
                                week_totals[week_index] += amount

                                if is_online:
                                    online_week[week_index] += amount
                                else:
                                    offline_week[week_index] += amount
                                    profit = float(profit_val) if profit_val else 0
                                    profit_week[week_index] += profit

                                print(f"{'[آنلاین]' if is_online else '[آفلاین]'} {j_date} → هفته {week_index + 1} → +{amount} (سود: {profit_val if not is_online else '-'})")
                    except Exception as e:
                        print(f"⚠️ خطا در تاریخ {'آنلاین' if is_online else 'آفلاین'}: {e} → {row}")


            # پردازش داده‌ها
            handle_rows(of_result, is_online=False)
            handle_rows(on_result, is_online=True)

            # اگر هفته خاص انتخاب شده
            if self.selected_week:
                try:
                    week_num = int(self.selected_week.replace("هفته ", "")) - 1
                    if 0 <= week_num < 4:
                        filtered_total = week_totals[week_num]
                        print(f"🔹 فروش هفته {week_num + 1}: {filtered_total}")

                        self.weekly_sa.emit({
                            "offlines": offline_week[week_num] if offline_week[week_num] > 0 else 0,
                            "onlines": online_week[week_num] if online_week[week_num] > 0 else 0,
                            "mobiles": 0,
                            "totals": filtered_total,
                            "profits": profit_week[week_num] if profit_week[week_num] > 0 else 0
                        })

                        return
                except Exception as e:
                    print(f"❌ selected_week نامعتبر: {self.selected_week} → {e}")

            # اگر هفته خاص انتخاب نشده، کل ۴ هفته را ارسال کن
            total_sum = sum(week_totals)
            print("📊 فروش هفته‌وار ۴ هفته‌ای:", week_totals)
            self.weekly_sale.emit(week_totals, total_sum)
            self.week_sales.emit(total_sum)
            self.weekly_sa.emit({
                "offlines": sum(offline_week) if sum(offline_week) > 0 else 0,
                "onlines": sum(online_week) if sum(online_week) > 0 else 0,
                "mobiles": 0,
                "totals": total_sum,
                "profits": sum(profit_week)
            })


        except pymysql.Error as e:
            print(f'{e}: خطا در اتصال یا اجرای کوئری به پایگاه داده')
    #
    def week_sale_offline_only(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1;")
            id_user = cursor.fetchone()[0]

            # 🟩 آفلاین
            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            results = cursor.fetchall()

            # 🟦 آنلاین
            cursor.execute('''
                SELECT created_at, price, profit
                FROM orders
                WHERE user_id = ?
            ''', (id_user,))
            order_result = cursor.fetchall()

            if not self.selected_month:
                print("ماه انتخابی مشخص نیست!")
                return

            j_year, j_month = map(int, self.selected_month.split("/"))

            week_totals = [0, 0, 0, 0]
            offline_week = [0, 0, 0, 0]
            online_week = [0, 0, 0, 0]
            profit_week = [0, 0, 0, 0]

            # آفلاین
            for row in results:
                try:
                    date_str, value, profit = row
                    g_date = self.parse_date_safe(date_str)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    if j_date.year == j_year and j_date.month == j_month:
                        week_index = (j_date.day - 1) // 7
                        if 0 <= week_index < 4:
                            amount = float(value) if value else 0
                            profit = float(profit) if profit else 0
                            week_totals[week_index] += amount
                            offline_week[week_index] += amount
                            profit_week[week_index] += profit
                except:
                    continue

            # آنلاین
            for row in order_result:
                try:
                    created_at, price, profit = row
                    g_date = self.parse_date_safe(created_at)
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    if j_date.year == j_year and j_date.month == j_month:
                        week_index = (j_date.day - 1) // 7
                        if 0 <= week_index < 4:
                            amount = float(price) if price else 0
                            profit = float(profit) if profit else 0
                            week_totals[week_index] += amount
                            online_week[week_index] += amount
                            profit_week[week_index] += profit
                except Exception as e:
                    print(f"⚠️ خطا در تاریخ آنلاین: {e} → {row}")


            if self.selected_week:
                week_num = int(self.selected_week.replace("هفته ", "")) - 1
                total_w = week_totals[week_num]
                self.weekly_sale.emit(week_totals, sum(week_totals))
                self.weekly_sa.emit({
                    "offlines": offline_week[week_num],
                    "onlines": online_week[week_num],
                    "totals": total_w,
                    "profits": profit_week[week_num]
                })
            else:
                self.weekly_sale.emit(week_totals, sum(week_totals))
                self.week_sales.emit(sum(week_totals))
                self.weekly_sa.emit({
                    "offlines": sum(offline_week),
                    "onlines": sum(online_week),
                    "totals": sum(week_totals),
                    "profits": sum(profit_week)
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")


    ##
    def day_off(self):
        db_data = Connection().get_connection()
        if not db_data:
            print("server errors😣")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users LIMIT 1;")
            result = cursor_sq.fetchone()
            id_user = result[0]
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
            return

        try:
            cursor = db_data.cursor()

            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = %s
            ''', (id_user,))
            of_result = cursor.fetchall()

            cursor.execute('''
                SELECT created_at, price
                FROM orders
                WHERE approve = 1 AND user_id = %s
            ''', (id_user,))
            on_result = cursor.fetchall()

            days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
            day_totals = {day: 0 for day in days}
            offline_day = {day: 0 for day in days}
            online_day = {day: 0 for day in days}
            profit_day = {day: 0 for day in days}

            today = jdatetime.date.today()

            def handle_rows(rows, is_online=False):
                for row in rows:
                    try:
                        # آفلاین شامل ۳ مقدار است
                        if not is_online:
                            date_str, value, profit_val = row
                        else:
                            date_str, value = row
                            profit_val = 0

                        date_str = str(date_str)
                        if "/" in date_str:
                            g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        else:
                            g_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        # فقط اگر در هفته جاری شمسی باشد، پردازش کن
                        start_of_week = today - jdatetime.timedelta(days=today.weekday())  # شنبه این هفته
                        end_of_week = start_of_week + jdatetime.timedelta(days=6)          # جمعه این هفته
                        if not (start_of_week <= j_date <= end_of_week):
                            continue


                        weekday_index = j_date.weekday()
                        weekday_name = days[weekday_index]
                        amount = float(value) if value else 0
                        profit = float(profit_val) if profit_val else 0

                        day_totals[weekday_name] += amount
                        if is_online:
                            online_day[weekday_name] += amount
                        else:
                            offline_day[weekday_name] += amount
                            profit_day[weekday_name] += profit

                        print(f"{'[آنلاین]' if is_online else '[آفلاین]'} {j_date} → {weekday_name} → +{amount} (سود: {profit})")
                    except Exception as e:
                        print(f"⚠️ خطا در تبدیل تاریخ: {e} → {row}")

            handle_rows(of_result, is_online=False)
            handle_rows(on_result, is_online=True)

            if self.selected_day and self.selected_day in days:
                value = day_totals[self.selected_day]
                index = days.index(self.selected_day)
                sales_list = [0] * 7
                sales_list[index] = value

                self.daily_sale.emit(sales_list, value)
                self.daily_sa.emit({
                    "offliness": offline_day[self.selected_day],
                    "onliness": online_day[self.selected_day],
                    "mobiless": 0,
                    "totalss": value,
                    "profitss": profit_day[self.selected_day]
                })
                return

            ordered_values = [day_totals[day] for day in days]
            total_sum = sum(ordered_values)
            total_profit = sum(profit_day.values())

            print("📊 فروش روزانه ۷ روز اخیر:")
            for d in days:
                print(f"{d}: {day_totals[d]} (سود: {profit_day[d]})")

            self.daily_sale.emit(ordered_values, total_sum)
            self.daily_sa.emit({
                "offliness": sum(offline_day.values()),
                "onliness": sum(online_day.values()),
                "mobiless": 0,
                "totalss": total_sum,
                "profitss": total_profit
            })

        except pymysql.Error as e:
            print(f"{e}: خطا در اتصال یا اجرای کوئری به پایگاه داده")
    ##
    def day_sale_offline_only(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users LIMIT 1;")
            result = cursor_sq.fetchone()
            if not result:
                print("❌ هیچ کاربری یافت نشد")
                return
            id_user = result[0]
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
            return

        try:
            cursor_sq.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            of_result = cursor_sq.fetchall()

            cursor_sq.execute('''
                SELECT created_at, price, profit
                FROM orders
                WHERE user_id = ?
            ''', (id_user,))
            on_result = cursor_sq.fetchall()

            days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
            day_totals = {day: 0 for day in days}
            offline_day = {day: 0 for day in days}
            online_day = {day: 0 for day in days}
            profit_day = {day: 0 for day in days}

            today = jdatetime.date.today()

            def handle_rows(rows, is_online=False):
                for row in rows:
                    try:
                        if not is_online:
                            date_str, value, profit_val = row
                        else:
                            # اگر ستون profit در orders نیست، مقدار صفر بده
                            if len(row) == 3:
                                date_str, value, profit_val = row
                            else:
                                date_str, value = row
                                profit_val = 0

                        g_date = self.parse_date_safe(str(date_str))
                        j_date = jdatetime.date.fromgregorian(date=g_date)

                        start_of_week = today - jdatetime.timedelta(days=today.weekday())
                        end_of_week = start_of_week + jdatetime.timedelta(days=6)
                        if not (start_of_week <= j_date <= end_of_week):
                            continue

                        weekday_name = days[j_date.weekday()]
                        amount = float(value) if value else 0
                        profit = float(profit_val) if profit_val else 0

                        day_totals[weekday_name] += amount
                        if is_online:
                            online_day[weekday_name] += amount
                            profit_day[weekday_name] += profit
                        else:
                            offline_day[weekday_name] += amount
                            profit_day[weekday_name] += profit

                        print(f"{'[آنلاین]' if is_online else '[آفلاین]'} {j_date} → {weekday_name} → +{amount} (سود: {profit})")
                    except Exception as e:
                        print(f"⚠️ خطا در تبدیل تاریخ: {e} → {row}")

            handle_rows(of_result, is_online=False)
            handle_rows(on_result, is_online=True)

            if self.selected_day and self.selected_day in days:
                value = day_totals[self.selected_day]
                index = days.index(self.selected_day)
                sales_list = [0] * 7
                sales_list[index] = value

                self.daily_sale.emit(sales_list, value)
                self.daily_sa.emit({
                    "offliness": offline_day[self.selected_day],
                    "onliness": online_day[self.selected_day],
                    "totalss": value,
                    "profitss": profit_day[self.selected_day]
                })
                return

            ordered_values = [day_totals[day] for day in days]
            total_sum = sum(ordered_values)
            total_profit = sum(profit_day.values())

            print("📊 فروش روزانه ۷ روز اخیر (آنلاین + آفلاین):")
            for d in days:
                print(f"{d}: {day_totals[d]} (سود: {profit_day[d]})")

            # ✅ شرط روز انتخابی
            if self.selected_day and self.selected_day in days:
                value = day_totals.get(self.selected_day, 0)  # اگر نبود 0
                profit_val = profit_day.get(self.selected_day, 0)
                index = days.index(self.selected_day)

                sales_list = [0] * 7
                sales_list[index] = value

                self.daily_sale.emit(sales_list, value)
                self.daily_sa.emit({
                    "offliness": offline_day.get(self.selected_day, 0),
                    "onliness": online_day.get(self.selected_day, 0),
                    "totalss": value,
                    "profitss": profit_val
                })
            else:
                # نمایش همه روزها
                self.daily_sale.emit(ordered_values, total_sum)
                self.daily_sa.emit({
                    "offliness": sum(offline_day.values()),
                    "onliness": sum(online_day.values()),
                    "totalss": total_sum,
                    "profitss": total_profit
                })


        except sqlite3.Error as e:
            print(f"{e}: خطا در اجرای کوئری دیتابیس آفلاین")

