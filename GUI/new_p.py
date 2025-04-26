from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget,QMessageBox)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
import jdatetime
from profile_picture import ProfileImage
from PyQt6.QtCore import Qt,QPropertyAnimation,QEasingCurve
from PyQt6 import QtCore
import os
from calendars import JalaliCalendar
import requests
import pymysql
import subprocess
class ProductForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 ثبت محصول جدید")
        self.resize(929, 630)
        self.setFixedSize(929, 630)  # جلوگیری از تغییر اندازه
        self.setStyleSheet("background-color: #E8E6E6;")
        

        self.center_window()  # <-- وسط‌چین کردن
        # نمونه ویجت تستی
        self.title_lb = QLabel("ثبت محصولات جدید",self)
        # 🔵 عکس پروفایل با کیفیت و کلیک‌پذیر
        profile_image_path = self.get_asset_path("ChatGPT Image Apr 14, 2025, 04_02_55 PM.png")  # مسیر پیش‌فرض عکس
        self.profile_widget = ProfileImage(profile_image_path, 70, self)
        self.profile_widget.setGeometry(850,14,0,0)
        self.date_lb= QLabel("",self)
        
        self.set_today_date()
        self.add_horizontal_line()
        ##
        self.cate_lb= QLabel("دسته بندی محصول:", self)
        self.choise_c= QComboBox(self)
        ##
        self.under_ct= QLabel("نوعیت محصول:",self)
        self.under_choise= QComboBox(self)
       ##
        self.name_lb= QLabel("نام محصول:", self)
        self.name_line= QLineEdit(self)
        ##
        self.bar_lb= QLabel("بارکد محصول:",self)
        self.bar_line= QLineEdit(self)
        ##
        self.exp_name= QLabel("تاریخ انقضاء:", self)
        self.exp_line= QLineEdit(self)
        self.exp_line.setReadOnly(True)
        ##
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.jalali_calendar = JalaliCalendar(self)
        self.jalali_calendar.setMaximumHeight(0)  # در ابتدا بسته باشد
        self.layout.addWidget(self.jalali_calendar)
        ##
        self.category= QLabel("کتگوری عمده:",self)
        self.cate_ch= QComboBox(self)
        
        ##
        self.buy_price= QLabel("قیمت خرید:",self)
        self.buy_line= QLineEdit(self)
        ##
        self.number_lb= QLabel("تعداد محصول:", self)
        self.number_line= QLineEdit(self)
        ##
        self.sale_price= QLabel("قیمت فروش:", self)
        self.sale_line= QLineEdit(self)
        ##
        self.sale_big= QLabel("قیمت عمده:",self)
        self.sale_big_line= QLineEdit(self)
        ##
        self.img_preveiw= QLabel(self)
        ##
        self.picture_btn= QPushButton(self)
        self.submit_btn= QPushButton(self)
        self.calendar_btn= QPushButton(self)
        ##
        self.name_category= ["انتخاب","مواد غذایی","نوشیدنی","لوازم خانه گی و آشپزخانه","لوازم برقی و الکترونیکی","لوازم کودک و اسباب بازی"]
        self.under_cate= []
        ##
        self.lable_UI()
        self.enties_UI()
        self.Button_UI()
        self.under_category()
        self.db_connection= self.get_db_config()

    def center_window(self):
        """مرکز کردن پنجره روی صفحه"""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2))

    ##
    def lable_UI(self):
        self.title_lb.setGeometry(360,15,150,20)
        self.title_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 20px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.date_lb.setGeometry(17,42,120,18)
        self.date_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 17px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.cate_lb.setGeometry(745,115,150,20)
        self.cate_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.under_ct.setGeometry(450,115,153,20)
        self.under_ct.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.bar_lb.setGeometry(480,200,115,20)
        self.bar_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.name_lb.setGeometry(776,200,115,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.exp_name.setGeometry(776,300,120,20)
        self.exp_name.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.category.setGeometry(480,300,120,20)
        self.category.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.buy_price.setGeometry(776,400,120,20)
        self.buy_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.number_lb.setGeometry(480,400,120,20)
        self.number_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.sale_price.setGeometry(776,495,120,20)
        self.sale_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
            ''')
        ##
        self.sale_big.setGeometry(480,495,120,20)
        self.sale_big.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
            ''')
        ##
        self.img_preveiw.setGeometry(20,191,221,238)
        self.img_preveiw.setScaledContents(True)
        self.img_preveiw.setStyleSheet('''
        background-color: transparent;
        border: 1px solid #1646B5;
        ''')
        ##
    ##
    def enties_UI(self):
        self.choise_c.setGeometry(653, 150, 250, 45)
        self.choise_c.addItems(self.name_category)
        self.choise_c.setCurrentText(self.name_category[0])
        self.choise_c.currentTextChanged.connect(self.under_category)
        self.choise_c.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.choise_c.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 15px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px; /* فضای کافی برای فلش در سمت چپ */
                padding-left: 77px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: white;  /* پس‌زمینه سفید */
                color: black;             /* متن سیاه */
                text-align: left;        /* تراز متن به راست */
                font-family: "B Nazanin";
                font-size: 15px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;  /* رنگ انتخاب آیتم */
            }
        ''')
        ##
        self.under_choise.setGeometry(355,150,250,45)
        self.under_choise.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.under_choise.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 15px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px; /* فضای کافی برای فلش در سمت چپ */
                padding-left: 100px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: white;  /* پس‌زمینه سفید */
                color: black;             /* متن سیاه */
                text-align: left;        /* تراز متن به راست */
                font-family: "B Nazanin";
                font-size: 15px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;  /* رنگ انتخاب آیتم */
            }
        ''')

        ##
        self.name_line.setGeometry(653,230,250,45)
        self.name_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
        ##
        self.bar_line.setGeometry(355,230,250,45)
        self.bar_line.setStyleSheet('''
            background-color: white;
            font-family: Arial;
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            color: black;
            padding: 7px;
        ''')
        ##
        self.exp_line.setGeometry(653,330,250,45)
        self.exp_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
        ##
        self.cate_ch.setGeometry(355,330,250,45)
        self.cate_ch.addItems(["انتخاب","دانه","کارتن","بسته","کیسه","شانه","جعبه"])
        self.cate_ch.setCurrentText("انتخاب")
        self.cate_ch.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.cate_ch.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 16px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px; /* فضای کافی برای فلش در سمت چپ */
                padding-left: 170px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 25px;
                height: 25px;
            }

            QComboBox QAbstractItemView {
                background-color: white;  /* پس‌زمینه سفید */
                color: black;             /* متن سیاه */
                text-align: left;        /* تراز متن به راست */
                font-family: "B Nazanin";
                font-size: 15px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;  /* رنگ انتخاب آیتم */
            }
        ''')
        ##
        self.buy_line.setGeometry(653,430,250,45)
        self.buy_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')
        ##
        self.number_line.setGeometry(355,430,250,45)
        self.number_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
        ##
        self.sale_line.setGeometry(653,520,250,45)
        self.sale_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
        ##
        self.sale_big_line.setGeometry(355,520,250,45)
        self.sale_big_line.setStyleSheet('''
            background-color: white;
            font-family: B Nazanin,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')

    ##
    def Button_UI(self):
        self.submit_btn.setGeometry(445,571,358,45)
        self.sub_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.submit_btn.setIcon(self.sub_icon)
        self.submit_btn.setIconSize(QtCore.QSize(36,36))
        self.submit_btn.setText("ثبت محصول")
        self.submit_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.submit_btn.setStyleSheet('''
            QPushButton {
                background-color: #3EB516;
                font-family: "Mirza";
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-right: 120px; /* فاصله‌ی داخلی سمت راست */
                padding-left: 125px;  /* فاصله‌ی داخلی سمت چپ */
                qproperty-iconSize: 32px;

            }
            QPushButton:hover {
                background-color: #84E963;  
            }
            QPushButton:pressed {
                background-color: #3EB516;
            }
        ''')
        ##
        self.picture_btn.setGeometry(40,134,155,43)
        self.picture_icon= QIcon(self.get_asset_path("Camera.png"))
        self.picture_btn.setIcon(self.picture_icon)
        self.picture_btn.setIconSize(QtCore.QSize(35,35))
        self.picture_btn.setText("  انتخاب عکس")
        self.picture_btn.clicked.connect(self.select_image)
        self.picture_btn.setStyleSheet('''
             QPushButton {
                background-color: #2251DB;
                font-family: "Mirza";
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
        ##
        self.calendar_btn.setGeometry(870,337,30,30)
        self.cale_icon= QIcon(self.get_asset_path("calendar_8265298.png"))
        self.calendar_btn.setIcon(self.cale_icon)
        self.calendar_btn.setIconSize(QtCore.QSize(30,30))
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 10px;
                border-radius: 12px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        self.calendar_btn.clicked.connect(self.show_calendar)
    ##
    def set_today_date(self):
        today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_lb.setText(f"تاریخ: {today_jalali}")
    ##line
    def add_horizontal_line(self):
        self.line = QFrame(self)
        self.line.setGeometry(15, 90, 900, 1)  # مکان: زیر date_lb با عرض 900
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("color: white; background-color: white;")
    ##
    def under_category(self):
        selected = self.choise_c.currentText()
        self.under_choise.clear()

        if selected == "مواد غذایی":
            self.under_cate = ["انتخاب", "خوارکی ها", "سبزیجات و میوه ها", "گوشت و ماهی", "روغن و چربی ها","خشکبار و مغزیجات","حبوبات","لبنیات"]
        elif selected == "نوشیدنی":
            self.under_cate = ["انتخاب","چای","قهوه","نوشیدنی انرژی زا","نوشابه و آبمیوه ها"]
        elif selected == "لوازم خانه گی و آشپزخانه":
            self.under_cate = ["انتخاب","ظرف", "قاشق و چنگال", "دستمال", "سرویس آشپزخانه"]
        elif selected == "لوازم برقی و الکترونیکی":
            self.under_cate = ["انتخاب","تلویزیون", "یخچال", "ماشین لباسشویی", "پنکه"]
        elif selected == "لوازم کودک و اسباب بازی":
            self.under_cate = ["انتخاب","عروسک", "ماشین بازی", "لگو", "توپ"]
        elif selected== "انتخاب":
            self.under_cate= ["انتخاب"]
        else:
            self.under_cate = []

        self.under_choise.addItems(self.under_cate)
    ##
    def show_calendar(self):
        self.calendar_popup = JalaliCalendar(self)
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomRight())
        self.calendar_popup.show_with_animation(pos)
    ##fonts
    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")

        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return

        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        pass

    ##
    def set_selected_date(self, date_str):
        self.exp_line.setText(date_str)
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ##
    def select_image(self):
        file_path, _= QFileDialog.getOpenFileName(self,"انتخاب تصویر محصول","", "images(*.png *.jpg *.jpeg)")
        if file_path:
            self.img_preveiw.setPixmap(QPixmap(file_path))
            self.img_path= file_path
    # دریافت اطلاعات دیتابیس از سرور
    def get_db_config(self):
        try:
            url = "https://aryaict.com//connect"  # URL فایل PHP
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
    def insert_product(self):
        pass
       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductForm()
    window.show()
    sys.exit(app.exec())
