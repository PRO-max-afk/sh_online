from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog)
from PyQt6.QtGui import QPixmap, QFont,QColor
import sys
import jdatetime
from profile_picture import ProfileImage
from PyQt6.QtCore import Qt
import os

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
        self.bar_lb= QLabel("بارکد محصول:",self)
        self.bar_line= QLineEdit(self)
        ##
        self.name_lb= QLabel("نام محصول:", self)
        self.name_line= QLineEdit(self)
        ##
        self.exp_name= QLabel("تاریخ انقضاء:", self)
        self.exp_line= QLineEdit(self)
        ##
        self.category= QLabel("کتگوری عمده:",self)
        self.cate_ch= QComboBox(self)
        ##

        ##
        self.lable_UI()
        self.enties_UI()

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
        self.cate_lb.setGeometry(760,115,150,20)
        self.cate_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.bar_lb.setGeometry(480,215,115,20)
        self.bar_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.name_lb.setGeometry(776,215,115,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.exp_name.setGeometry(776,315,120,20)
        self.exp_name.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.category.setGeometry(480,315,120,20)
        self.category.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
    ##
    def enties_UI(self):
        self.choise_c.setGeometry(355, 150, 545, 45)
        self.choise_c.addItems(["مواد غذایی","سبزیجات","غله جات"])
        self.choise_c.setCurrentText("مواد غذایی")
        self.choise_c.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.choise_c.setStyleSheet('''
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
                padding-left: 440px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 30px;
                height: 30px;
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
        self.name_line.setGeometry(653,250,250,45)
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
        self.bar_line.setGeometry(355,250,250,45)
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
        self.exp_line.setGeometry(653,350,250,45)
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
        self.cate_ch.setGeometry(355,350,250,45)
        self.cate_ch.addItems(["عدد","دانه","بسته"])
        self.cate_ch.setCurrentText("دانه")
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
                padding-left: 180px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 30px;
                height: 30px;
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

    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductForm()
    window.show()
    sys.exit(app.exec())
