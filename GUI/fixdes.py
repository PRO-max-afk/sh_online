import os, requests, sqlite3, pymysql, time
from PyQt6.QtCore import QThread
from decimal import Decimal
from db_connection import Connection

class FixThread(QThread):
    def __init__(self):
        super().__init__()
        self.db_connect = Connection().get_connection()

    def run(self):
        if self.db_connect:
            self.get_fixed_info()

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
                return local_path

            headers = {
                'User-Agent': 'Mozilla/5.0'
            }

            response = requests.get(image_path, headers=headers, timeout=20)
            if response.status_code == 404:
                raise FileNotFoundError(f"تصویر یافت نشد: {image_path}")

            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print("✅ تصویر با موفقیت دانلود شد:", local_path)
            return local_path

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

                # ✅ تبدیل Decimal به float
                for var_name in ['buy_price', 'sell_price', 'big_price']:
                    value = locals()[var_name]
                    if isinstance(value, Decimal):
                        locals()[var_name] = float(value)

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
                                        barcode=?, product_name=?, category=?, sub_category=?, product_image=?,
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
