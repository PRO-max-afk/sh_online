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

class YearThread(QThread):
    year_data= pyqtSignal(list)
    year_info= pyqtSignal(dict)
    year_chart= pyqtSignal(list)
    ##
    full_info= pyqtSignal(dict)
    chart_data= pyqtSignal(list)
    def __init__(self,selected_year=None):
        super().__init__()
        self.year_selected= selected_year
    ##
    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            if self.year_selected:
                self.year_datas()
            else:
                self.full_data()
                self.fetch_years_only()
        else:
            if self.year_selected:
                self.year_datas_offline()
            else:
                self.full_data_offline()
                self.fetch_years_only_offline()

        if hasattr(self, "available_years") and self.available_years:
            self.year_data.emit(sorted(self.available_years))
        else:
            print("📭 سالی برای نمایش وجود ندارد")
    ###
    def year_datas(self):
        from datetime import datetime
        import jdatetime

        data = Connection().get_connection()
        if not data:
            self.year_datas_offline()
            print("خطا در اتصال به سرور")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            MessageBox(text="مسیر دیتابیس آفلاین پیدا نشد", title="ناموفق", type="error").show()
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1')
            result = cursor_sq.fetchone()
            if not result:
                print("آیدی کاربر پیدا نشد")
                return
            id_user = result[0]
        except sqlite3.Error as e:
            print(f"{e} خطا در دیتابیس آفلاین")
            return

        try:
            
            cursor = data.cursor()

            years_inventories = set()
            cursor.execute("SELECT created_at FROM inventories WHERE user_id = %s", (id_user,))
            for (created_at,) in cursor.fetchall():
                if not created_at:
                    continue
                # تبدیل تاریخ میلادی به سال شمسی
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except ValueError:
                        continue
                sh_year = str(jdatetime.date.fromgregorian(date=miladi.date()).year)
                years_inventories.add(sh_year)

            # ---------- کنترل وجود سال‌ها ----------
            if not years_inventories:
                print("❌ هیچ سالی در جدول خرید (inventories) یافت نشد.")
                return

            # ---------- تصمیم‌گیری درباره year_selected ----------
            if not self.year_selected:  # کاربر سالی مشخص نکرده → آخرین سال
                self.year_selected = sorted(years_inventories)[-1]
            else:                       # کاربر سال را مشخص کرده → صحت‌سنجی
                self.year_selected = str(self.year_selected)
                if self.year_selected not in years_inventories:
                    print(f"⚠️ سال انتخاب‌شده ({self.year_selected}) در داده‌ها موجود نیست.")
                    return

            print(f"📌 سال انتخاب‌شده: {self.year_selected}")

            # ---------- محاسبه آمار آن سال ----------
            total_buy    = 0.0
            total_sale   = 0.0
            total_profit = 0.0
            total_harvest= 0
            total_barrow= 0

            # sale_factor
            cursor.execute("""
                SELECT created_at, total, profit
                FROM sale_factor
                WHERE user_id = %s
            """, (id_user,))
            for created_at, total, profit in cursor.fetchall():
                if not created_at:
                    continue
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except ValueError:
                        continue
                if str(jdatetime.date.fromgregorian(date=miladi.date()).year) == self.year_selected:
                    total_sale   += float(total)   if total   else 0
                    total_profit += float(profit)  if profit  else 0

            # orders
            cursor.execute("""
                SELECT created_at, price
                FROM orders
                WHERE user_id = %s
            """, (id_user,))
            for created_at, price in cursor.fetchall():
                if not created_at:
                    continue
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except ValueError:
                        continue
                if str(jdatetime.date.fromgregorian(date=miladi.date()).year) == self.year_selected:
                    total_sale += float(price) if price else 0

            # inventories
            cursor.execute("""
                SELECT created_at, final_total
                FROM inventories
                WHERE user_id = %s
            """, (id_user,))
            for created_at, total in cursor.fetchall():
                if not created_at:
                    continue
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except ValueError:
                        continue
                if str(jdatetime.date.fromgregorian(date=miladi.date()).year) == self.year_selected:
                    total_buy += float(total) if total else 0
            ##harvest
            cursor.execute("SELECT date, amount from harvest where user_id = %s",(id_user,))
            for date_str,amount in cursor.fetchall():
                if not date_str:
                    continue
                try:
                    year = date_str.strip().split('/') [0]
                    if year == self.year_selected:
                        total_harvest += float(amount) if amount else 0
                except Exception as e:
                    print("⛔ خطا در پردازش تاریخ harvest:", e)
            ##
            cursor.execute("SELECT date,amount FROM barrow WHERE user_id=%s",(id_user,))
            for date_b,amounts in cursor.fetchall():
                if not date_b:
                    continue
                try:
                    years= date_b.strip().split('/')[0]
                    if years== self.year_selected:
                        total_barrow += float(amounts) if amounts else 0
                except Exception as e:
                    print("⛔ خطا در پردازش تاریخ harvest:", e) 

            # ---------- خروجی در صورت نبود داده ----------
            if total_sale == total_buy == total_profit == total_harvest== total_barrow== 0:
                print("📭 اطلاعاتی برای این سال وجود ندارد.")
                return

            # ---------- ساخت دیکشنری نهایی ----------
            box_stats = {
                "total_buy"      : total_buy,
                "total_sale"     : total_sale,
                "profit"         : total_profit,
                "harvest"        : total_harvest,
                "total_barrow"   : total_barrow,
                "current_capital": total_buy - total_profit,
                "total_cush"     : total_sale,
            }
            self.year_info.emit(box_stats)

            chart_values = [
                box_stats["total_buy"],
                box_stats["total_sale"],
                box_stats["profit"],
                box_stats["harvest"],
                box_stats["total_barrow"],
                box_stats["current_capital"],
                box_stats["total_cush"],
            ]
            self.year_chart.emit(chart_values)

            print(f"✅ آمار سال {self.year_selected} با موفقیت بارگذاری شد.")

        except pymysql.Error as e:
            print(f"❌ خطا در دیتابیس آنلاین: {e}")
    ##
    def year_datas_offline(self):
        from datetime import datetime
        import jdatetime

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            MessageBox(text="📁 مسیر دیتابیس آفلاین یافت نشد", title="خطا", type="error").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1")
            result = cursor.fetchone()
            if not result:
                print("❌ آیدی کاربر در دیتابیس آفلاین یافت نشد.")
                return
            id_user = result[0]
        except Exception as e:
            print("❌ خطا در اتصال به دیتابیس آفلاین:", e)
            return

        # سال انتخاب‌شده را بررسی کن
        if not self.year_selected:
            print("⚠️ سالی انتخاب نشده برای پردازش آفلاین.")
            return

        total_buy = 0.0
        total_sale = 0.0
        total_profit = 0.0
        total_harvest = 0.0
        total_barrow = 0.0

        # sale_factor
        cursor.execute("SELECT created_at, total, profit FROM sale_factor WHERE user_id = ?", (id_user,))
        for created_at, total, profit in cursor.fetchall():
            if not created_at:
                continue
            try:
                miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                except:
                    continue
            if str(jdatetime.date.fromgregorian(date=miladi.date()).year) == self.year_selected:
                total_sale += float(total) if total else 0
                total_profit += float(profit) if profit else 0

        # products
        cursor.execute("SELECT create_at, final_total FROM products WHERE user_id = ?", (id_user,))
        for created_at, total in cursor.fetchall():
            if not created_at:
                continue
            try:
                miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                except:
                    continue
            if str(jdatetime.date.fromgregorian(date=miladi.date()).year) == self.year_selected:
                total_buy += float(total) if total else 0

        # harvest (تاریخ شمسی است)
        cursor.execute("SELECT date, amount FROM harvest WHERE user_id = ?", (id_user,))
        for date_str, amount in cursor.fetchall():
            if not date_str:
                continue
            year = date_str.strip().split("/")[0]
            if year == self.year_selected:
                total_harvest += float(amount) if amount else 0

        # barrow (تاریخ شمسی است)
        cursor.execute("SELECT date, amount FROM barrow WHERE user_id = ?", (id_user,))
        for date_str, amount in cursor.fetchall():
            if not date_str:
                continue
            year = date_str.strip().split("/")[0]
            if year == self.year_selected:
                total_barrow += float(amount) if amount else 0

        # ارسال داده
        if total_sale == total_buy == total_profit == total_harvest == total_barrow == 0:
            print("📭 اطلاعاتی برای این سال در دیتابیس آفلاین وجود ندارد.")
            return

        box_stats = {
            "total_buy": total_buy,
            "total_sale": total_sale,
            "profit": total_profit,
            "harvest": total_harvest,
            "total_barrow": total_barrow,
            "current_capital": total_buy - total_profit,
            "total_cush": total_sale,
        }

        self.year_info.emit(box_stats)

        chart_values = [
            box_stats["total_buy"],
            box_stats["total_sale"],
            box_stats["profit"],
            box_stats["harvest"],
            box_stats["total_barrow"],
            box_stats["current_capital"],
            box_stats["total_cush"],
        ]
        self.year_chart.emit(chart_values)
        print(f"📦 آمار آفلاین برای سال {self.year_selected} بارگذاری شد.")


    ###
    def full_data(self):
        data= Connection().get_connection()
        if not data:
            self.full_data_offline()
            print("خطا در اتصال به سرور")
            return
        ##ofline
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            MessageBox(text="مسیر دیتابیس آفلاین پیدا نشد",title="ناموفق",type="error").show()
            return
        ##offline db
        try:
            conn_sq= sqlite3.connect(db_path)
            cursor_sq= conn_sq.cursor()
            cursor_sq.execute('select id from users LIMIT 1')
            id_result= cursor_sq.fetchone()
            if id_result:
                id_user= id_result[0]
            else:
                print("آیدی پیدا نشد")
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
        
        ##online db
        try:
            cursor= data.cursor()
            
            cursor.execute('''
            SELECT SUM(total) FROM sale_factor WHERE user_id = %s
            ''',(id_user,))
            sale_result= cursor.fetchone()
            total_sale_f=0
            if sale_result:
                total_sale_f += float(sale_result[0]) if sale_result[0] else 0
                print(f" total sale off :{total_sale_f}")
            
            ##online sale
            cursor.execute('''
            SELECT SUM(price) FROM orders WHERE user_id = %s
            ''',(id_user,))
            online_result= cursor.fetchone()
            total_sale_on=0
            if sale_result:
                    total_sale_on += float(online_result[0]) if online_result[0] else 0
                    print(f" total sale online :{total_sale_on}")
            ##
            total_sale= total_sale_f + total_sale_on
            ##
            cursor.execute("SELECT SUM(final_total) FROM inventories WHERE user_id= %s",(id_user,))
            buy_result= cursor.fetchone()
            total_buy=0
            if buy_result:
                    total_buy += float(buy_result[0]) if buy_result[0] else 0
                    print(f"{total_buy} :  total buy")
            ###
            cursor.execute("SELECT SUM(profit) FROM sale_factor WHERE user_id= %s",(id_user,))
            profit_result= cursor.fetchone()
            total_profit=0
            if profit_result:
                    total_profit += float(profit_result[0]) if profit_result[0] else 0
                    print(f"{total_profit} :  total profit")
            ##
            cursor.execute("select SUM(amount) FROM harvest WHERE user_id= %s",(id_user,))
            har_result= cursor.fetchone()
            total_harvest=0
            if har_result:
                total_harvest += float(har_result[0]) if har_result[0] else 0
                print(f'{total_harvest} : total_harvest')

            cursor.execute("select SUM(ABS(amount)) from barrow WHERE user_id=%s",(id_user,))
            bar_total= cursor.fetchone()
            total_barrow=0
            if bar_total:
                total_barrow += float(bar_total[0]) if bar_total[0] else 0
                print(f"{total_barrow} : total barrow")

            ##
            total_cush= total_sale - total_harvest - total_barrow
            total_cush =  float(total_cush) if total_cush else 0
            ##
            box_stats={
                "total_buy" : total_buy,
                "total_sale" : total_sale,
                "profit" :total_profit,
                "harvest" : total_harvest,
                "total_barrow" : total_barrow,
                "current_capital" :total_cush + total_buy,
                "total_cush" : total_cush 
            }
            self.full_info.emit(box_stats)
            
            ### chart_info
            # ارسال مقادیر به عنوان لیست برای چارت
            chart_values = [
                box_stats["total_buy"],
                box_stats["total_sale"],
                box_stats["profit"],
                box_stats["harvest"],
                box_stats["total_barrow"],
                box_stats["current_capital"],
                box_stats["total_cush"],
            ]
            self.chart_data.emit(chart_values)

        except pymysql.Error as e:
            print(f"{e}: online db error")
    
    def full_data_offline(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
            if not os.path.exists(db_path):
                MessageBox(text="مسیر دیتابیس آفلاین پیدا نشد", title="ناموفق", type="error").show()
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users LIMIT 1")
            result = cursor.fetchone()
            if not result:
                print("آیدی کاربر در دیتابیس آفلاین یافت نشد.")
                return
            id_user = result[0]

            total_sale_f = 0
            total_sale_on = 0
            total_profit = 0
            total_buy = 0
            total_harvest = 0
            total_barrow = 0

            # sale_factor
            cursor.execute("SELECT SUM(total), SUM(profit) FROM sale_factor WHERE user_id = ?", (id_user,))
            res = cursor.fetchone()
            if res:
                total_sale_f = float(res[0]) if res[0] else 0
                total_profit = float(res[1]) if res[1] else 0

            ###

            total_sale = total_sale_f + total_sale_on

            # inventories
            cursor.execute("SELECT SUM(final_total) FROM products WHERE user_id = ?", (id_user,))
            res = cursor.fetchone()
            if res:
                total_buy = float(res[0]) if res[0] else 0

            # harvest
            cursor.execute("SELECT SUM(amount) FROM harvest WHERE user_id = ?", (id_user,))
            res = cursor.fetchone()
            if res:
                total_harvest = float(res[0]) if res[0] else 0

            # barrow
            cursor.execute("SELECT SUM(ABS(amount)) FROM barrow WHERE user_id = ?", (id_user,))
            res = cursor.fetchone()
            if res:
                total_barrow = float(res[0]) if res[0] else 0

            box_stats = {
                "total_buy": total_buy,
                "total_sale": total_sale,
                "profit": total_profit,
                "harvest": total_harvest,
                "total_barrow": total_barrow,
                "current_capital": total_buy - total_profit,
                "total_cush": total_sale,
            }

            self.full_info.emit(box_stats)
            self.chart_data.emit([
                box_stats["total_buy"],
                box_stats["total_sale"],
                box_stats["profit"],
                box_stats["harvest"],
                box_stats["total_barrow"],
                box_stats["current_capital"],
                box_stats["total_cush"],
            ])
            print("📦 آمار کلی از دیتابیس آفلاین خوانده شد.")

        except Exception as e:
            print("❌ خطا در full_data_offline:", e)

    ##
    def fetch_years_only(self):
        from datetime import datetime
        import jdatetime

        self.available_years = set()
        data = Connection().get_connection()
        if not data:
            self.fetch_years_only_offline()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1')
            result = cursor_sq.fetchone()
            if not result:
                return
            id_user = result[0]
        except:
            return

        try:
            cursor = data.cursor()
            cursor.execute("SELECT created_at FROM inventories WHERE user_id = %s", (id_user,))
            for row in cursor.fetchall():
                created_at = row[0]
                if not created_at:
                    continue
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except:
                        continue
                sh_year = str(jdatetime.date.fromgregorian(date=miladi.date()).year)
                self.available_years.add(sh_year)
        except pymysql.Error as e:
            print(f"online inventory problem:{e}")
    ##
    def fetch_years_only_offline(self):
        from datetime import datetime
        import jdatetime

        self.available_years = set()

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
            if not os.path.exists(db_path):
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1")
            result = cursor.fetchone()
            if not result:
                return
            id_user = result[0]

            cursor.execute("SELECT create_at FROM products WHERE user_id = ?", (id_user,))
            for row in cursor.fetchall():
                created_at = row[0]
                print(created_at)
                if not created_at:
                    continue
                try:
                    miladi = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        miladi = datetime.strptime(str(created_at), "%Y-%m-%d")
                    except:
                        continue
                sh_year = str(jdatetime.date.fromgregorian(date=miladi.date()).year)
                self.available_years.add(sh_year)
                self.year_data.emit(sorted(sh_year))
            print(f"📅 سال‌های موجود در دیتابیس آفلاین:{self.available_years}")

        except Exception as e:
            print("❌ خطا در fetch_years_only_offline:", e)

