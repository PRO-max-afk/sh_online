from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
import jdatetime
import datetime
from datetime import date
from profile_picture import ProfileImage
from message_b import MessageBox
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os
from c_calendar import Calendar
import pymysql
import sqlite3


class Customer_Form(QDialog):
    def __init__(self, customer_page=None):
        super().__init__()
        self.customer_page= customer_page
        self.setWindowTitle("ثبت نام مشتریان")
        self.resize(470,500)
        self.setFixedSize(470,500)
        self.setStyleSheet("background-color: #E8E6E6;")
        self.load_all_fonts()
        self.center_window()
        self.in_UI()
        self.Button_UI()
        self.Lable_UI()
        self.Input_UI()

    def in_UI(self):
        ##top
        self.top_label= QLabel("ثبت نام مشتریان",self)
        self.add_horizontal_line()
        ##middle:
        self.name_lb= QLabel("نام مشتری:",self)
        self.name_line= QLineEdit(self)
        ##
        self.last_lb= QLabel("تخلص مشتری:",self)
        self.last_line= QLineEdit(self)
        ##
        self.phone_lb= QLabel("شماره تماس:",self)
        self.phone_line= QLineEdit(self)
        ##
        self.email_lb= QLabel("ایمیل مشتری:",self)
        self.email_line= QLineEdit(self)
        ##
        self.save_btn= QPushButton(self)


        
    def Button_UI(self):
                ##
        self.save_btn.setGeometry(100,430,300,45)
        self.sub_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.save_btn.setIcon(self.sub_icon)
        self.save_btn.setIconSize(QtCore.QSize(36,36))
        self.save_btn.setText(" ذخیره اطلاعات")
        self.save_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.save_btn.clicked.connect(self.insert_customer)
        self.save_btn.setStyleSheet('''
            QPushButton {
                background-color: #3EB516;
                font-family: "B Nazanin";
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-right: 80px; /* فاصله‌ی داخلی سمت راست */
                padding-left: 100px;  /* فاصله‌ی داخلی سمت چپ */
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
    def Lable_UI(self):
        self.top_label.setGeometry(180,20,115,30)
        self.top_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        self.name_lb.setGeometry(350,95,85,30)
        self.name_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        self.last_lb.setGeometry(365,165,85,30)
        self.last_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        self.phone_lb.setGeometry(357,245,85,30)
        self.phone_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.email_lb.setGeometry(357,315,85,30)
        self.email_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
    ##
    def Input_UI(self):
        self.name_line.setGeometry(150,90,210,45)
        self.name_line.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.name_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')
        ##
        self.last_line.setGeometry(150,160,210,45)
        self.last_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')
        ##
        self.phone_line.setGeometry(150,240,210,45)
        self.phone_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')
        ##
        self.email_line.setGeometry(150,310,210,45)
        self.email_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 7px;
            ''')     
    ##
    def closeEvent(self, event):
        if self.customer_page:
            self.customer_page.show_customers()
        event.accept()
    ##
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            self.insert_customer()
    ##
    def add_horizontal_line(self):
        self.line = QFrame(self)
        self.line.setGeometry(15, 60, 440, 1)  # مکان: زیر date_lb با عرض 900
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("color: white; background-color: white;")
    ##center_window open
    def center_window(self):
        screen= self.screen().availableVirtualGeometry()
        size= self.geometry()
        self.move(
            int((screen.width() - size.width())/2),
            int((screen.height() - size.height())/2)
        )
    ##
    def insert_customer(self):
        name= self.name_line.text().strip()
        last_name= self.last_line.text().strip()
        phone= self.phone_line.text()
        email= self.email_line.text().strip()
        register_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not (name,last_name,phone,email):
            MessageBox(text="لطفاً اطلاعات مورد نیاز را وارد کنید",title="هشدار!",type="warning").show()
            return
        base_dir=os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir,"Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no offline db")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user= cursor.fetchone()[0]
            cursor.execute('''
                INSERT INTO customers(name,last_name,phone,email,register_date,user_id) Values(?,?,?,?,?,?)
            ''',(name,last_name,phone,email,register_date,id_user))
            conn.commit()
            MessageBox(text="اطلاعات مشتری موفقانه ذخیره شد",title="موفقانه",type="info").show()
            self.name_line.clear()
            self.last_line.clear()
            self.phone_line.clear()
            self.email_line.clear()
        except sqlite3.Error as e:
            print(f"{e}: db problem")
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
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



if __name__== "__main":
    app= QApplication(sys.argv)
    window= Customer_Form()
    window.show()
    sys.exit(app.exec())