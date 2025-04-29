from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QFileDialog,
    QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor,QIcon,QPixmap
from PyQt6 import QtCore
import jdatetime
import os
import requests
from message_b import MessageBox
import uuid
import pymysql
from info_box import ProductBox


class Inventory(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.field_UI()
        self.set_today_date()
        self.set_today_time()
        self.button_UI()
        self.load_all_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # تاریخ و زمان
        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("لیست محصولات فروشگاه", self)
        self.search_line = QLineEdit(self)
        self.serach_btn = QPushButton("جستجو", self)
        self.add_btn= QPushButton()
        self.new_btn= QPushButton()

        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.search_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.serach_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.new_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.serach_btn)
        top_layout.addWidget(self.search_line, stretch=3)
        top_layout.addWidget(self.label, stretch=1)
        
        button_layout= QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.new_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        ##box
        self.box_layout= QHBoxLayout()
        #self.box_layout.addWidget(info_box)
        self.box_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        ##
        self.db_data= self.get_db_config()

        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(self.box_layout)
        main_layout.addStretch()
    
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")

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
    # دریافت اطلاعات دیتابیس از سرور
    def get_db_config(self):
        try:
            url = "https://aryaict.com/connect.php"  # URL فایل PHP
            headers = {
                'Accept': 'application/json',  # اعلام انتظار پاسخ به صورت JSON
                'User-Agent': 'MyApp/1.0',  # اضافه کردن هدر User-Agent
            }
            response = requests.get(url, headers=headers, timeout=1)
            response.raise_for_status()  # بررسی خطا در پاسخ

            # بررسی اینکه پاسخ به صورت JSON است
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            # دریافت داده‌ها به‌صورت JSON
            data = response.json()

            # بررسی وجود کلیدهای مورد نیاز
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data  # بازگشت دیکشنری حاوی اطلاعات دیتابیس

        except requests.Timeout:
            print("⏳ اتصال به سرور زمان زیادی برد")
        except requests.RequestException as e:
            print(f"⚠️ خطای درخواست: {e}")
            print(f"کد وضعیت: {response.status_code}")  # اضافه کردن کد وضعیت برای بررسی خطا
            print(f"متن پاسخ: {response.text}")  # نمایش متن پاسخ برای بررسی بیشتر
        except ValueError as e:
            print(f"🚨 خطای JSON: {e}")

        return None
    ## 
    def load_all_data(self):
        if not self.db_data:
            MessageBox(text="لطفاً اینترنت خود را بررسی کنید❌ اتصال به سرور ناموفق بود", title="❌خطا", type="error").show()
            return False

        conn = None
        cursor = None

        try:
            # اتصال به دیتابیس اصلی (MySQL)
            conn = pymysql.connect(
                host=self.db_data["host"],
                user=self.db_data["user"],
                password=self.db_data["password"],
                database=self.db_data["database"]
            )
            cursor = conn.cursor()

            cursor.execute('''
                SELECT product_name, barcode, buy_price, sell_price, quantity, expiration_dates, product_image
                FROM inventories
                ORDER BY invent_id DESC
            ''')
            products = cursor.fetchall()

            # ساخت پوشه temp_images اگر وجود ندارد
            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)

            for product in products:
                name, barcode, buy_price, sale_price, quantity, exp_date, image_data = product

                image_path = None
                if image_data:
                    # تولید یک نام تصادفی برای فایل عکس
                    filename = f"{uuid.uuid4().hex}.jpg"
                    image_path = os.path.join(temp_dir, filename)

                    # ذخیره کردن فایل روی دیسک
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

                product_box = ProductBox()
                product_box.set_product_info(
                    name=name,
                    barcode=barcode,
                    buy_price=buy_price,
                    sale_price=sale_price,
                    number=quantity,
                    expire_date=exp_date,
                    image_path=image_path  # مسیر عکس جدید که ساخته‌ایم
                )
                self.box_layout.addWidget(product_box)

        except Exception as e:
            MessageBox(text=f"خطا در بارگذاری محصولات: {e}", title="❌ خطا", type="error").show()

        finally:
            if conn:
                conn.close()
    
    # #images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ##open box_frames
    def open_new_form(self):
        from new_p import ProductForm  # 🔥 اینجا ایمپورت می‌کنیم، نه بالا
        form = ProductForm(inventory_page=self)
        form.exec()


