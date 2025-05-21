from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtCore import Qt,QTimer,QThread, pyqtSignal
from PyQt6.QtGui import QColor,QIcon,QFontDatabase
from PyQt6 import QtCore
import jdatetime
import os
import requests
import sqlite3
from message_b import MessageBox
from notifi_box import Notification
from circle import CircularSpinner
from notifi_check import NotificationChecker
import pymysql
from info_box import ProductBox
from decimal import Decimal
import threading
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt

class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    ##
    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data
        except Exception as e:
            print("خطا در دریافت config:", e)
            return None
        ## 
    ##
    def load_all_data(self):
        self.db_data = self.get_db_config()
        if not self.db_data:
            self.error_occurred.emit("لطفاً اینترنت خود را بررسی کنید❌ اتصال به سرور ناموفق بود")
            return

        conn = None
        conn_sq = None
        try:
            # اتصال به دیتابیس اصلی (MySQL)
            conn = pymysql.connect(
                host=self.db_data["host"],
                user=self.db_data["user"],
                password=self.db_data["password"],
                database=self.db_data["database"]
            )
            cursor = conn.cursor()

            # اتصال به SQLite برای دریافت user_id
            conn_sq = sqlite3.connect('Data\\sh_online.db')
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1')
            user_row = cursor_sq.fetchone()

            if not user_row:
                self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                return

            id_user = user_row[0]

            # بارگذاری محصولات فقط برای user_id خاص
            cursor.execute('''
                SELECT product_name, barcode,category,sub_category,buy_date,buy_price, sell_price,
                           big_category,quantity, expiration_dates, product_image,store_name, 
                           new_price, discount_percent, big_price,big_sub,big_sub_display, total
                FROM inventories
                WHERE quantity > 0 and user_id = %s 
                ORDER BY invent_id DESC
            ''', (id_user,))
            products = cursor.fetchall()

            product_list = []
            for product in products:
                name, barcode,category, sub_category,buy_date,buy_price, sale_price,big_category,quantity, exp_date, image_path, store_name, new_price, discount_percent, big_price,big_sub,big_sub_display, total= product

                product_info = {
                    "name": name,
                    "barcode": barcode,
                    "category":category,
                    "sub_category": sub_category,
                    "buy_date": buy_date,
                    "buy_price": float(buy_price) if isinstance(buy_price, Decimal) else buy_price,
                    "sale_price": float(sale_price) if isinstance(sale_price, Decimal) else sale_price,
                    "big_category": big_category,
                    "quantity": float(quantity) if isinstance(quantity, Decimal) else quantity,
                    "expire_date": exp_date,
                    "image_path": image_path,
                    "user_id": id_user,
                    "store_name": store_name,
                    "new_price": float(new_price) if isinstance(new_price, Decimal) else new_price,
                    "discount_percent": float(discount_percent) if isinstance(discount_percent, Decimal) else discount_percent,
                    "big_price": float(big_price) if isinstance(big_price, Decimal) else big_price,
                    "big_sub" : float(big_sub) if isinstance(big_sub,Decimal) else big_sub,
                    "big_sub_display" : big_sub_display,
                    "total": float(total) if isinstance(total, Decimal) else total
                }
                product_list.append(product_info)

            # ذخیره یا آپدیت در SQLite
            self.store_in_local_db(product_list)

            self.data_loaded.emit(product_list)

        except Exception as e:
            self.error_occurred.emit(f"خطا در بارگذاری محصولات: {e}")

        finally:
            if conn:
                conn.close()
            if conn_sq:
                conn_sq.close()

    ##
    def store_in_local_db(self, product_list):
        conn = sqlite3.connect("Data\\sh_online.db")
        cursor = conn.cursor()

        for product in product_list:
            if all(key in product for key in ["barcode", "name", "category","sub_category","buy_date","buy_price", "sale_price","big_category","store_name", "new_price", "discount_percent", "big_price", "big_sub","big_sub_display","total", "quantity", "expire_date", "image_path", "user_id"]):
                
                # بررسی وجود محصول با barcode
                cursor.execute("SELECT COUNT(*) FROM products WHERE barcode = ?", (product["barcode"],))
                exists = cursor.fetchone()[0]

                if exists:
                    # اگر وجود داشت: آپدیت کن
                    cursor.execute('''
                        UPDATE products SET
                            barcode=?,name = ?, category=?,sub_category=?,buy_date=?,buy_price = ?, sale_price = ?, store_name = ?, new_price = ?, 
                            discount_percent = ?, big_price = ?, big_sub=?, big_sub_display=?,total = ?, quantity = ?, expire_date = ?, 
                            image_path = ?, user_id = ?
                        WHERE barcode = ?
                    ''', (
                        product["barcode"],
                        product["name"],
                        product["category"],
                        product["sub_category"],
                        product["buy_date"],
                        product["buy_price"],
                        product["sale_price"],
                        product["big_category"],
                        product["store_name"],
                        product["new_price"],
                        product["discount_percent"],
                        product["big_price"],
                        product["big_sub"],
                        product["big_sub_display"],
                        product["total"],
                        product["quantity"],
                        product["expire_date"],
                        product["image_path"],
                        product["user_id"]
                    ))
                else:
                    # اگر وجود نداشت: درج کن
                    cursor.execute('''
                        INSERT INTO products (barcode, name, category,sub_category,buy_date,
                                   buy_price, sale_price,big_category,store_name, new_price, discount_percent, big_price,big_sub,big_sub_display,
                                    total, quantity, expire_date, image_path, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)
                    ''', (
                        product["barcode"],
                        product["name"],
                        product["category"],
                        product["sub_category"],
                        product["buy_date"],
                        product["buy_price"],
                        product["sale_price"],
                        product["big_category"],
                        product["store_name"],
                        product["new_price"],
                        product["discount_percent"],
                        product["big_price"],
                        product["big_sub"],
                        product["big_sub_display"],
                        product["total"],
                        product["quantity"],
                        product["expire_date"],
                        product["image_path"],
                        product["user_id"]
                    ))

        conn.commit()
        conn.close()

    ##
    def load_from_local_db(self):
        try:
            conn = sqlite3.connect("Data\\sh_online.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1")
            row = cursor.fetchone()
            if not row:
                self.error_occurred.emit("❌ کاربر در دیتابیس آفلاین یافت نشد")
                return
            user_id = row[0]

            cursor.execute('''
                SELECT name, barcode, buy_price, sale_price, quantity, expire_date,big_price,big_sub_display, image_path
                FROM products
                WHERE user_id = ?
            ''', (user_id,))
            rows = cursor.fetchall()

            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)

            product_list = []
            for r in rows:
                name, barcode, buy_price, sale_price, quantity, expire_date,big_price,big_sub_display, image_path = r

                local_image = image_path
                if image_path:
                    local_image_path = os.path.join(temp_dir, os.path.basename(image_path))
                    if not os.path.exists(local_image_path):
                        try:
                            with open(image_path, 'rb') as src, open(local_image_path, 'wb') as dst:
                                dst.write(src.read())
                        except Exception as e:
                            print(f"❌ خطا در کپی عکس: {e}")
                    local_image = local_image_path

                product_list.append({
                    "name": name,
                    "barcode": barcode,
                    "buy_price": buy_price,
                    "sale_price": sale_price,
                    "quantity": quantity,
                    "expire_date": expire_date,
                    "big_sub_display": big_sub_display,
                    "big_price" : big_price,
                    "image_path": local_image
                })

            self.data_loaded.emit(product_list)

        except Exception as e:
            self.error_occurred.emit(f"❌ خطا در بارگذاری آفلاین: {e}")
        finally:
            if conn:
                conn.close()

    ##
    def run(self):
        if self.get_db_config():
            self.load_all_data()  # حالت آنلاین
        else:
            self.load_from_local_db()  # حالت آفلاین


