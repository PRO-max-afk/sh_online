import os, requests, sqlite3, pymysql, time
from PyQt6.QtCore import QThread,pyqtSignal
from decimal import Decimal
from db_connection import Connection
from decimal import Decimal

class FixThread(QThread):
    data_synced= pyqtSignal(bool)
    def __init__(self,last_invent_id=0,last_fixed_id=0):
        super().__init__()
        self.last_invent_id = last_invent_id
        self.last_fixed_id = last_fixed_id
        self.db_connect = None
        self.prev_inventory_state = {}

    def has_new_data(self):
        """ بررسی تغییرات واقعی در دیتابیس لوکال نسبت به MySQL """
        try:
            cursor = self.db_connect.cursor()

            # گرفتن آخرین داده‌ها از MySQL
            cursor.execute("SELECT invent_id, quantity, big_sub FROM inventories")
            mysql_rows = cursor.fetchall()
            mysql_state = {row[0]: (row[1], row[2]) for row in mysql_rows}

            # گرفتن داده‌های فعلی از SQLite
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(base_dir, ".."))
            db_path = os.path.join(project_root, "Data", "sh_online.db")

            if not os.path.exists(db_path):
                print("❌ دیتابیس آفلاین یافت نشد.")
                return False

            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT invent_id, quantity, big_sub FROM products")
            local_rows = cursor_sq.fetchall()
            conn_sq.close()

            local_state = {row[0]: (row[1], row[2]) for row in local_rows}

            # مقایسه MySQL با SQLite
            if mysql_state != local_state:
                print("🔄 تغییرات در inventory شناسایی شد")
                return True

            return False

        except Exception as e:
            print("❌ خطا در بررسی داده جدید:", e)
            return False



    def run(self):
        self.db_connect = Connection().get_connection()
        if not self.db_connect:
            return
        
        # ✅ فقط اگر دیتا جدید بود اجرا کن
        if self.has_new_data():
            print("🔄 داده جدید یافت شد → sync شروع شد...")
            self.get_fixed_info()
            self.get_inventory_info()
            self.get_orders_info()
            self.get_sale_factors()
            self.get_customer_info()
            self.get_salary_info()
            self.get_barrow_info()
            self.get_harvest_info()
            self.data_synced.emit(True)
        else:
            print("ℹ️ داده جدیدی وجود ندارد → ترید اجرا نشد")
            self.data_synced.emit(False)


    def download_image_from_url(self, image_path):
        try:
            if not image_path:
                raise ValueError("image_path is empty or None")

            if not image_path.startswith("http"):
                base_url = "https://ihr.blg.mybluehost.me/storage/"
                image_path = base_url + image_path.lstrip("/")

            print(f"📥 در حال تلاش برای دریافت تصویر از: {image_path}")

            local_dir = os.path.join(os.getcwd(), "temp_images")
            os.makedirs(local_dir, exist_ok=True)

            filename = os.path.basename(image_path)
            local_path = os.path.join(local_dir, filename)

            if os.path.exists(local_path):
                print("📦 تصویر قبلاً دانلود شده:", local_path)
                return local_path  # مسیر لوکال به‌جای لینک URL

            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(image_path, headers=headers, timeout=20)
            if response.status_code == 404:
                raise FileNotFoundError(f"تصویر یافت نشد: {image_path}")

            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print("✅ تصویر با موفقیت دانلود شد:", local_path)
            return local_path  # فقط مسیر فایل روی سیستم

        except Exception as e:
            print("❌ خطا در دریافت تصویر:", e)
            default_image_path = os.path.join(os.getcwd(), "default.png")
            if os.path.exists(default_image_path):
                return default_image_path
            return None


    def get_fixed_info(self):
        try:
            # فرض: فایل FixThread در مسیر D:\projects\sh_online\GUI\fixdes.py قرار دارد
            base_dir = os.path.dirname(os.path.abspath(__file__))              # → D:\projects\sh_online\GUI
            project_root = os.path.abspath(os.path.join(base_dir, ".."))       # → D:\projects\sh_online
            db_path = os.path.join(project_root, "Data", "sh_online.db")  

            print(f"📂 مسیر دیتابیس آفلاین: {db_path}")
            if not os.path.exists(db_path):
                print("❌ دیتابیس آفلاین یافت نشد.")
                return

            # اتصال جدا به دیتابیس SQLite
            conn_sq = sqlite3.connect(db_path, check_same_thread=False)
            cursor_sq = conn_sq.cursor()

            cursor = self.db_connect.cursor()
            cursor.execute('''
                SELECT barcode, product_name, categorie, sub_categorie, product_image,
                       weight, production_date, brand, production_place, product_state, 
                       more_detail, keep_place, buy_price, sell_price, big_price, 
                       big_category, sale_unit, big_quantity
                FROM fixeds
            ''')

            fixeds_result = cursor.fetchall()

            for product in fixeds_result:
                (
                    barcode, product_name, categorie, sub_categorie, product_image,
                    weight, production_date, brand, production_place, product_state,
                    more_detail, keep_place, buy_price, sell_price, big_price,
                    big_category, sale_unit, big_quantity
                ) = product

                # 🔄 تبدیل Decimal‌ها به float
                buy_price = float(buy_price) if isinstance(buy_price, Decimal) else buy_price
                sell_price = float(sell_price) if isinstance(sell_price, Decimal) else sell_price
                big_price = float(big_price) if isinstance(big_price, Decimal) else big_price


                # ✅ مدیریت مسیر تصویر
                if not product_image:
                    downloaded_image_path = os.path.join(os.getcwd(), "default.png")
                else:
                    downloaded_image_path = self.download_image_from_url(product_image)


                # بررسی وجود داده
                cursor_sq.execute("SELECT COUNT(*) FROM fixeds WHERE barcode = ?", (barcode,))
                exists = cursor_sq.fetchone()[0]

                if exists:
                    try:
                        for attempt in range(3):
                            try:
                                cursor_sq.execute('''
                                    UPDATE fixeds SET
                                        barcode=?, product_name=?, categorie=?, sub_categorie=?, product_image=?,
                                        weight=?, production_date=?, brand=?, production_place=?, product_state=?, more_detail=?,
                                        keep_place=?, buy_price=?, sell_price=?, big_price=?, big_category=?,
                                        sale_unit=?, big_quantity=?
                                    WHERE barcode=?
                                ''', (
                                    barcode, product_name, categorie, sub_categorie, downloaded_image_path,
                                    weight, production_date, brand, production_place, product_state, more_detail,
                                    keep_place, buy_price, sell_price, big_price, big_category, sale_unit, big_quantity,
                                    barcode
                                ))
                                print("info updated successfully ✅")
                                conn_sq.commit()
                                break
                            except sqlite3.OperationalError as e:
                                if "locked" in str(e):
                                    print("⏳ دیتابیس قفل است، تلاش مجدد...")
                                    time.sleep(1)
                                else:
                                    raise
                    except sqlite3.Error as e:
                        print(f"{e}: مشکل در بروزرسانی آفلاین")

                else:
                    try:
                        for attempt in range(3):
                            try:
                                cursor_sq.execute('''
                                    INSERT INTO fixeds (barcode, product_name, categorie, sub_categorie, product_image,
                                                        weight, production_date, brand, production_place, product_state, 
                                                        more_detail, keep_place, buy_price, sell_price,
                                                        big_price, big_category, sale_unit, big_quantity)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    barcode, product_name, categorie, sub_categorie, downloaded_image_path,
                                    weight, production_date, brand, production_place, product_state,
                                    more_detail, keep_place, buy_price, sell_price,
                                    big_price, big_category, sale_unit, big_quantity
                                ))
                                print("info inserted successfully ✅")
                                conn_sq.commit()
                                break
                            except sqlite3.OperationalError as e:
                                if "locked" in str(e):
                                    print("⏳ دیتابیس قفل است (در insert)، تلاش مجدد...")
                                    time.sleep(1)
                                else:
                                    raise
                    except sqlite3.Error as e:
                        print(f"{e}: مشکل در درج آفلاین")

            conn_sq.close()

        except pymysql.Error as e:
            print(f"❌ خطا در دیتابیس آنلاین: {e}")
    
    def get_inventory_info(self):
        rows = []
        conn = None
        cursor = None

        try:
            # 📌 تلاش برای اتصال آنلاین (MySQL)
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()

                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")

                # اتصال به SQLite برای دریافت user_id
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                user_row = cursor_sq.fetchone()

                if not user_row:
                    self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                    return []

                id_user = user_row[0]

                # 🔹 کوئری روی MySQL
                cursor.execute('''
                    SELECT 
                        product_name, barcode, category, sub_category, buy_date, buy_price, sell_price,
                        big_category, quantity, expiration_dates, product_image, store_name,
                        new_price, discount_percent, big_price, big_quantity, big_sub, big_sub_display,
                        sale_unit, total, final_total, created_at
                    FROM inventories
                    WHERE quantity > 0 AND user_id = %s
                    ORDER BY invent_id DESC
                ''', (id_user,))
                products = cursor.fetchall()

                for product in products:
                    (product_name, barcode, category, sub_category, buy_date, buy_price, sell_price,
                    big_category, quantity, expiration_dates, product_image, store_name,
                    new_price, discount_percent, big_price, big_quantity, big_sub, big_sub_display,
                    sale_unit, total, final_total, created_at) = product

                    # ✅ مسیر تصویر
                    if not product_image:
                        downloaded_image_path = os.path.join(os.getcwd(), "default.png")
                    else:
                        downloaded_image_path = self.download_image_from_url(product_image)

                    # 🔄 تبدیل Decimal به float
                    def safe_num(val):
                        return float(val) if isinstance(val, Decimal) else val

                    buy_price        = safe_num(buy_price)
                    sell_price       = safe_num(sell_price)
                    quantity         = safe_num(quantity)
                    new_price        = safe_num(new_price)
                    discount_percent = safe_num(discount_percent)
                    big_price        = safe_num(big_price)
                    big_sub          = safe_num(big_sub)
                    total            = safe_num(total)
                    final_total      = safe_num(final_total)

                    # بررسی وجود محصول در SQLite
                    cursor_sq.execute(
                        "SELECT COUNT(*) FROM products WHERE barcode = ? AND user_id = ?", 
                        (barcode, id_user)
                    )
                    row = cursor_sq.fetchone()
                    exists = row[0] if row else 0

                    # بررسی مقدار quantity و big_sub
                    cursor_sq.execute(
                        "SELECT quantity, big_sub FROM products WHERE barcode=? AND user_id=?",
                        (barcode, id_user)
                    )
                    row_q = cursor_sq.fetchone()

                    if exists:
                        qua, big_s = row_q
                        if qua != quantity or big_s != big_sub:
                            # آپدیت محصول
                            cursor_sq.execute('''
                                UPDATE products SET
                                    name=?, category=?, sub_category=?, buy_date=?, buy_price=?, 
                                    sale_price=?, store_name=?, new_price=?, discount_percent=?, 
                                    big_price=?, big_quantity=?, big_sub=?, big_sub_display=?, 
                                    total=?, final_total=?, sale_unit=?, quantity=?, expire_date=?, 
                                    image_path=?, user_id=?, create_at=?
                                WHERE barcode=? AND user_id=?
                            ''', (
                                product_name, category, sub_category, buy_date, buy_price,
                                sell_price, store_name, new_price, discount_percent,
                                big_price, big_quantity, big_sub, big_sub_display,
                                total, final_total, sale_unit, quantity, expiration_dates,
                                downloaded_image_path, id_user, created_at, barcode, id_user
                            ))
                    else:
                        # درج محصول جدید
                        cursor_sq.execute('''
                            INSERT INTO products (
                                barcode, name, category, sub_category, buy_date,
                                buy_price, sale_price, big_category, store_name,
                                new_price, discount_percent, big_price, big_quantity,
                                big_sub, big_sub_display, total, final_total,
                                sale_unit, quantity, expire_date, image_path,
                                user_id, create_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            barcode, product_name, category, sub_category, buy_date,
                            buy_price, sell_price, big_category, store_name,
                            new_price, discount_percent, big_price, big_quantity,
                            big_sub, big_sub_display, total, final_total,
                            sale_unit, quantity, expiration_dates, downloaded_image_path,
                            id_user, created_at
                        ))

                conn_sq.commit()
                conn_sq.close()
                conn.close()
                return products

        except pymysql.Error as e:
            print(f"❌ مشکل در دریافت اطلاعات از MySQL: {e}")

        # 📌 اگر آنلاین در دسترس نبود → استفاده از دیتابیس آفلاین
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))              
            project_root = os.path.abspath(os.path.join(base_dir, ".."))       
            db_path = os.path.join(project_root, "Data", "sh_online.db")

            if not os.path.exists(db_path):
                print("❌ دیتابیس آفلاین یافت نشد.")
                return []

            offline_conn = sqlite3.connect(db_path)
            cursor = offline_conn.cursor()
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            offline_conn.close()
            print("✅ داده‌ها از دیتابیس آفلاین خوانده شدند.")
            return rows

        except sqlite3.Error as e:
            print(f"❌ مشکل در دیتابیس SQLite: {e}")
            return []
    
    def get_orders_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                cursor.execute('''
                    SELECT 
                        id,buyer_id,address,home_number,area,phone,invent_id,product_name,
                        quantity,price,profit,sale_number,product_unit,user_id,approve,denied,
                        message,created_at,updated_at,customer_name
                    FROM orders 
                    WHERE user_id = %s AND approve = 1
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for sale_orders in unsaved:
                    (id_e, buyer_id, address, home_number, area, phone, invenit_id, product_name,
                    quantity, price, profit, sale_number, product_unit, user_id, approve, denied,
                    message, created_at, updated_at, customer_name) = sale_orders

                    def safe_num(val):
                        return float(val) if isinstance(val, Decimal) else val

                    total = safe_num(price)
                    total_profit = safe_num(profit)

                    # ✅ بررسی وجود id_e در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM orders WHERE id = ?", (id_e,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO orders(
                                id,buyer_id,address,home_number,area,phone,invent_id,product_name,
                                quantity,price,profit,sale_number,product_unit,user_id,approve,denied,
                                message,created_at,updated_at,customer_name
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ''', (id_e, buyer_id, address, home_number, area, phone, invenit_id, product_name,
                            quantity, total, total_profit, sale_number, product_unit, user_id, approve, denied,
                            message, created_at, updated_at, customer_name))
                        conn_sq.commit()
                        print(f"✅ info orders inserted: {id_e}")
                    else:
                        print(f"⚠️ سفارش {id_e} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"online orders problem: {e}")

    def get_sale_factors(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                cursor.execute('''
                    SELECT 
                        product_name,barcode,factor_number,sale_price,sale_date,
                        quantity,product_type,sale_type,user_id,discount,total,profit,cus_id,choise_type
                    FROM sale_factor
                    WHERE user_id = %s;
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for sale_factor in unsaved:
                    (product_name,barcode,factor_number,sale_price,sale_date,
                        quantity,product_type,sale_type,user_id,discount,total,profit,cus_id,choise_type) = sale_factor

                    def safe_num(val):
                        return float(val) if isinstance(val, Decimal) else val

                    total = safe_num(total)
                    total_profit = safe_num(profit)

                    # ✅ بررسی وجود id_e در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM sale_factor WHERE factor_number = ?", (factor_number,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO sale_factor(
                                product_name,barcode,factor_number,sale_price,sale_date,
                                quantity,product_type,sale_type,user_id,discount,total,profit,cus_id,choise_type
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ''',  (product_name,barcode,factor_number,sale_price,sale_date,
                                quantity,product_type,sale_type,user_id,discount,total,total_profit,cus_id,choise_type))
                        conn_sq.commit()
                        print(f"✅ info factor inserted: {factor_number}")
                    else:
                        print(f"⚠️ فاکتور {factor_number} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"sale_factor db problems: {e}")
    
    def get_customer_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                cursor.execute('''
                    SELECT 
                    id,name,last_name,phone,register_date,email,user_id
                    FROM customer
                    WHERE user_id = %s 
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for customers in unsaved:
                    ( id_e,name,last_name,phone,register_date,email,user_id) = customers

                    # ✅ بررسی وجود id_e در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM customers WHERE id = ?", (id_e,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO cusotmers(
                                 id,name,last_name,phone,register_date,email,user_id
                            ) VALUES (?,?,?,?,?,?,?)
                        ''', ( id_e,name,last_name,phone,register_date,email,user_id))
                        conn_sq.commit()
                        print(f"✅ info customer inserted: {id_e}")
                    else:
                        print(f"⚠️ مشتری {id_e} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"online orders problem: {e}")

    def get_worker_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                cursor.execute('''
                    SELECT 
                    employee_id,first_name,last_name,phone,email,address,city,position,salary,hire_date,status,user_id
                    FROM employees
                    WHERE user_id = %s 
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for employee in unsaved:
                    ( employee_id,first_name,last_name,phone,email,address,city,position,salary,hire_date,status,user_id) = employee

                    # ✅ بررسی وجود id_e در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM employees WHERE employee_id = ?", (employee_id,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO employees(
                                employee_id,first_name,last_name,phone,email,address,city,position,salary,hire_date,status,user_id
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                        ''', (employee_id,first_name,last_name,phone,email,address,
                            city,position,salary,hire_date,status,user_id))
                        conn_sq.commit()
                        print(f"✅ info employee inserted: {employee_id}")
                    else:
                        print(f"⚠️ کارمند {employee_id} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"online orders problem: {e}")

    def get_salary_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                cursor.execute('''
                    SELECT 
                    salary_id,employee_id,pay_date,amount,note
                    FROM salaries
                    WHERE employee_id = %s 
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for salaries in unsaved:
                    ( salary_id,employee_id,pay_date,amount,note) = salaries

                    # ✅ بررسی وجود id_e در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM salaries WHERE employee_id = ?", (employee_id,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO salaries(
                                salary_id,employee_id,pay_date,amount,note
                            ) VALUES (?,?,?,?,?)
                        ''', (salary_id,employee_id,pay_date,amount,note))
                        conn_sq.commit()
                        print(f"✅ info salary employee inserted: {employee_id}")
                    else:
                        #print(f"⚠️ معاش کارمند {employee_id} قبلا ذخیره شده و دوباره insert نشد.")
                        print(f"salary of employee:{employee_id}")

        except pymysql.Error as e:
            print(f"online orders problem: {e}")

    def get_barrow_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()

                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                # گرفتن اطلاعات از سرور
                cursor.execute('''
                    SELECT 
                        b_id, name, amount, type, date, description, user_id, phone, cus_id
                    FROM barrow
                    WHERE user_id = %s
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for row in unsaved:
                    (id_e, name, amount, type_b, date, description, user_id, phone, cus_id) = row

                    # ✅ بررسی وجود رکورد در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM barrow WHERE b_id = ?", (id_e,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO barrow(
                                b_id, name, amount, type, date, description, user_id, phone, cus_id
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (id_e, name, amount, type_b, date, description, user_id, phone, cus_id))
                        conn_sq.commit()
                        print(f"✅ info barrow inserted: {id_e}")
                    else:
                        print(f"⚠️ barrow {id_e} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"online barrow problem: {e}")

    def get_harvest_info(self):
        try:
            conn = Connection().get_connection()
            if conn:
                cursor = conn.cursor()
                # مسیر دیتابیس آفلاین
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(base_dir, ".."))
                db_path = os.path.join(project_root, "Data", "sh_online.db")
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()

                cursor_sq.execute("SELECT id FROM users LIMIT 1")
                id_user = cursor_sq.fetchone()[0]

                # گرفتن اطلاعات از سرور
                cursor.execute('''
                    SELECT 
                        h_id, name, amount,date, description, user_id,har_type
                    FROM harvest
                    WHERE user_id = %s
                ''', (id_user,))
                unsaved = cursor.fetchall()

                for row in unsaved:
                    (h_id, name, amount,date, description, user_id,har_type) = row

                    # ✅ بررسی وجود رکورد در دیتابیس آفلاین
                    cursor_sq.execute("SELECT COUNT(*) FROM harvest WHERE h_id = ?", (h_id,))
                    exists = cursor_sq.fetchone()[0]

                    if exists == 0:  # فقط اگر وجود ندارد وارد کن
                        cursor_sq.execute('''
                            INSERT INTO harvest(
                                h_id, name, amount,date, description, user_id,har_type
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', h_id, name, amount,date, description, user_id,har_type)
                        conn_sq.commit()
                        print(f"✅ info harvest inserted: {h_id}")
                    else:
                        print(f"⚠️ harvest {h_id} قبلا ذخیره شده و دوباره insert نشد.")

        except pymysql.Error as e:
            print(f"online harvest problem: {e}")

