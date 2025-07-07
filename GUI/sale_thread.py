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
from message_b import MessageBox
import os
import requests


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
        if self.get_db_config():
            # اول ماهانه، اگر تنظیم شده
            if self.selected_month:
                self.month_sale()
                self.day_off()
                self.week_sale_off()
            # بعد هفته‌ای، اگر تنظیم شده
            elif self.selected_week:
                self.week_sale_off()
        else:
            if self.selected_week:
                self.week_sale_offline_only()
            elif self.selected_month:
                self.month_sale_offline_only()
                self.day_sale_offline_only()
            
    
    ###
    def month_sale(self):
        db_data= self.get_db_config()
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
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

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

            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            results = cursor.fetchall()

            total = 0
            total_profit = 0
            monthly_totals = [0] * 12

            for row in results:
                date_str, value, profit = row
                try:
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    amount = float(value) if value else 0
                    profit = float(profit) if profit else 0
                    monthly_totals[j_month - 1] += amount
                    total += amount
                    total_profit += profit
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {row}")

            self.ofline_sale.emit(total)
            self.online_sale.emit(0)  # فروش آنلاین صفر
            self.total_sale.emit(total)
            self.monthly_sale.emit(monthly_totals, total)

            if self.selected_month:
                try:
                    j_year, j_month = map(int, self.selected_month.split("/"))
                    target_prefix = f"{j_year:04d}/{j_month:02d}"
                except:
                    return

                selected_total = 0
                selected_profit = 0

                for row in results:
                    date_str, value, profit = row
                    try:
                        g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        prefix = f"{j_date.year:04d}/{j_date.month:02d}"
                        if prefix == target_prefix:
                            selected_total += float(value) if value else 0
                            selected_profit += float(profit) if profit else 0
                    except:
                        continue

                self.monthly_sa.emit({
                    "offline": selected_total,
                    "online": 0,
                    "mobile": 0,
                    "total": selected_total,
                    "profit": selected_profit
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")
    ##
    def week_sale_off(self):
        db_data = self.get_db_config()
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
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

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
                        if "/" in date_str:
                            g_date = datetime.datetime.strptime(str(date_str), "%Y/%m/%d").date()
                        else:
                            g_date = datetime.datetime.strptime(str(date_str), "%Y-%m-%d").date()

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

            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            results = cursor.fetchall()

            if not self.selected_month:
                print("ماه انتخابی مشخص نیست!")
                return

            j_year, j_month = map(int, self.selected_month.split("/"))

            week_totals = [0, 0, 0, 0]
            offline_week = [0, 0, 0, 0]
            profit_week = [0, 0, 0, 0]

            for row in results:
                try:
                    date_str, value, profit = row
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
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

            if self.selected_week:
                week_num = int(self.selected_week.replace("هفته ", "")) - 1
                total_w = week_totals[week_num]
                self.weekly_sale.emit(week_totals, sum(week_totals))
                self.weekly_sa.emit({
                    "offlines": offline_week[week_num],
                    "onlines": 0,
                    "mobiles": 0,
                    "totals": total_w,
                    "profits": profit_week[week_num]
                })
            else:
                self.weekly_sale.emit(week_totals, sum(week_totals))
                self.week_sales.emit(sum(week_totals))
                self.weekly_sa.emit({
                    "offlines": sum(offline_week),
                    "onlines": 0,
                    "mobiles": 0,
                    "totals": sum(week_totals),
                    "profits": sum(profit_week)
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")

    ##
    def day_off(self):
        db_data = self.get_db_config()
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
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

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
                        # فقط اگر اختلاف کمتر از 7 روز است، پردازش کن
                        delta_days = (today.togregorian() - j_date.togregorian()).days
                        if delta_days < 0 or delta_days >= 7:
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
    #
    def day_sale_offline_only(self):
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

            cursor.execute('''
                SELECT sale_date, total, profit
                FROM sale_factor
                WHERE user_id = ?
            ''', (id_user,))
            results = cursor.fetchall()

            days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
            day_totals = {day: 0 for day in days}
            offline_day = {day: 0 for day in days}
            profit_day = {day: 0 for day in days}

            today = jdatetime.date.today()

            for row in results:
                try:
                    date_str, value, profit = row
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    delta_days = (today.togregorian() - j_date.togregorian()).days
                    if delta_days < 0 or delta_days >= 7:
                        continue

                    weekday_name = days[j_date.weekday()]
                    amount = float(value) if value else 0
                    profit = float(profit) if profit else 0
                    day_totals[weekday_name] += amount
                    offline_day[weekday_name] += amount
                    profit_day[weekday_name] += profit
                except:
                    continue

            if self.selected_day and self.selected_day in days:
                index = days.index(self.selected_day)
                value = day_totals[self.selected_day]
                sales_list = [0] * 7
                sales_list[index] = value

                self.daily_sale.emit(sales_list, value)
                self.daily_sa.emit({
                    "offliness": offline_day[self.selected_day],
                    "onliness": 0,
                    "mobiless": 0,
                    "totalss": value,
                    "profitss": profit_day[self.selected_day]
                })
            else:
                ordered_values = [day_totals[day] for day in days]
                self.daily_sale.emit(ordered_values, sum(ordered_values))
                self.daily_sa.emit({
                    "offliness": sum(offline_day.values()),
                    "onliness": 0,
                    "mobiless": 0,
                    "totalss": sum(day_totals.values()),
                    "profitss": sum(profit_day.values())
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")
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