class SearchThread(QThread):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, search_text):
        super().__init__()
        self.search_text = search_text

    ##
    def run(self):
        try:
            conn = sqlite3.connect('Data\\sh_online.db')
            cursor = conn.cursor()
            ##
            cursor.execute("select id from users LIMIT 1")
            c_row= cursor.fetchone()
            id_user= c_row[0]
            if not id_user:
                    self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                    return
            # جستجو بر اساس متن وارد شده در نام محصول
            cursor.execute('''
                SELECT name, barcode, buy_price, sale_price, quantity, expire_date,big_price,big_sub_display, image_path
                FROM products
                WHERE quantity > 0 and user_id = ? and name LIKE ?
            ''', (id_user,'%' + self.search_text + '%',))
            products = cursor.fetchall()

            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)

            product_list = []
            for product in products:
                name, barcode, buy_price, sale_price, quantity, exp_date,big_price,big_sub_display, image_path = product

                # بررسی وجود عکس
                if image_path:
                    full_image_path = os.path.join(temp_dir, os.path.basename(image_path))
                    if not os.path.exists(full_image_path):
                        try:
                            # کپی یا ذخیره‌سازی عکس در صورت عدم وجود (اینجا فقط نمونه آورده شده)
                            with open(image_path, 'rb') as src_file:
                                with open(full_image_path, 'wb') as dst_file:
                                    dst_file.write(src_file.read())
                        except Exception as img_err:
                            print(f"❌ خطا در کپی تصویر: {img_err}")

                    image_path = full_image_path  # به‌روزرسانی مسیر عکس

                product_info = {
                    "name": name,
                    "barcode": barcode,
                    "buy_price": buy_price,
                    "sale_price": sale_price,
                    "quantity": quantity,
                    "expire_date": exp_date,
                    "big_sub_display" : big_sub_display,
                    "big_price" :big_price,
                    "image_path": image_path
                }
                product_list.append(product_info)

            self.data_loaded.emit(product_list)

        except Exception as e:
            self.error_occurred.emit(str(e))

        finally:
            if conn:
                conn.close()
  
