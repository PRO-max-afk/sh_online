import os, requests, sqlite3, pymysql, time
from PyQt6.QtCore import QThread
from decimal import Decimal
from db_connection import Connection
from decimal import Decimal

class FixThread(QThread):
    def __init__(self,last_invent_id=0,last_fixed_id=0):
        super().__init__()
        self.last_invent_id = last_invent_id
        self.last_fixed_id = last_fixed_id
        self.db_connect = None

    def has_new_data(self):
        """ بررسی کند که داده جدیدی نسبت به آخرین اجرا وجود دارد یا خیر """
        try:
            cursor = self.db_connect.cursor()
            
            # بررسی fixeds
            cursor.execute("SELECT MAX(id) FROM fixeds")
            latest_fixed = cursor.fetchone()[0] or 0

            # بررسی inventories
            cursor.execute("SELECT MAX(invent_id) FROM inventories")
            latest_invent = cursor.fetchone()[0] or 0

            # اگر چیزی جدیدتر از آخرین ذخیره شده بود
            if latest_fixed > self.last_fixed_id or latest_invent > self.last_invent_id:
                self.last_fixed_id = latest_fixed
                self.last_invent_id = latest_invent
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
        else:
            print("ℹ️ داده جدیدی وجود ندارد → ترید اجرا نشد")


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
        conn= Connection().get_connection()
        cursor= conn.cursor()
        try:
            # فرض: فایل FixThread در مسیر D:\projects\sh_online\GUI\fixdes.py قرار دارد
            base_dir = os.path.dirname(os.path.abspath(__file__))              # → D:\projects\sh_online\GUI
            project_root = os.path.abspath(os.path.join(base_dir, ".."))       # → D:\projects\sh_online
            db_path = os.path.join(project_root, "Data", "sh_online.db")  

            print(f"📂 مسیر دیتابیس آفلاین: {db_path}")
            if not os.path.exists(db_path):
                print("❌ دیتابیس آفلاین یافت نشد.")
                return
            
            # اتصال به SQLite برای دریافت user_id
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1')
            user_row = cursor_sq.fetchone()

            if not user_row:
                self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                return

            id_user = user_row[0]

            # بارگذاری محصولات فقط برای user_id خاص
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
                # ✅ مدیریت مسیر تصویر
                if not product_image:
                    downloaded_image_path = os.path.join(os.getcwd(), "default.png")
                else:
                    downloaded_image_path = self.download_image_from_url(product_image)
                ##
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
            
                # بررسی وجود محصول با barcode
                cursor_sq.execute("SELECT COUNT(*) FROM products WHERE barcode = ? AND user_id = ?", (barcode, id_user))
                row = cursor_sq.fetchone()
                exists = row[0] if row else 0

                if exists:
                    cursor_sq.execute('''
                        UPDATE products SET
                            name = ?, category=?, sub_category=?, buy_date=?, buy_price=?, 
                            sale_price=?, store_name=?, new_price=?, discount_percent=?, 
                            big_price=?, big_quantity=?, big_sub=?, big_sub_display=?, 
                            total=?, final_total=?, sale_unit=?, quantity=?, expire_date=?, 
                            image_path=?, user_id=?, create_at=?
                        WHERE barcode = ?
                    ''', (product_name, category, sub_category, buy_date, buy_price,
                        sell_price, store_name, new_price, discount_percent, 
                        big_price, big_quantity, big_sub, big_sub_display,
                        total, final_total, sale_unit, quantity, expiration_dates,
                        downloaded_image_path, id_user, created_at, barcode))

                else:
                    # اگر وجود نداشت: درج کن
                    cursor.execute('''
                        INSERT INTO products (barcode, name, category,sub_category,buy_date,
                                buy_price, sale_price,big_category,store_name, new_price, discount_percent, big_price,big_quantity,big_sub,big_sub_display,
                                total,final_total, sale_unit,quantity, expire_date, image_path, user_id,create_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?)
                    ''',(product_name, barcode,category,sub_category,buy_date,buy_price, sell_price,
                        big_category,quantity, expiration_dates, downloaded_image_path,store_name, 
                        new_price, discount_percent, big_price,big_quantity,big_sub,big_sub_display,sale_unit, total,final_total,created_at))
        except pymysql.Error as e:
            print(f"offline db inventory problem:{e}")
