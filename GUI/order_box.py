from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import time
import os
import requests
from message_b import MessageBox

class OrderInformation(QThread):
    new_order_info = pyqtSignal(list)  # لیستی از دیکشنری‌ها شامل اطلاعات محصولات
    order_count_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.prev_count = -1
        self.sale_number= None
        self.order_number=None

    def run(self):
        while self.running:
            db_config = self.get_db_config()
            if not db_config:
                time.sleep(5)
                continue

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
                    SELECT id,sale_number, customer_name, product_name, quantity, area, home_number, phone, product_unit
                    FROM orders
                    WHERE approve=0 and denied=0 and user_id = %s
                """, (id_user,))
                results = cursor.fetchall()
                ###
                if results:
                    # گرفتن تمام sale_number و order_id از MySQL
                    new_sale_numbers = list(set(row[1] for row in results))
                    new_order_ids = list(set(row[0] for row in results))

                    # گرفتن اطلاعات فعلی از SQLite
                    cursor_sq.execute("SELECT sale_id FROM sale_number")
                    current_sales = sorted(row[0] for row in cursor_sq.fetchall())

                    cursor_sq.execute("SELECT order_id FROM order_number")
                    current_orders = sorted(row[0] for row in cursor_sq.fetchall())

                    # مقایسه لیست‌ها
                    if sorted(new_sale_numbers) != current_sales:
                        cursor_sq.execute("DELETE FROM sale_number")
                        cursor_sq.executemany("INSERT INTO sale_number(sale_id) VALUES (?)", 
                                            [(sid,) for sid in new_sale_numbers])

                    if sorted(new_order_ids) != current_orders:
                        cursor_sq.execute("DELETE FROM order_number")
                        cursor_sq.executemany("INSERT INTO order_number(order_id) VALUES (?)", 
                                            [(oid,) for oid in new_order_ids])

                    conn_sq.commit()

                    self.sale_number = new_sale_numbers[0] if new_sale_numbers else None
                    self.order_number = new_order_ids[0] if new_order_ids else None
                else:
                    self.sale_number = None
                    self.order_number = None


                orders = {}

                for row in results:
                    order_id, sale_number, name, product_name, quantity, area, home_number, phone, unit = row

                    if sale_number not in orders:
                        orders[sale_number] = {
                            "sale_number": sale_number,
                            "customer_name": name,
                            "area": area,
                            "home_number": home_number,
                            "phone": phone,
                            "products": []  # ✅ هر محصول با آیدی خاص خودش
                        }

                    orders[sale_number]["products"].append({
                        "id": order_id,  # 👈 اضافه کردن آیدی خاص هر ردیف
                        "product_name": product_name,
                        "quantity": quantity,
                        "unit": unit
                    })


                # تبدیل دیکشنری به لیست برای ارسال به show_nt
                grouped_orders = list(orders.values())

                count = len(grouped_orders)
                if count != self.prev_count:
                    self.prev_count = count
                    self.order_count_signal.emit(count)
                    self.new_order_info.emit(grouped_orders)
                conn.close()
            except pymysql.MySQLError as e:
                print(f"{e}: خطا در کوئری یا اتصال دیتابیس")


            time.sleep(5)
    ##
    def accept_order(self):
        try:
            db_check = self.get_db_config()
            if not db_check:
                return False
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return False

            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            ##
            cursor_sq.execute("select sale_id from sale_number;")
            sal_num=cursor_sq.fetchone()

            if not res_id and not sal_num :
                return False
            id_user = res_id[0]
            sale_number= sal_num[0]

            conn = pymysql.connect(
                host=db_check["host"],
                user=db_check["user"],
                password=db_check["password"],
                database=db_check["database"]
            )
            cursor = conn.cursor()
            print("✔️ sale_number:", self.sale_number)

            cursor.execute("UPDATE orders SET approve=1 WHERE user_id=%s AND sale_number=%s", (id_user, sale_number))
            print("📝 تعداد رکوردهای به‌روز شده:", cursor.rowcount)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"{e}: خطا در تایید سفارش")
            return False
    ##
    def denied_order(self):
        try:
            db_check = self.get_db_config()
            if not db_check:
                return False
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return False

            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            ##
            cursor_sq.execute("select sale_id from sale_number;")
            sal_num=cursor_sq.fetchone()

            if not res_id and not sal_num :
                return False
            id_user = res_id[0]
            sale_number= sal_num[0]

            conn = pymysql.connect(
                host=db_check["host"],
                user=db_check["user"],
                password=db_check["password"],
                database=db_check["database"]
            )
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET denied=1 WHERE user_id=%s AND sale_number=%s", (id_user, sale_number))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"{e}: خطا در تایید سفارش")
            return False
    ##
    def reject_order(self, product_id: int) -> bool:
        try:
            # بررسی فایل کانفیگ اتصال آنلاین
            db_check = self.get_db_config()
            if not db_check:
                print("❌ تنظیمات دیتابیس یافت نشد.")
                return False

            # بررسی وجود دیتابیس آفلاین
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return False

            # اتصال به SQLite برای گرفتن user_id
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()

            cursor_sq.execute("SELECT id FROM users LIMIT 1;")
            res_id = cursor_sq.fetchone()
            if not res_id:
                print("❌ کاربر یافت نشد.")
                return False

            id_user = res_id[0]
            message= "محصول از طرف فروشگاه رد شد"

            # اتصال به MySQL
            conn = pymysql.connect(
                host=db_check["host"],
                user=db_check["user"],
                password=db_check["password"],
                database=db_check["database"]
            )
            cursor = conn.cursor()

            # بررسی اینکه آیا این سفارش وجود دارد و قابل رد شدن هست یا نه
            cursor.execute("""
                SELECT id FROM orders 
                WHERE user_id=%s AND id=%s AND approve=0 AND denied=0
            """, (id_user, product_id))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE orders SET message= %s, denied=1 WHERE id=%s", (message,product_id))
                conn.commit()
                print(f"⛔ رد سفارش با ID = {product_id}")
                return True
            else:
                print(f"❌ سفارش با ID = {product_id} قابل رد شدن نیست یا وجود ندارد.")
                return False

        except Exception as e:
            print(f"{e}: خطا در رد سفارش")
            return False

        finally:
            try:
                conn.close()
            except:
                pass

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
