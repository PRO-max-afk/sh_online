from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
import jdatetime
import datetime 
from datetime import date
from profile_picture import ProfileImage
from info_box import ProductBox
from message_b import MessageBox
from more_details import MoreDetails
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os
import cv2
import numpy as np
from calendars import JalaliCalendar
from c_calendar import Calendar
import requests
import pymysql
import sqlite3
from  ftplib import FTP
import ntpath
from PIL import Image

class ProductForm(QDialog):
    def __init__(self,inventory_page):
        super().__init__()
        self.setWindowTitle("📦 ثبت محصول جدید")
        self.resize(929, 630)
        self.setFixedSize(929, 630)  # جلوگیری از تغییر اندازه
        self.setStyleSheet("background-color: #E8E6E6;")
        self.inventory_page= inventory_page
        

        self.center_window()  # <-- وسط‌چین کردن
        self.load_all_fonts()
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
        self.jalali_calendar = Calendar(self)
        self.jalali_calendar.setMaximumHeight(0)  # در ابتدا بسته باشد
        self.layout.addWidget(self.jalali_calendar)
        ##
        self.category= QLabel("کتگوری عمده:",self)
        self.cate_ch= QComboBox(self)
        ##
        self.unit_label = None
        self.unit_lineedit = None
        self.cate_ch.currentTextChanged.connect(self.public_category)
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
        self.total_label= QLabel("مجموعه:",self)
        self.total_line= QLabel("0.00",self)
        ### event
        self.buy_line.textEdited.connect(self.calculate_total)
        self.number_line.textEdited.connect(self.calculate_total)

        ##
        self.picture_btn= QPushButton(self)
        self.submit_btn= QPushButton(self)
        self.calendar_btn= QPushButton(self)
        self.details_btn= QPushButton(self)
        ##
        self.name_category= ["انتخاب","مواد غذایی","نوشیدنی","لوازم خانه گی و آشپزخانه","لوازم برقی و الکترونیکی","لوازم کودک و اسباب بازی"]
        self.under_cate= []
        ##
        self.lable_UI()
        self.enties_UI()
        self.Button_UI()
        self.under_category()
    
    ###
    def center_window(self):
        """مرکز کردن پنجره روی صفحه"""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2))
    ##
    def calculate_total(self):
        buy_price = self.buy_line.text().strip()
        quantity = self.number_line.text().strip()

        if buy_price and quantity:
            try:
                total = float(buy_price) * float(quantity)
                self.total_line.setText(f'{total:.2f}')
            except ValueError:
                self.total_line.setText("0.00")  # اگر کاربر متن اشتباهی مثل حروف وارد کند، خروجی خالی بماند
        else:
            self.total_line.setText("")  # اگر یکی از فیلدها خالی بود، خروجی خالی شود
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
        self.total_label.setGeometry(152,577,60,20)
        self.total_label.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.total_line.setGeometry(90,573,70,30)
        self.total_line.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 15px;
            font-weight: bold;
            color: black;
            text-align: center;
        ''')
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
        self.exp_line.setAlignment(Qt.AlignmentFlag.AlignRight)
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
        self.cate_ch.addItems(["انتخاب","دانه","کیلو","کارتن","بسته","کیسه","شانه","جعبه"])
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
        self.submit_btn.clicked.connect(self.insert_product)
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
        self.calendar_btn.setGeometry(660,337,30,30)
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
        self.details_btn.setGeometry(38,461,155,43)
        self.details_icon= QIcon(self.get_asset_path("View Details.png"))
        self.details_btn.setIcon(self.details_icon)
        self.details_btn.setIconSize(QtCore.QSize(35,35))
        self.details_btn.clicked.connect(self.open_details)
        self.details_btn.setText("  جزئیات بیشتر")
        self.details_btn.setStyleSheet('''
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
            self.under_cate = ["انتخاب", "خوارکی ها", "تنقلات و شیرینی ها","سبزیجات و میوه ها", "گوشت و ماهی", "روغن و برنج","خشکبار و مغزیجات","حبوبات","لبنیات"]
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
        self.calendar_popup = Calendar(self)
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
            if filename.lower().endswith((".ttf", ".otf",".TTF")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        pass
    ##
    def public_category(self, text):
        # اگر لاین ادیت یا لیبل قبلاً ساخته شده حذف شوند
        if self.unit_label:
            self.unit_label.deleteLater()
            self.unit_label = None
        if self.unit_lineedit:
            self.unit_lineedit.deleteLater()
            self.unit_lineedit = None

        if text != "دانه"and text !="کیلو" and text != "انتخاب":
            # ساخت لیبل
            self.unit_label = QLabel(f"هر {text}:", self)
            self.unit_label.setGeometry(270, 290, 60, 30)
            self.unit_label.setStyleSheet('''
                font-family: B Nazanin;
                font-size: 16px;
                font-weight: bold;
                color: black;
            ''')
            self.unit_label.show()

            # ساخت لاین ادیت
            self.unit_lineedit = QLineEdit(self)
            self.unit_lineedit.setGeometry(260, 330, 90, 45)
            self.unit_lineedit.setStyleSheet('''
                background-color: white;
                font-family: B Nazanin;
                font-size: 15px;
                font-weight: bold;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 7px;
                padding: 7px;
            ''')
            self.unit_lineedit.show()

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
    def remove_background(self,image: Image.Image) -> Image.Image:
        ##
        image_np = np.array(image.convert("RGB"))
        lower = np.array([200, 200, 200], dtype=np.uint8)  # رنگ‌های روشن پس‌زمینه
        upper = np.array([255, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(image_np, lower, upper)
        mask_inv = cv2.bitwise_not(mask)

        b, g, r = cv2.split(image_np)
        rgba = [b, g, r, mask_inv]
        image_with_alpha = cv2.merge(rgba)

        return Image.fromarray(image_with_alpha, "RGBA")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب تصویر محصول", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            webp_path = os.path.join("converted_images", f"{base_name}.webp")

            os.makedirs("converted_images", exist_ok=True)

            # باز کردن تصویر با PIL
            image = Image.open(file_path)

            # حذف پس‌زمینه به‌صورت واقعی
            image = self.remove_background(image)

            # کاهش اندازه تصویر به حداکثر عرض/ارتفاع مثلاً 800px (بدون افت کیفیت زیاد)
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)

            # ذخیره به صورت WebP با کیفیت بالا و حجم کمتر
            image.save(webp_path, "WEBP", quality=85, method=6)  # روش 6 برای فشرده‌سازی بهتر

            # نمایش تصویر و ذخیره مسیر
            self.img_preveiw.setPixmap(QPixmap(webp_path))
            self.image_path = webp_path

        # دریافت اطلاعات دیتابیس از سرور
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

    ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.insert_product()
    ##

    def insert_product(self):
        import shutil
        f_ch = self.choise_c.currentText()
        s_ch = self.under_choise.currentText()
        name = self.name_line.text()
        barcode = self.bar_line.text()
        exp_date = self.exp_line.text()
        category = self.cate_ch.currentText()
        buy_price = self.buy_line.text()
        quantity = self.number_line.text()
        sale_price = self.sale_line.text()
        sale_big = self.sale_big_line.text()
        
        
        if hasattr(self, 'unit_lineedit') and self.unit_lineedit and self.unit_lineedit.isVisible():
            text = self.unit_lineedit.text()
            try:
                big_s = float(text) if text.strip() else 0.0
            except ValueError:
                big_s = 0.0
        else:
            big_s = 0.0


        db_connection = self.get_db_config()

        if f_ch == "انتخاب" and s_ch == "انتخاب":
            MessageBox(text="لطفاً اطلاعات را از باکس‌های انتخابی وارد کنید", title="هشدار", type="warning").show()
            return

        if not all([name, barcode, exp_date, category, buy_price, quantity, sale_price, sale_big]):
            MessageBox(text="لطفاً تمامی فیلدها را پر کنید", title="هشدار", type="warning").show()
            return

        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            id_user = res_id[0]
        except Exception as e:
            MessageBox(text=f"خطا در خواندن یوزر محلی: {e}", title="❌ خطا", type="error").show()
            return
        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('''
                SELECT weight, production_date, brand, production_place, product_state, more_details, keep_place
                FROM details
                ORDER BY production_date DESC
                LIMIT 1;
        ''')
            detail = cursor_sq.fetchone()
            if detail:
                weight= detail[0]
                pro_date= detail[1]
                brand= detail[2]
                palce= detail[3]
                status= detail[4]
                data= detail[5]
                place= detail[6]


        except Exception as e:
            MessageBox(text=f"خطا در خواندن یوزر محلی: {e}", title="❌ خطا", type="error").show()
            return

        date = datetime.date.today().strftime("%Y/%m/%d")
        date_ent = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
        sale_unit= None
        if category in ["کارتن", "بسته", "شانه", "جعبه"]:
            sale_unit = "عدد"
        elif category in ["کیلو", "کیسه"]:
            sale_unit = "کیلو"
        else:
            sale_unit = "عدد"  # مقدار پیش‌فرض برای جلوگیری از None

        print(sale_unit)

        
        total = float(buy_price) * float(quantity)
        if big_s != 0:
            per_buy = float(buy_price) if buy_price else 0
            per_quantity = float(quantity) * big_s
        else:
            per_buy = float(buy_price)  # اگر big_s صفر باشد، از buy_price استفاده می‌شود
            per_quantity = float(quantity)
              # اگر big_s صفر باشد، از quantity استفاده می‌شود
        # در غیر این صورت محاسبه نمی‌شود
        if big_s > 0:
            big_sub = round(float(per_quantity) / big_s , 1)
            print(f"{big_sub} : تعداد هر بسته 😉✅")
        else:
            big_sub = 0
        
        ##small_price
        small_price= float(sale_big) / big_s
        
        # افزودن ویجت محصول به رابط کاربری
        new_sub= f'{big_sub} {category}'

        local_temp_dir = os.path.join(os.getcwd(), "temp_images")
        os.makedirs(local_temp_dir, exist_ok=True)

        ftp_image_url = ""
        uploaded_to_ftp = False
        local_image_path = ""

        if hasattr(self, "image_path") and self.image_path:
            try:
                image_name = ntpath.basename(self.image_path)
                ftp_image_url = f"uploads/app_images/{image_name}"

                ftp_host = 'ihr.blg.mybluehost.me'
                ftp_user = 'shop@ihr.blg.mybluehost.me'
                ftp_pass = 't@fQvz-7e9'

                ftp = FTP()
                ftp.connect(ftp_host, 21)
                ftp.login(ftp_user, ftp_pass)

                with open(self.image_path, 'rb') as file:
                    ftp.storbinary(f'STOR {image_name}', file)

                ftp.quit()
                uploaded_to_ftp = True
                print("✅ تصویر با موفقیت آپلود شد:", ftp_image_url)

            except Exception as e:
                print("❌ خطا در آپلود تصویر:", e)
                uploaded_to_ftp = False
                # ذخیره موقت در temp_images در صورت خطا
                try:
                    filename = ntpath.basename(self.image_path)
                    local_image_path = os.path.join(local_temp_dir, filename)
                    shutil.copy(self.image_path, local_image_path)
                    print("📁 تصویر در مسیر temp_images ذخیره شد:", local_image_path)
                except Exception as copy_err:
                    print("❌ خطا در کپی تصویر:", copy_err)
        else:
            MessageBox(text="تصویری انتخاب نشده است!", title="❌ هشدار", type="warning").show()

        inserted_online = False
        synced = 0
        if db_connection and uploaded_to_ftp:
            try:
                conn = pymysql.connect(
                    host=db_connection["host"],
                    user=db_connection["user"],
                    password=db_connection["password"],
                    database=db_connection["database"]
                )
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO inventories (barcode, product_name, category,sub_category,buy_date,buy_price, sell_price, big_price, big_category,quantity, expiration_dates, big_quantity,big_sub,
                                            product_image,small_price,sale_unit, total, user_id,created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''', (
                    barcode, name, f_ch, s_ch, date, per_buy, sale_price, sale_big, 
                    category, per_quantity, exp_date,big_s,big_sub, ftp_image_url, small_price or 0,sale_unit,total, id_user,date_ent
                ))

                invent_id = cursor.lastrowid  # گرفتن ID رکورد ثبت‌شده

                cursor.execute('''
                INSERT INTO product_details (weight,production_date,brand,production_place,product_state,
                               more_detail,keep_place,invent_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            ''',(weight,pro_date,brand,palce,status,data,place,invent_id))
                
                conn.commit()
                inserted_online = True
                synced = 1
                MessageBox("✅ محصول در سرور ذخیره شد", title="موفقانه", type="info").show()
            except Exception as e:
                print("❌ خطا در اتصال به سرور:", e)
            finally:
                if conn:
                    conn.close()

        # ذخیره در دیتابیس آفلاین اگر سرور در دسترس نبود یا آپلود تصویر ناموفق بود
        if not inserted_online:
            try:
                # تعیین مسیر تصویر (اگر آپلود نشد، از مسیر temp_images استفاده شود)
                if not uploaded_to_ftp and os.path.exists(local_image_path):
                    image_path_to_store = local_image_path
                else:
                    image_path_to_store = self.image_path if self.image_path else ""

                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute('''
                    INSERT INTO products (barcode, name,category,sub_category,buy_date,buy_price,sale_price, big_price,big_category,quantity, expire_date,big_quantity,big_sub,big_sub_display,
                                        image_path,small_price,sale_unit, total, user_id, is_synced,create_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?,?,?,?,?,?)
                ''', (
                    barcode, name, f_ch, s_ch, date, per_buy, sale_price, sale_big, category, 
                    per_quantity, exp_date, big_s,big_sub,new_sub,image_path_to_store,small_price or 0,sale_unit, total, id_user, synced,date_ent
                ))
                
                invent_ids = cursor_sq.lastrowid

                cursor_sq.execute('''
                INSERT INTO product_details (weight,production_date,brand,production_place,product_state,
                            more_details,keep_place,is_synced,invent_id) VALUES(?,?,?,?,?,?,?,?,?)
                ''',(weight,pro_date,brand,palce,status,data,place,synced,invent_ids))

                
                conn_sq.commit()
                MessageBox("✅ محصول به صورت آفلاین ذخیره شد", title="موفقانه", type="info").show()
                MessageBox("محصول پس از اتصال به اینترنت به صورت خودکار آپلود خواهد شد", title="اطلاع", type="info").show()
            except Exception as e:
                MessageBox(f"❌ خطا در ذخیره آفلاین: {e}", title="خطا", type="error").show()
            finally:
                conn_sq.close()

      
        product_box = ProductBox()
        product_box.set_product_info(
            name=name,
            barcode=barcode,
            buy_price=per_buy,
            sale_price=sale_price,
            number=per_quantity,
            expire_date=exp_date,
            big_sub=new_sub,
            big_price=sale_big,
            image_path=self.image_path
        )
        row, col = divmod(self.inventory_page.box_layout.count(), 4)
        self.inventory_page.box_layout.addWidget(product_box, row, col)

        # پاک کردن فیلدها
        self.name_line.clear()
        self.bar_line.clear()
        self.buy_line.clear()
        self.sale_line.clear()
        self.sale_big_line.clear()
        self.number_line.clear()
        self.exp_line.clear()
        self.choise_c.setCurrentIndex(0)
        self.under_choise.setCurrentIndex(0)
        self.cate_ch.setCurrentIndex(0)
        self.total_line.setText("0.00")
        self.img_preveiw.clear()
   
    ##
    def sync_to_server(self):
        db_connect = self.get_db_config()
        if not db_connect:
            return

        conn_sq = sqlite3.connect("D:\\projects\\sh_online\\Data\\sh_online.db")
        cursor_sq = conn_sq.cursor()

        cursor_sq.execute('''SELECT invent_id, barcode, name, category, sub_category,
                            buy_date, buy_price, sale_price, big_price,
                            big_category, quantity, expire_date,big_quantity,big_sub, image_path, small_price,sale_unit,total, user_id,create_at
                            FROM products WHERE is_synced = 0''')

        unsynced_products = cursor_sq.fetchall()

        try:
            conn = pymysql.connect(
                host=db_connect["host"],
                user=db_connect["user"],
                password=db_connect["password"],
                database=db_connect["database"]
            )
            cursor = conn.cursor()

            for product in unsynced_products:
                (local_product_id, barcode, name, category, sub_category, buy_date, buy_price,
                sale_price, big_price, big_category, quantity, expire_date,big_quantity,big_sub,
                image_path, small_price,sale_unit,total, user_id,create_at) = product

                ftp_image_url = ""

                # آپلود تصویر
                if image_path and os.path.isfile(image_path):
                    try:
                        image_name = ntpath.basename(image_path)
                        ftp_image_url = f"uploads/app_images/{image_name}"

                        ftp = FTP()
                        ftp.connect('ihr.blg.mybluehost.me', 21)
                        ftp.login('shop@ihr.blg.mybluehost.me', 't@fQvz-7e9')

                        with open(image_path, 'rb') as file:
                            ftp.storbinary(f'STOR {image_name}', file)

                        ftp.quit()
                        print("✅ تصویر آپلود شد:", ftp_image_url)

                    except Exception as e:
                        print("❌ خطا در آپلود تصویر:", e)
                        ftp_image_url = ""

                # جایگزینی None با مقدار خالی
                big_category = big_category or ""
                category = category or ""
                name = name or ""
                sub_category = sub_category or ""

                # بررسی وجود محصول در جدول آنلاین
                cursor.execute("SELECT COUNT(*) FROM inventories WHERE barcode = %s", (barcode,))
                if cursor.fetchone()[0] == 0:
                    # درج در inventories
                    cursor.execute('''
                        INSERT INTO inventories (
                            barcode, product_name, category, sub_category, buy_date,
                            buy_price, sell_price, big_price, big_category, quantity,
                            expiration_dates,big_quantity,big_sub,product_image,small_price,sale_unit, total, user_id,created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
                    ''', (
                        barcode, name, category, sub_category, buy_date,
                        buy_price, sale_price, big_price, big_category, quantity,
                        expire_date, big_quantity,big_sub,ftp_image_url, small_price,sale_unit,total, user_id,create_at
                    ))

                    invent_id = cursor.lastrowid  # آیدی رکورد ثبت‌شده در سرور

                    # خواندن اطلاعات product_details از SQLite
                    cursor_sq.execute('''
                        SELECT weight, production_date, brand, production_place, product_state,
                            more_detail, keep_place
                        FROM product_details WHERE invent_id = ?
                    ''', (local_product_id,))
                    detail = cursor_sq.fetchone()

                    if detail:
                        weight, pro_date, brand, place, status, description, keep_place = detail
                        # درج در product_details در سرور
                        cursor.execute('''
                            INSERT INTO product_details (
                                weight, production_date, brand, production_place,
                                product_state, more_detail, keep_place, invent_id
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            weight, pro_date, brand, place,
                            status, description, keep_place, invent_id
                        ))

            conn.commit()
            print("✅ همگام‌سازی با موفقیت انجام شد")

            # به‌روزرسانی SQLite
            cursor_sq.execute("UPDATE products SET is_synced = 1 WHERE is_synced = 0")
            cursor_sq.execute("UPDATE product_details SET is_synced = 1 WHERE is_synced = 0")
            conn_sq.commit()

        except Exception as e:
            print("❌ خطا در همگام‌سازی:", e)

        finally:
            conn_sq.close()
            if conn:
                conn.close()

   
    

    ##
    def open_details(self):
        details= MoreDetails()
        details.exec()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductForm()
    window.show()
    sys.exit(app.exec())
