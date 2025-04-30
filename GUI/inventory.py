from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QFileDialog,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtCore import Qt,QTimer,QThread, pyqtSignal
from PyQt6.QtGui import QColor,QIcon,QPixmap
from PyQt6 import QtCore
import jdatetime
import os
import requests
from message_b import MessageBox
from circle import CircularSpinner
import uuid
import pymysql
from info_box import ProductBox

from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QGridLayout
)
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
            response = requests.get(url, headers=headers, timeout=5)
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

        try:
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

            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)

            product_list = []
            for product in products:
                name, barcode, buy_price, sale_price, quantity, exp_date, image_data = product

                image_path = None
                if image_data:
                    filename = f"{uuid.uuid4().hex}.jpg"
                    image_path = os.path.join(temp_dir, filename)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

                product_info = {
                    "name": name,
                    "barcode": barcode,
                    "buy_price": buy_price,
                    "sale_price": sale_price,
                    "quantity": quantity,
                    "expire_date": exp_date,
                    "image_path": image_path
                }
                product_list.append(product_info)

            self.data_loaded.emit(product_list)

        except Exception as e:
            self.error_occurred.emit(f"خطا در بارگذاری محصولات: {e}")

        finally:
            if conn:
                conn.close()

    def run(self):
        self.load_all_data()
    
class Inventory(QFrame):
    def __init__(self):
        super().__init__()
        self.spinner = None
        self.should_show_spinner = True  # ✅ شرط اولیه True
        self.init_ui()
        self.label_UI()
        self.field_UI()
        self.set_today_date()
        self.set_today_time()
        self.button_UI()
        self.show_spinner_and_load_data()


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

        #scroll_layout.addLayout(top_layout)

        # دکمه‌ها
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        #scroll_layout.addLayout(button_layout)
        scroll_layout.addSpacing(20)  # فضای بیشتر بین دکمه‌ها و جعبه‌ها

        # لایه جعبه‌ها (ProductBoxها)
        self.box_layout = QGridLayout()
        self.box_layout.setSpacing(15)
        scroll_layout.addLayout(self.box_layout)

        scroll_layout.addStretch()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_layout.addWidget(scroll_area)
       

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")
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
    ##spinner 
    def show_spinner_and_load_data(self):
        spinner_wrapper = QWidget()
        spinner_layout = QVBoxLayout(spinner_wrapper)
        spinner_layout.setContentsMargins(0, 100, 0, 100)
        spinner_layout.addStretch()

        self.spinner = CircularSpinner(self)
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        spinner_layout.addStretch()

        self.box_layout.addWidget(spinner_wrapper, 0, 0, 1, 2)

        QTimer.singleShot(100, self.run_data_loader)
    ##
    def run_data_loader(self):
        self.thread = DataLoaderThread()
        self.thread.data_loaded.connect(self.on_data_loaded)
        self.thread.error_occurred.connect(self.on_data_error)
        self.thread.start()

    def on_data_loaded(self, product_list):
        if self.spinner:
            self.spinner.setParent(None)
            self.spinner.deleteLater()
            self.spinner = None

        for index, data in enumerate(product_list):
            product_box = ProductBox()
            product_box.set_product_info(
                name=data["name"],
                barcode=data["barcode"],
                buy_price=data["buy_price"],
                sale_price=data["sale_price"],
                number=data["quantity"],
                expire_date=data["expire_date"],
                image_path=data["image_path"]
            )
            row, col = divmod(index, 4)
            self.box_layout.addWidget(product_box, row, col)

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
    ##open box_frames
    def open_new_form(self):
        from new_p import ProductForm  # 🔥 اینجا ایمپورت می‌کنیم، نه بالا
        form = ProductForm(inventory_page=self)
        form.exec()