class Inventory(QFrame):
    def __init__(self):
        super().__init__()
        self.spinner = None
        self.search_initialized = False  # 👈 اینجا بیار بالا
        self.init_ui()
        self.label_UI()
        self.field_UI()
        self.set_today_date()
        self.set_today_time()
        self.button_UI()
        self.show_spinner_and_load_data()
        self.start_auto_refresh()
        self.start_auto_sync_timer()
        self.load_all_fonts()
        self.start_notification_checker()
        self.start_synced_to_server()
        


    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # ScrollArea setup
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #eee;
                width: 10px;
                margin: 4px 0 4px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #999;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("لیست محصولات فروشگاه", self)
        self.search_line = QLineEdit(self)
        self.serach_btn = QPushButton("جستجو", self)
        self.add_btn = QPushButton()
        self.new_btn = QPushButton()

        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.search_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.serach_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.new_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.serach_btn)
        top_layout.addWidget(self.search_line, 3)
        top_layout.addWidget(self.label, 1)

        # دکمه‌ها
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        scroll_layout.addSpacing(20)

        # لایه جعبه‌ها
        self.box_layout = QGridLayout()
        self.box_layout.setSpacing(10)
        scroll_layout.addLayout(self.box_layout)
        scroll_layout.addStretch()

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()

        ##

    def label_UI(self):
        self.label.setMinimumSize(200, 40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;
        ''')

    def field_UI(self):
        self.search_line.setMinimumHeight(60)
        self.search_line.setMaximumHeight(70)
        self.search_line.setMaximumWidth(700)
        self.search_line.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_line.textChanged.connect(self.show_spinner_and_load_dataes)
        self.search_line.setPlaceholderText("جستجو محصولات...")
        self.search_line.setStyleSheet('''
            font-size: 17px;
            color: black;
            font-family: B Nazanin;
            font-weight: bold;
            background-color: white;
            border: 5px solid transparent;
            border-radius: 30px;
            padding: 5px;
            margin-right: 50px;
        ''')
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.search_line.setGraphicsEffect(shadow)

    def button_UI(self):
        self.serach_btn.setMinimumSize(100, 30)
        self.serach_btn.setMaximumSize(140, 40)
        self.serach_btn.clicked.connect(self.show_spinner_and_load_dataes)
        self.serach_btn.setStyleSheet('''
            QPushButton {
                background-color: #2251DB;
                font-family: "B Nazanin";
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
        ##add btn
        self.add_btn.setMinimumSize(70,20)
        self.add_btn.setMaximumSize(120,35)
        self.add_btn.clicked.connect(self.open_new_form)
        self.add_btn.setText(" ثبت محصول")
        self.add_icon= QIcon(self.get_asset_path("MacOS Maximize.png"))
        self.add_btn.setIcon(self.add_icon)
        self.add_btn.setIconSize(QtCore.QSize(25,25))
        self.add_btn.setStyleSheet('''
            QPushButton {
                background-color: #2251DB;
                font-family: "Mirza";
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-left: 5px;
                margin-right:10px;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
        ##new btn
        self.new_btn.setMinimumSize(70,20)
        self.new_btn.setMaximumSize(120,35)
        self.new_btn.setText(" افزودن محصول")
        self.new_icon= QIcon(self.get_asset_path("MacOS Maximize.png"))
        self.new_btn.clicked.connect(self.open_add_form)
        self.new_btn.setIcon(self.new_icon)
        self.new_btn.setIconSize(QtCore.QSize(25,25))
        self.new_btn.setStyleSheet('''
             QPushButton {
                background-color: #2251DB;
                font-family: "Mirza";
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-left: 5px;
                
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
    ##
    def set_today_date(self):
        today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_label.setText(f"تاریخ: {today_jalali}")
        self.date_label.setMinimumHeight(30)
        self.date_label.setMaximumHeight(70)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_label.setStyleSheet('''
            font-size: 18px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
            margin-left:20px
        ''')

    def set_today_time(self):
        weekdays_fa = {
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌ شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج ‌شنبه',
            'Friday': 'جمعه',
        }
        weekday_en = jdatetime.date.today().togregorian().strftime("%A")
        weekday_fa = weekdays_fa.get(weekday_en, 'نامشخص')

        self.time_label.setText(f"امروز: {weekday_fa}")
        self.time_label.setMinimumHeight(30)
        self.time_label.setMaximumHeight(50)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.time_label.setStyleSheet('''
            font-size: 16px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-left:30px;
        ''')
    ##spinner
    def start_auto_refresh(self):
        self.refresh_timer= QTimer(self)
        self.refresh_timer.timeout.connect(self.show_first_spinner) 
        self.refresh_timer.start(15 * 60 *1000)
    ##
    def show_first_spinner(self):
        self.clear_products()
        self.show_spinner_and_load_data()
   ##
    def show_spinner_and_load_data(self):
        # نمایش spinner
        spinner_wrapper = QWidget()
        spinner_layout = QVBoxLayout(spinner_wrapper)
        spinner_layout.setContentsMargins(0, 100, 0, 100)
        spinner_layout.addStretch()

        self.spinner = CircularSpinner(self)
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        spinner_layout.addStretch()

        self.box_layout.addWidget(spinner_wrapper, 0, 0, 1, 2)

        # شروع بارگذاری داده‌ها
        QTimer.singleShot(100, self.run_data_loader)
    ##
    def run_data_loader(self):
        self.thread = DataLoaderThread()
        self.thread.data_loaded.connect(self.on_data_loaded)
        self.thread.error_occurred.connect(self.on_data_error)
        self.thread.start()

    ##
    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data
        except Exception as e:
            print("خطا در دریافت config:", e)
            return None
    
    ##
    def on_data_loaded(self, product_list):
        # زمانی که داده‌ها بارگذاری شدند
        has_internet = self.get_db_config() is not None

        for index, data in enumerate(product_list):
            product_box = ProductBox()

            image_path = None
            if data["image_path"]:
                if has_internet:
                    image_path = self.download_image_from_url(data["image_path"])
                    if image_path is None:
                        # اگر دانلود موفق نبود، از فولدر temp_images استفاده کن
                        image_path = self.load_image_from_temp(data["image_path"])
                else:
                    image_path = self.load_image_from_temp(data["image_path"])

            product_box.set_product_info(
                name=data["name"],
                barcode=data["barcode"],
                buy_price=data["buy_price"],
                sale_price=data["sale_price"],
                number=data["quantity"],
                expire_date=data["expire_date"],
                big_sub= data["big_sub_display"],
                big_price= data["big_price"],
                image_path=image_path
            )

            row, col = divmod(index, 4)
            self.box_layout.addWidget(product_box, row, col)

        # متوقف کردن spinner بعد از بارگذاری داده‌ها
        self.spinner.stop()
    ##
    def on_data_error(self, error):
        # در صورت بروز خطا، spinner را متوقف کنید
        self.spinner.stop()

        # نمایش پیام خطا
        print(f"❌ خطا در بارگذاری داده‌ها: {error}")
        self.show_error_message(error)

    def show_error_message(self, error):
        # نمایش پیام خطا در صورت بروز مشکل
        print(f"خطا: {error}")
        ##
    ##
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

            # ✅ بررسی کش - اگر فایل قبلاً دانلود شده باشد، مستقیماً بازگردانده می‌شود
            if os.path.exists(local_path):
                print("📦 تصویر قبلاً دانلود شده. بارگیری از حافظه محلی:", local_path)
                return local_path

            # اضافه کردن هدرهای مناسب برای درخواست
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(image_path, headers=headers, timeout=20)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print("✅ تصویر با موفقیت دانلود شد:", local_path)
            return local_path

        except Exception as e:
            print("❌ خطا در دریافت تصویر از URL:", e)
            default_image_path = os.path.join(os.getcwd(), "default.png")
            if os.path.exists(default_image_path):
                print("🔁 بازگشت به تصویر پیش‌فرض:", default_image_path)
                return default_image_path
            else:
                print("⚠️ تصویر پیش‌فرض پیدا نشد.")
                return None
    ##
    def load_image_from_temp(self, image_relative_path):
        """
        فقط تصویر را از فولدر temp_images بارگذاری می‌کند.
        اگر وجود نداشت، تصویر پیش‌فرض را بازمی‌گرداند.
        """
        try:
            if not image_relative_path:
                raise ValueError("مسیر تصویر نامعتبر است.")

            filename = os.path.basename(image_relative_path)
            temp_dir = os.path.join(os.getcwd(), "temp_images")
            local_path = os.path.join(temp_dir, filename)

            if os.path.exists(local_path):
                return local_path

            # اگر عکس نبود، تصویر پیش‌فرض
            fallback = os.path.join(os.getcwd(), "default.png")
            if os.path.exists(fallback):
                return fallback
            else:
                print("❌ تصویر پیش‌فرض یافت نشد.")
                return None

        except Exception as e:
            print("❌ خطا در بارگذاری تصویر از temp_images:", e)
            return None

    ##search actions
    def show_spinner_and_load_dataes(self):
        text = self.search_line.text().strip()

        # اگر متن خالی است و سرچ هنوز آغاز نشده، جلوی اجرا را بگیر
        if not text:
            if not hasattr(self, 'search_initialized'):
                self.search_initialized = False

            if not self.search_initialized:
                return  # 👈 جلوی اجرای اولیه هنگام باز شدن برنامه را می‌گیرد

            self.clear_products()
            self.load_all_products(show_spinner=False)
            return

        # اکنون سرچ فعال می‌شود چون کاربر چیزی تایپ کرده
        self.search_initialized = True

        self.clear_products()

        self.spinner_wrapper = QWidget()
        spinner_layout = QVBoxLayout(self.spinner_wrapper)
        spinner_layout.setContentsMargins(0, 100, 0, 100)
        spinner_layout.addStretch()

        self.spinner = CircularSpinner(self)
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        spinner_layout.addStretch()

        self.box_layout.addWidget(self.spinner_wrapper, 0, 0, 1, 2)

        QTimer.singleShot(100, self.live_search)

    def live_search(self):
        text = self.search_line.text().strip()
        if not text:
            return  # چون در show_spinner_and_load_datas بررسی شده

        self.search_thread = SearchThread(text)
        self.search_thread.data_loaded.connect(self.show_products)
        self.search_thread.error_occurred.connect(self.show_error)
        self.search_thread.start()


    def show_products(self, product_list):
        # حذف اسپینر
        if self.spinner_wrapper:
            self.spinner_wrapper.setParent(None)
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None

        for index, data in enumerate(product_list):
            image_path = None
            if data["image_path"]:
                image_path = data["image_path"]  # فقط استفاده از مسیر ذخیره‌شده در temp_images

            product_box = ProductBox()
            product_box.set_product_info(
                name=data["name"],
                barcode=data["barcode"],
                buy_price=data["buy_price"],
                sale_price=data["sale_price"],
                number=data["quantity"],
                expire_date=data["expire_date"],
                big_sub= data["big_sub_display"],
                big_price= data["big_price"],
                image_path=image_path
            )
            row, col = divmod(index, 4)
            self.box_layout.addWidget(product_box, row, col)


    def show_error(self, msg):
        if self.spinner_wrapper:
            self.spinner_wrapper.setParent(None)
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None

        MessageBox(text=msg, title="❌ خطا", type="error").show()
    
    ##
    def data_full_loaded(self):
        try:
            conn = sqlite3.connect('Data\\sh_online.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users LIMIT 1")
            c_row = cursor.fetchone()
            id_user = c_row[0]
            if not id_user:
                self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                return

            cursor.execute('''
                SELECT name, barcode, buy_price, sale_price, quantity, expire_date,big_price,big_sub_display, image_path
                FROM products
                WHERE user_id = ?
            ''', (id_user,))
            products = cursor.fetchall()
            
            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)

            product_list = []
            for product in products:
                name, barcode, buy_price, sale_price, quantity, exp_date,big_price,big_sub_display, image_path = product

                # بررسی وجود عکس
                if image_path:
                    full_image_path = os.path.join(temp_dir, os.path.basename(image_path))
                    if not os.path.exists(full_image_path):
                        try:
                            with open(image_path, 'rb') as src_file:
                                with open(full_image_path, 'wb') as dst_file:
                                    dst_file.write(src_file.read())
                        except Exception as img_err:
                            print(f"❌ خطا در کپی تصویر: {img_err}")
                    image_path = full_image_path

                product_info = {
                    "name": name,
                    "barcode": barcode,
                    "buy_price": buy_price,
                    "sale_price": sale_price,
                    "quantity": quantity,
                    "expire_date": exp_date,
                    "big_sub_display" : big_sub_display,
                    "big_price" : big_price,
                    "image_path": image_path
                }
                product_list.append(product_info)

            # 👈 اینجا نمایش در UI:
            self.Full_data_load(product_list)

        except Exception as e:
            print(str(e))
        except sqlite3.Error as e:
            MessageBox(f"{e}: خطا در بارگذاری اطلاعات", title="خطا", type="error")
        finally:
            if conn:
                conn.close()

    ##
    def Full_data_load(self,product_list): 
        # حذف اسپینر
        if self.spinner_wrapper:
            self.spinner_wrapper.setParent(None)
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None
        
        for index, data in enumerate(product_list):
                    image_path = None
                    if data["image_path"]:
                        image_path = data["image_path"]  # فقط استفاده از مسیر ذخیره‌شده در temp_images

                    product_box = ProductBox()
                    product_box.set_product_info(
                        name=data["name"],
                        barcode=data["barcode"],
                        buy_price=data["buy_price"],
                        sale_price=data["sale_price"],
                        number=data["quantity"],
                        expire_date=data["expire_date"],
                        big_sub= data["big_sub_display"],
                        big_price= data["big_price"],
                        image_path=image_path
                    )
                    row, col = divmod(index, 4)
                    self.box_layout.addWidget(product_box, row, col)


    def clear_products(self):
        while self.box_layout.count():
            child = self.box_layout.takeAt(0)
            widget = child.widget()
            if widget:
                if hasattr(widget, 'image_path') and widget.image_path and os.path.exists(widget.image_path):
                    try:
                        os.remove(widget.image_path)
                    except Exception as e:
                        print("حذف فایل ناموفق:", e)
                widget.deleteLater()

    def load_all_products(self, show_spinner=True):
        self.clear_products()

        if show_spinner:
            self.spinner_wrapper = QWidget()
            spinner_layout = QVBoxLayout(self.spinner_wrapper)
            spinner_layout.setContentsMargins(0, 100, 0, 100)
            spinner_layout.addStretch()

            self.spinner = CircularSpinner(self)
            spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
            spinner_layout.addStretch()

            self.box_layout.addWidget(self.spinner_wrapper, 0, 0, 1, 2)

        self.data_full_loaded()

    ##
    def on_data_error(self, error_message):
        if self.spinner:
            self.spinner.setParent(None)
            self.spinner.deleteLater()
            self.spinner = None

        MessageBox(text=error_message, title="❌ خطا", type="error").show()
    # #images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ###
    def open_new_form(self):
        from new_p import ProductForm  # 🔥 اینجا ایمپورت می‌کنیم، نه بالا
        form = ProductForm(inventory_page=self)
        form.exec()
    ### insert
    def start_auto_sync_timer(self):
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.start_sync_thread)
        self.sync_timer.start(5 * 60 * 1000)  # هر 5 دقیقه

    def start_sync_thread(self):
        from new_p import ProductForm
        products= ProductForm(inventory_page=self)
        sync_thread = threading.Thread(target=products.sync_to_server)
        sync_thread.setDaemon(True)  # اگر پنجره بسته شد، ترد هم بسته شود
        sync_thread.start()
    ###update
    def start_synced_to_server(self):
        self.synced_timer= QTimer(self)
        self.synced_timer.timeout.connect(self.start_synced_to_thread)
        self.synced_timer.start(2 *60 *1000)

    def start_synced_to_thread(self):
        from add_p import AddProduct
        add_pro= AddProduct(inventory_page=self)
        synced_thread= threading.Thread(target=add_pro.synced_to_server)
        synced_thread.setDaemon(True)
        synced_thread.start()
    ##
    def open_add_form(self):
        from add_p import AddProduct
        form= AddProduct(inventory_page=self)
        form.exec()
    ##fonts
    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")

        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return

        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf",".TTF")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        pass
    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)

    ##
    def start_notification_checker(self):
        self.notif_checker = NotificationChecker()
        self.notif_checker.new_message.connect(self.show_notification_message)  # بدون ()
        self.notif_checker.start()

    def show_notification_message(self, pro_name: str, message: str):
        notif = Notification(
            pro_name=pro_name,
            message=message,
            parent_frame=self.notification_frame,
            icon_path=self.get_asset_path("alarm.png")
        )
        notif.show()
