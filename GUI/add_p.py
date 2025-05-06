from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
import jdatetime
from profile_picture import ProfileImage
from info_box import ProductBox
from inventory import Inventory
from message_b import MessageBox
from PyQt6.QtCore import Qt,QPropertyAnimation,QEasingCurve,QPoint
from PyQt6 import QtCore
import os
from calendars import JalaliCalendar
import requests
import pymysql
import sqlite3
from  ftplib import FTP
from list_p import ProductListPopup


class AddProduct(QDialog):
    def __init__(self,inventory_page):
        super().__init__()
        self.setWindowTitle("📦 ثبت محصول جدید")
        self.resize(929, 630)
        self.setFixedSize(929, 630)  # جلوگیری از تغییر اندازه
        self.setStyleSheet("background-color: #E8E6E6;")
        self.inventory_page= inventory_page
        

        self.center_window()  # <-- وسط‌چین کردن
        # نمونه ویجت تستی
        self.title_lb = QLabel("افزودن محصولات",self)
        # 🔵 عکس پروفایل با کیفیت و کلیک‌پذیر
        profile_image_path = self.get_asset_path("ChatGPT Image Apr 14, 2025, 04_02_55 PM.png")  # مسیر پیش‌فرض عکس
        self.profile_widget = ProfileImage(profile_image_path, 70, self)
        self.profile_widget.setGeometry(850,14,0,0)
        self.date_lb= QLabel("",self)
        
        self.set_today_date()
        self.add_horizontal_line()
        ##
        self.bar_lb= QLabel("بارکد محصول:",self)
        self.bar_line= QLineEdit(self)
        self.barcode_img= QLabel(self)
       ##
        self.name_lb= QLabel("نام محصول:", self)
        self.name_line= QLineEdit(self)
        self.name_line.setReadOnly(True)
        ##
        self.quantity_lb= QLabel("موجودی فعلی:", self)
        self.quantity_line= QLineEdit(self)

        self.number_lb= QLabel("تعداد جدید محصول:", self)
        self.number_line= QLineEdit(self)
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
        self.buy_price= QLabel("قیمت خرید:",self)
        self.buy_line= QLineEdit(self)
        ##
        self.sale_price= QLabel("قیمت فروش:", self)
        self.sale_line= QLineEdit(self)
        ##
        self.sale_big= QLabel("قیمت عمده:",self)
        self.sale_big_line= QLineEdit(self)
        ##
        self.total_label= QLabel("مجموعه:",self)
        self.total_line= QLabel("0.00",self)
        ### event
        self.buy_line.textEdited.connect(self.calculate_total)
        self.number_line.textEdited.connect(self.calculate_total)

        ##
        self.product_list= QPushButton(self)

        # بعد از تعریف سایر ویجت‌ها در __init__
        self.product_popup = ProductListPopup()
        self.product_popup.list_widget.itemClicked.connect(self.set_selected_product)
        self.product_list.clicked.connect(self.show_product_popup)


        ##
        self.picture_btn= QPushButton(self)
        self.submit_btn= QPushButton(self)
        self.calendar_btn= QPushButton(self)
        ##
        self.lable_UI()
        self.enties_UI()
        self.Button_UI()
    
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
        self.bar_lb.setGeometry(776,115,115,20)
        self.bar_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.barcode_img.setGeometry(860,157,30,30)
        self.bar_pix= QPixmap(self.get_asset_path("Barcode.png"))
        self.barcode_img.setPixmap(self.bar_pix)
        self.barcode_img.setStyleSheet("background-color: transparent;")
        self.barcode_img.setFixedSize(30,30)
        ##
        self.name_lb.setGeometry(470,115,120,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.quantity_lb.setGeometry(776,225,115,20)
        self.quantity_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.exp_name.setGeometry(776,320,120,20)
        self.exp_name.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.buy_price.setGeometry(480,320,120,20)
        self.buy_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.number_lb.setGeometry(475,225,120,20)
        self.number_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.sale_price.setGeometry(776,425,120,20)
        self.sale_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
            ''')
        ##
        self.sale_big.setGeometry(480,425,120,20)
        self.sale_big.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
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
        self.bar_line.setGeometry(653, 150, 250, 45)
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
        self.name_line.setGeometry(355,150,250,45)
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
        self.quantity_line.setGeometry(653,260,250,45)
        self.quantity_line.setStyleSheet('''
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
        self.number_line.setGeometry(355,260,250,45)
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
        self.exp_line.setGeometry(653,350,250,45)
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
        self.buy_line.setGeometry(355,350,250,45)
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
        
        self.sale_line.setGeometry(653,450,250,45)
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
        self.sale_big_line.setGeometry(355,450,250,45)
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
        self.submit_btn.setText("ذخیره محصول")
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
                padding-right: 110px; /* فاصله‌ی داخلی سمت راست */
                padding-left: 120px;  /* فاصله‌ی داخلی سمت چپ */
                qproperty-iconSize: 32px;

            }
            QPushButton:hover {
                background-color: #84E963;  
            }
            QPushButton:pressed {
                background-color: #3EB516;
            }
        ''')
        #self.submit_btn.clicked.connect(self.insert_product)
        ##
        self.picture_btn.setGeometry(40,230,120,36)
        self.picture_icon= QIcon(self.get_asset_path("Percentage.png"))
        self.picture_btn.setIcon(self.picture_icon)
        self.picture_btn.setIconSize(QtCore.QSize(30,30))
        self.picture_btn.setText("  تخفیف")
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
        self.calendar_btn.setGeometry(660,357,30,30)
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
        self.product_list.setGeometry(360,157,30,30)
        self.produt_icon= QIcon(self.get_asset_path("Product.png"))
        self.product_list.setIcon(self.produt_icon)
        self.product_list.setIconSize(QtCore.QSize(30,30))
        self.product_list.setStyleSheet('''
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

        # دریافت اطلاعات دیتابیس از سرور
    ##
    def get_db_config(self):

        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }

        try:
            # ارسال درخواست با timeout کوتاه‌تر و تقسیم شده
            response = requests.get(url, headers=headers, timeout=(20))  # (اتصال، دریافت)
            response.raise_for_status()

            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data

        except requests.Timeout:
            print("⏳ زمان اتصال یا پاسخ‌گویی سرور بیش از حد طول کشید.")
        except requests.RequestException as e:
            print(f"⚠️ خطای ارتباطی: {e}")
        except ValueError as e:
            print(f"🚨 خطای پردازش پاسخ: {e}")

        return None
    ##
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.bar_line.hasFocus():
                self.search_barcode()
            elif self.name_line.hasFocus():
                self.search_name()

    ##upadte actions:
    def search_barcode(self):
        barcode= self.bar_line.text().strip()
        if not barcode:
            MessageBox("لطفاً بارکد محصول را وارد کنید",title="یادآوری",type="warning").show()
        conn_sq=None
        cursor_sq= None
        # خواندن شناسه کاربر از دیتابیس محلی
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
            ##
            cursor_sq.execute('''
            select name,buy_price,
            sale_price,quantity,
            expire_date,big_price
            From products WHERE  barcode=? and user_id=?''',(barcode,id_user))
            result= cursor_sq.fetchone()
            
            if result:
                self.name_line.clear()
                self.name_line.insert(str(result[0]))
                ##
                self.buy_line.clear()
                self.buy_line.insert(str(result[1]))
                ##
                self.sale_line.clear()
                self.sale_line.insert(str(result[2]))
                ##
                self.sale_big_line.clear()
                self.sale_big_line.insert(str(result[5]))
                ##
                self.quantity_line.clear()
                self.quantity_line.insert(str(result[3]))
                ##
                self.exp_line.clear()
                self.exp_line.insert(str(result[4]))
                
        except pymysql.Error as e:
            MessageBox(f"{e}: خطا در دیتابیس",type="error",title="خطا").show()
    ##
    def search_name(self):
        name= self.name_line.text().strip()
        if not name: 
            MessageBox("لطفاً نام محصول را وارد کنید",title="یادآوری",type="warning")
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
            ##
            cursor_sq.execute('''
            select barcode,buy_price,
            sale_price,quantity,
            expire_date,big_price
            From products WHERE  name=? and user_id=?''',(name,id_user))
            result= cursor_sq.fetchone()
            
            if result:
                self.bar_line.clear()
                self.bar_line.insert(str(result[0]))
                ##
                self.buy_line.clear()
                self.buy_line.insert(str(result[1]))
                ##
                self.sale_line.clear()
                self.sale_line.insert(str(result[2]))
                ##
                self.sale_big_line.clear()
                self.sale_big_line.insert(str(result[3]))
                ##
                self.quantity_line.clear()
                self.quantity_line.insert(str(result[3]))
                ##
                self.exp_line.clear()
                self.exp_line.insert(str(result[4]))

        except pymysql.Error as e:
            MessageBox(f"{e}: خطا در دیتابیس",type="error",title="خطا").show()
    ##
    def show_product_popup(self):
        # مکان دقیق باز شدن زیر name_line
        global_pos = self.name_line.mapToGlobal(self.name_line.rect().bottomLeft())
        self.product_popup.show_with_animation(global_pos)

    def set_selected_product(self, item):
        self.name_line.setText(item.text())
        self.product_popup.hide()



    def update_product(self):
        pass






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddProduct()
    window.show()
    sys.exit(app.exec())
