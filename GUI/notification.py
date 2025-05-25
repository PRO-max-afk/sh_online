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
from circle import CircularSpinner
from notifi_box import Notification
from m_dec import Decrease
from m_de import Stock
from notifi_info import Notifi_Box
from notifi_check import NotificationChecker
from notifi_box import Notification
from notifi_ch import ExpirationNotifier
import pymysql
from info_box import ProductBox
from mini_box import MniniBox
from persiantools.jdatetime import JalaliDate
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt


class Frame2(QFrame):
    def __init__(self):
        super().__init__()
        self.spinner= None
        self.init_ui()
        self.label_UI()
        self.button_UI()
        self.field_UI()
        self.set_today_date()
        self.set_today_time()
        self.start_notification_checker()
        self.show_first_spinner()


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
        ##widgets
        self.label = QLabel("لیست هشدار های برنامه", self)
        self.search_line = QLineEdit(self)
        self.serach_btn = QPushButton("جستجو", self)
        ##
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.search_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.serach_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

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
        ##box layouts
        mini_box= QHBoxLayout()
        ##top boxes
        self.mini_info= MniniBox()
        self.decrease= Decrease() 
        self.stock= Stock()
        ##
        mini_box.addWidget(self.stock)
        mini_box.addWidget(self.decrease)
        mini_box.addWidget(self.mini_info)
    
        # لایه جعبه‌ها
        self.box_layout = QGridLayout()
        self.box_layout.setSpacing(10)
        scroll_layout.addLayout(self.box_layout)
        scroll_layout.addStretch()

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(mini_box)
        main_layout.addSpacing(10)
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
        #self.search_line.textChanged.connect(self.show_spinner_and_load_dataes)
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
        #
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.search_line.setGraphicsEffect(shadow)

    def button_UI(self):
        self.serach_btn.setMinimumSize(100, 30)
        self.serach_btn.setMaximumSize(140, 40)
        #self.serach_btn.clicked.connect(self.show_notification)
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
    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)
    
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
    ##
    def show_first_spinner(self):
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

        self.box_layout.addWidget(spinner_wrapper)

        # شروع بارگذاری داده‌ها
        QTimer.singleShot(100, self.run_data_loader)
    ##
    def run_data_loader(self):
        self.notifier = ExpirationNotifier()
        self.notifier.new_expired_info.connect(self.show_nt)
        self.notifier.expired_count_signal.connect(self.show_exp)
        self.notifier.start()
    ##
    def show_nt(self, products: list):
        # پاک کردن ویجت‌های قبلی در layout
        for i in reversed(range(self.box_layout.count())):
            widget = self.box_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # اضافه کردن محصولات جدید
        for product in products:
            notif = Notifi_Box()

            # دریافت مسیر محلی عکس با استفاده از متد دانلود
            image_path = self.download_image_from_url(product.get("product_image", ""))

            notif.set_product_info(
                name=product.get("product_name", ""),
                number=str(product.get("quantity", "")),
                expire_date=str(product.get("expiration_dates", "")),
                image_path=image_path or ""  # استفاده از تصویر دانلود شده یا مسیر خالی
            )

            self.box_layout.addWidget(notif)


    def show_exp(self, count):
        self.decrease.set_product_info(number=str(count))

    
    # #images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
     ##notifications
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
