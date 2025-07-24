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
from inventory import Inventory
from message_b import MessageBox
from inventory import Inventory
from PyQt6.QtCore import Qt,QPropertyAnimation,QEasingCurve,QPoint
from PyQt6 import QtCore
import os
from calendars import JalaliCalendar
import requests
import pymysql
import sqlite3
from  ftplib import FTP
from list_p import ProductListPopup
from inventory import Inventory


class ProductDiscount(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 ثبت محصول جدید")
        self.resize(613, 492)
        self.setFixedSize(613, 492)  # جلوگیری از تغییر اندازه
        self.setStyleSheet("background-color: #E8E6E6;")
        self.load_all_fonts()
        self.inventory_page= Inventory()
        

        self.center_window()  # <-- وسط‌چین کردن
        # نمونه ویجت تستی
        self.title_lb = QLabel("ثبت تخفیف",self)

        
        self.add_horizontal_line()
        ##
        self.bar_lb= QLabel("بارکد محصول:",self)
        self.bar_line= QLineEdit(self)
        self.barcode_img= QLabel(self)
       ##
        self.name_lb= QLabel("نام محصول:", self)
        self.name_line= QLineEdit(self)
        self.name_line.setReadOnly(True)
        self.name_line.textChanged.connect(self.auto_search_name)
      
        ##
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.jalali_calendar = JalaliCalendar(self)
        self.jalali_calendar.setMaximumHeight(0)  # در ابتدا بسته باشد
        self.layout.addWidget(self.jalali_calendar)
        ##
        self.buy_price= QLabel("فیصدی تخفیف :",self)
        self.buy_line= QLineEdit(self)
        ##
        self.sale_price= QLabel("قیمت فروش:", self)
        self.sale_line= QLineEdit(self)
        self.sale_line.setReadOnly(True)
        ##
        self.exp_name= QLabel("مدت اعتبار:", self)
        self.exp_line= QLineEdit(self)
        self.exp_line.setReadOnly(True)
        ##
        self.total_label= QLabel("قیمت جدید:",self)
        self.total_line= QLabel("0.00",self)
        ### event
        self.buy_line.textEdited.connect(self.calculate_total)
        self.sale_line.textChanged.connect(self.calculate_total)

        ##
        self.product_list= QPushButton(self)

        # بعد از تعریف سایر ویجت‌ها در __init__
        self.product_popup = ProductListPopup()
        self.product_popup.list_widget.itemClicked.connect(self.set_selected_product)
        self.product_list.clicked.connect(self.show_product_popup)


        ##
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
    def lable_UI(self):
        self.title_lb.setGeometry(200,15,150,20)
        self.title_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 20px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.bar_lb.setGeometry(465,95,117,20)
        self.bar_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.barcode_img.setGeometry(545,127,30,30)
        self.bar_pix= QPixmap(self.get_asset_path("Barcode.png"))
        self.barcode_img.setPixmap(self.bar_pix)
        self.barcode_img.setStyleSheet("background-color: transparent;")
        self.barcode_img.setFixedSize(30,30)
        ##
        self.name_lb.setGeometry(135,100,120,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
    
        ##
        self.exp_name.setGeometry(465,287,120,20)
        self.exp_name.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.buy_price.setGeometry(135,189,120,20)
        self.buy_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.sale_price.setGeometry(460,189,120,20)
        self.sale_price.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
            ''')
        ##
        self.total_label.setGeometry(78,340,85,20)
        self.total_label.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.total_line.setGeometry(17,340,70,30)
        self.total_line.setStyleSheet('''
            font-family: Arial,"Roboto";
            font-size: 15px;
            font-weight: bold;
            color: black;
            text-align: center;
        ''')
    ##
    def enties_UI(self):
        self.bar_line.setGeometry(340, 123, 250, 45)
        self.bar_line.setStyleSheet('''
            background-color: white;
            font-family: Arial,"Roboto";
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            color: black;
            padding: 7px;
        ''')
        ##
        self.name_line.setGeometry(17,126,250,45)
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
        self.exp_line.setGeometry(340,321,250,45)
        self.exp_line.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.exp_line.setStyleSheet('''
            background-color: white;
            font-family: "arial",Roboto;
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
       ##
        self.buy_line.setGeometry(17,223,250,45)
        self.buy_line.setStyleSheet('''
            background-color: white;
            font-family: arial,"Roboto";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')
        
        self.sale_line.setGeometry(340,218,250,45)
        self.sale_line.setStyleSheet('''
            background-color: white;
            font-family: arial,"Mirza";
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
        ''')
        

    ##
    def Button_UI(self):
        self.submit_btn.setGeometry(116,421,358,45)
        self.sub_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.submit_btn.setIcon(self.sub_icon)
        self.submit_btn.setIconSize(QtCore.QSize(36,36))
        self.submit_btn.setText("ثبت تخفیف")
        self.submit_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.submit_btn.clicked.connect(self.update_product)
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
     
        ##
        self.calendar_btn.setGeometry(545,327,30,30)
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
        self.product_list.setGeometry(23,132,30,30)
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

    ##line
    def add_horizontal_line(self):
        self.line = QFrame(self)
        self.line.setGeometry(15, 70, 590, 1)  # مکان: زیر date_lb با عرض 900
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
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.bar_line.hasFocus():
                self.search_barcode()
            elif any(line.hasFocus() for line in [
                self.exp_line,self.buy_line, self.sale_line
            ]):
                self.update_product()

    ##
    def auto_search_name(self):
        text = self.name_line.text().strip()
        if text:  # اگر حتی یک حرف نوشته شده باشد
            self.search_name()
    ##upadte actions:
    def search_barcode(self):
        barcode= self.bar_line.text().strip()
        if not barcode:
            MessageBox("لطفاً بارکد محصول را وارد کنید",title="یادآوری",type="warning").show()
        conn_sq=None
        cursor_sq= None
        # خواندن شناسه کاربر از دیتابیس محلی
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        try:
            ##
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('''
            select name,sale_price
            From products WHERE  barcode=?''',(barcode,))
            result= cursor_sq.fetchone()
            
            if result:
                self.name_line.clear()
                self.name_line.insert(str(result[0]))
                ##
                self.sale_line.clear()
                self.sale_line.insert(str(result[1]))

        except pymysql.Error as e:
            MessageBox(f"{e}: خطا در دیتابیس",type="error",title="خطا").show()
    
    ##
    def search_name(self):
        name= self.name_line.text().strip()
        if not name: 
            MessageBox("لطفاً نام محصول را وارد کنید",title="یادآوری",type="warning")
            return
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        
        try:
            ##
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('''
            select barcode,sale_price
            From products WHERE  TRIM(name)=?''',(name,))
            result= cursor_sq.fetchone()
            
            if result:
                self.bar_line.clear()
                self.bar_line.insert(str(result[0]))
                ##
                self.sale_line.clear()
                self.sale_line.insert(str(result[1]))


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
    ##
    def calculate_total(self):
        sale_price= self.sale_line.text()
        discount_percent= self.buy_line.text()

        try:
            sale_price= float(sale_price) if sale_price.strip() else 0.0
            discount_percent = float(discount_percent) if discount_percent.strip() else 0.0

            total= sale_price - (sale_price * discount_percent / 100) 
            self.total_line.setText(f'{total}')
        except ValueError:
            self.total_line.setText("0.00")
            return
         
       

    def update_product(self):
        barcode = self.bar_line.text().strip()
        name = self.name_line.text().strip()
        expire_date = self.exp_line.text().strip()
        discount_percent = self.buy_line.text().strip()
        sale_price = self.sale_line.text().strip()
        
        today_jalali = jdatetime.date.today()
        date_ent = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

        # اعتبارسنجی ورودی‌ها
        if not all([barcode, name, expire_date, discount_percent, sale_price]):
            MessageBox("لطفاً تمام فیلدها را پر کنید.", title="⚠️ هشدار", type="warning").show()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            # تبدیل expire_date به jdatetime.date
            try:
                year, month, day = map(int, expire_date.split("/"))
                expire_jdate = jdatetime.date(year, month, day)
            except ValueError:
                MessageBox("تاریخ انقضا وارد شده معتبر نیست!", title="⚠️ خطا در تاریخ", type="warning").show()
                return

            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()

            cursor_sq.execute('SELECT quantity FROM products WHERE barcode=?', (barcode,))
            qua = cursor_sq.fetchone()

            if not qua:
                MessageBox("محصولی با این بارکد یافت نشد.", title="❌ خطا", type="error").show()
                return

            quantity = qua[0]

            sale_price = float(sale_price)
            discount_percent = float(discount_percent)

            total = sale_price - (sale_price * discount_percent / 100)
            final_total = quantity * total

            # محاسبه روزهای باقی‌مانده تا انقضا
            expire_discount = (expire_jdate - today_jalali).days
            print(f"{expire_discount} روز تا انقضا باقی مانده است.")

            is_synced = 0
            cursor_sq.execute("""
                UPDATE products 
                SET new_price = ?, discount_percent=?,total = ?, expire_discount = ?, is_synced = ?, update_at = ?
                WHERE barcode = ?
            """, (total,discount_percent, final_total, expire_discount, is_synced, date_ent, barcode))

            conn_sq.commit()

            MessageBox("✅ اطلاعات محصول با موفقیت به‌روزرسانی شد.", title="عملیات موفق", type="info").show()
            print("✅ تغییرات در جدول products ثبت شد.")

            self.name_line.clear()
            self.bar_line.clear()
            self.exp_line.clear()
            self.buy_line.clear()
            self.sale_line.clear()
            self.total_line.setText("0.00")

        except sqlite3.Error as e:
            MessageBox(f"{e}: خطا در پایگاه داده", title="❌ خطا", type="error").show()

    ##
    def closeEvent(self, event):
        if self.inventory_page:
            self.inventory_page.start_synced_to_thread()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductDiscount()
    window.show()
    sys.exit(app.exec())
