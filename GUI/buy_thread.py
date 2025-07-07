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


class BuyThread(QThread):
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
                self.month_buy()
                self.day_buy()
                self.week_buy()
        else:
            if self.selected_week:
                self.week_buy()
            elif self.selected_month:
                self.month_buy_offline_only()
                self.day_buy_offline()
    ##
    def get_user_id(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'sh_online.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1")
            return cursor.fetchone()[0]
        except:
            return None
    
    ###
    def month_buy(self):
        db_data = self.get_db_config()
        if not db_data:
            print("server errors😣")
            return

        # آدرس دیتابیس آفلاین
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        # گرفتن user_id از دیتابیس آفلاین
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
            # اتصال به دیتابیس آنلاین
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

            # دریافت خریدهای آنلاین
            cursor.execute('''
                SELECT DATE_FORMAT(buy_date, '%%Y/%%m/%%d') AS buy_date, SUM(total)
                FROM inventory_log
                WHERE user_id = %s and type_save= 'inventory'
                GROUP BY buy_date
            ''', (id_user,))
            on_result = cursor.fetchall()

            monthly_totals = [0] * 12
            total_online = 0
            total_offline = 0

            # پردازش مجموع کلی برای نمودار
            for row in on_result:
                date_str, value = row
                try:
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    value = float(value) if value else 0
                    total_online += value
                    monthly_totals[j_month - 1] += value
                except Exception as e:
                    print(f"خطا در تاریخ آنلاین → {e} → {row}")

            # ارسال سیگنال‌های عمومی
            self.ofline_sale.emit(total_offline)
            self.online_sale.emit(total_online)
            self.total_sale.emit(total_online + total_offline)
            self.monthly_sale.emit(monthly_totals, total_online + total_offline)

            # پردازش فقط زمانی که selected_month تنظیم شده باشد
            if self.selected_month:
                try:
                    j_year, j_month = map(int, self.selected_month.split("/"))
                except:
                    print("خطا در فرمت selected_month")
                    return

                # محاسبه ماه قبلی
                if j_month == 1:
                    past_month = 12
                    past_year = j_year - 1
                else:
                    past_month = j_month - 1
                    past_year = j_year

                # جمع کل برای هر ماه
                current_month_total = 0
                past_month_total = 0

                for row in on_result:
                    try:
                        date_str, value = row
                        g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        value = float(value) if value else 0

                        if j_date.year == j_year and j_date.month == j_month:
                            current_month_total += value
                        elif j_date.year == past_year and j_date.month == past_month:
                            past_month_total += value
                    except:
                        continue

                # درصد تغییر
                if past_month_total == 0:
                    percent_change = 100 if current_month_total > 0 else 0
                else:
                    percent_change = round(((current_month_total - past_month_total) / past_month_total) * 100, 2)

                total_month_result= current_month_total + past_month_total
                # ارسال فقط همان ماه و ماه قبل
                selected_stats = {
                    "current_month": current_month_total,
                    "past_month": past_month_total,
                    "percent": percent_change,
                    "total": total_month_result
                }
                self.monthly_sa.emit(selected_stats)

        except pymysql.Error as e:
            print(f"{e}: خطا در اتصال به پایگاه داده آنلاین")
    #
    def month_buy_offline_only(self):
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
                SELECT buy_date, total
                FROM products
                WHERE user_id = ? AND type_save = 'sale'
            ''', (id_user,))
            results = cursor.fetchall()

            total = 0
            monthly_totals = [0] * 12

            # ابتدا مجموع کلی برای نمودار را محاسبه کن
            for row in results:
                date_str, value = row
                try:
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                    j_date = jdatetime.date.fromgregorian(date=g_date)
                    j_month = j_date.month
                    amount = float(value) if value else 0
                    monthly_totals[j_month - 1] += amount
                    total += amount
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ آفلاین: {e} → {row}")

            self.ofline_sale.emit(total)
            self.online_sale.emit(0)
            self.total_sale.emit(total)
            self.monthly_sale.emit(monthly_totals, total)

            # حالا پردازش ماه انتخاب‌شده
            if self.selected_month:
                try:
                    j_year, j_month = map(int, self.selected_month.split("/"))
                except:
                    print("❌ selected_month نامعتبر است")
                    return

                # محاسبه ماه قبل
                if j_month == 1:
                    past_month = 12
                    past_year = j_year - 1
                else:
                    past_month = j_month - 1
                    past_year = j_year

                current_month_total = 0
                past_month_total = 0

                for row in results:
                    date_str, value = row
                    try:
                        g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                        j_date = jdatetime.date.fromgregorian(date=g_date)
                        amount = float(value) if value else 0

                        if j_date.year == j_year and j_date.month == j_month:
                            current_month_total += amount
                        elif j_date.year == past_year and j_date.month == past_month:
                            past_month_total += amount
                    except:
                        continue

                # محاسبه درصد تغییر
                if past_month_total == 0:
                    percent_change = 100 if current_month_total > 0 else 0
                else:
                    percent_change = round(((current_month_total - past_month_total) / past_month_total) * 100, 2)

                # ارسال اطلاعات دقیق آفلاین
                self.monthly_sa.emit({
                    "current_month": current_month_total,
                    "past_month": past_month_total,
                    "percent": percent_change,
                    "total": current_month_total
                })

        except sqlite3.Error as e:
            print(f"❌ خطای دیتابیس آفلاین: {e}")

    ##
    def week_buy(self):
        user_id = self.get_user_id()
        if not user_id:
            print("❌ user_id یافت نشد.")
            return

        db_data = self.get_db_config()
        if not db_data:
            print("❌ تنظیمات اتصال دیتابیس یافت نشد.")
            return

        try:
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT buy_date, total 
                FROM inventory_log 
                WHERE user_id = %s AND type_save = 'inventory'
            """, (user_id,))
            rows = cursor.fetchall()

            try:
                j_year, j_month = map(int, self.selected_month.split("/"))
            except Exception as e:
                print(f"❌ selected_month نامعتبر است: {e}")
                return

            week_totals = [0, 0, 0, 0]
            print("📌 نمونه تاریخ‌ها از دیتابیس:")
            for r in rows[:5]:
                print(f"  📅 {r[0]} - 💵 {r[1]}")


            for buy_date, value in rows:
                try:
                    # بررسی نوع تاریخ
                    if isinstance(buy_date, str):
                        g_date = datetime.datetime.strptime(buy_date, "%Y/%m/%d").date()
                    elif isinstance(buy_date, datetime.date):
                        g_date = buy_date
                    elif isinstance(buy_date, datetime.datetime):
                        g_date = buy_date.date()
                    else:
                        print(f"⚠️ نوع تاریخ ناشناخته: {type(buy_date)} ← {buy_date}")
                        continue

                    # تبدیل به تاریخ شمسی
                    j_date = jdatetime.date.fromgregorian(date=g_date)

                    if j_date.year == j_year and j_date.month == j_month:
                        week_index = (j_date.day - 1) // 7
                        week_index = min(week_index, 3)
                        week_totals[week_index] += float(value) if value else 0

                except Exception as e:
                    print(f"⚠️ خطا در پردازش ردیف: {e} ← {buy_date}")
                    continue

            total = sum(week_totals)

            print("✅ اطلاعات خرید هفتگی:")
            for i, amount in enumerate(week_totals):
                print(f"هفته {i+1}: {amount:,.0f}")

            self.weekly_sale.emit(week_totals, total)
            self.week_sales.emit(total)
            self.weekly_sa.emit({
                "first": week_totals[0],
                "second": week_totals[1],
                "third": week_totals[2],
                "fourth": week_totals[3],
                "total_week": total
            })

        except pymysql.Error as e:
            print(f"{e}: ❌ خطا در اتصال به پایگاه داده آنلاین")


    #
    def week_buy_offline(self):
        user_id = self.get_user_id()
        if not user_id:
            return

        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'sh_online.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT buy_date, total FROM products WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

        j_year, j_month = map(int, self.selected_month.split("/"))
        week_totals = [0, 0, 0, 0]

        for date_str, value in rows:
            try:
                g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                j_date = jdatetime.date.fromgregorian(date=g_date)
                if j_date.year == j_year and j_date.month == j_month:
                    week_index = (j_date.day - 1) // 7
                    week_totals[week_index] += float(value)
            except:
                continue

        total = sum(week_totals)
        self.weekly_sale.emit(week_totals, total)
        self.week_sales.emit(total)
        self.weekly_sa.emit({
            "first": week_totals[0],
            "second": week_totals[1],
            "third": week_totals[2],
            "fourth": week_totals[3],
            "total_week": total
        })


    ##
    def day_buy(self):
        user_id = self.get_user_id()
        if not user_id:
            return

        db_data = self.get_db_config()
        if not db_data or not self.selected_month:
            return

        try:
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT buy_date, total 
                FROM inventory_log 
                WHERE user_id = %s AND type_save = 'inventory'
            """, (user_id,))
            rows = cursor.fetchall()
        except:
            return

        # استخراج سال و ماه شمسی از selected_month
        try:
            j_year, j_month = map(int, self.selected_month.split("/"))
        except Exception as e:
            print(f"❌ selected_month نامعتبر است: {e}")
            return

        # روزهای هفته به فارسی
        days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
        day_totals = {day: 0 for day in days}

        for date_str, value in rows:
            try:
                if isinstance(date_str, str):
                    g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                elif isinstance(date_str, datetime.datetime):
                    g_date = date_str.date()
                else:
                    g_date = date_str

                j_date = jdatetime.date.fromgregorian(date=g_date)

                # فقط اگر سال و ماه یکی بود
                if j_date.year == j_year and j_date.month == j_month:
                    weekday = days[j_date.weekday()]
                    day_totals[weekday] += float(value) if value else 0
            except Exception as e:
                print(f"⚠️ خطا در تبدیل تاریخ: {e}")
                continue

        ordered = [day_totals[day] for day in days]
        total = sum(ordered)

        self.daily_sale.emit(ordered, total)
        self.daily_sa.emit({
            "saturday": day_totals["شنبه"],
            "sunday": day_totals["یک‌شنبه"],
            "monday": day_totals["دوشنبه"],
            "tuesday": day_totals["سه‌شنبه"],
            "wednesday": day_totals["چهارشنبه"],
            "thursday": day_totals["پنج‌شنبه"],
            "friday": day_totals["جمعه"]
        })

    #   
    def day_buy_offline(self):
        user_id = self.get_user_id()
        if not user_id or not self.selected_month:
            return

        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'sh_online.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT buy_date, total FROM products WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

        try:
            j_year, j_month = map(int, self.selected_month.split("/"))
        except Exception as e:
            print(f"❌ selected_month آفلاین نامعتبر است: {e}")
            return

        days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
        day_totals = {day: 0 for day in days}

        for date_str, value in rows:
            try:
                g_date = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                j_date = jdatetime.date.fromgregorian(date=g_date)

                if j_date.year == j_year and j_date.month == j_month:
                    weekday = days[j_date.weekday()]
                    day_totals[weekday] += float(value)
            except:
                continue

        ordered = [day_totals[day] for day in days]
        total = sum(ordered)

        self.daily_sale.emit(ordered, total)
        self.daily_sa.emit({
            "saturday": day_totals["شنبه"],
            "sunday": day_totals["یک‌شنبه"],
            "monday": day_totals["دوشنبه"],
            "tuesday": day_totals["سه‌شنبه"],
            "wednesday": day_totals["چهارشنبه"],
            "thursday": day_totals["پنج‌شنبه"],
            "friday": day_totals["جمعه"]
        })

    
    
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

