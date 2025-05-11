from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget,QTextEdit)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
import jdatetime
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os
import numpy as np
from calendars import JalaliCalendar
import requests
import pymysql
import sqlite3

class MoreDetails(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("جزئیات بیشتر محصول")
        self.resize(613,540)
        self.setFixedSize(613,540)
        self.setStyleSheet("background-color: #E8E6E6;")
        self.In_UI()
        self.label_UI()
        self.Entries_UI()
        self.Button_UI()
        self.add_horizontal_line()
        self.center_window()

    
    def In_UI(self):
        self.title_lb= QLabel("مشخصات محصول",self)
        ##
        self.brand_lb= QLabel("برند محصول:",self)
        self.brand_line= QLineEdit(self)
        ##
        self.place_lb= QLabel("محل تولید:",self)
        self.palce_line= QLineEdit(self)
        ##
        self.pro_date_lb= QLabel("تاریخ تولید:",self)
        self.pro_date_line= QLineEdit(self)
        ##
        self.state_lb= QLabel("وضعیت محصول:",self)
        self.state_line= QLineEdit(self)
        ##
        self.weight_lb= QLabel("وزن محصول:",self)
        self.weight_line= QLineEdit(self)
        ##
        self.place_st_lb= QLabel("محل نگهداری:",self)
        self.place_st_line= QLineEdit(self)
        ##
        self.more_lb= QLabel("توضیحات بیشتر:",self)
        self.more_detials= QTextEdit(self)
        ##
        self.save_btn= QPushButton(self)
        self.calendar_btn= QPushButton(self)
        
        
    ##
    def label_UI(self):
        self.title_lb.setGeometry(226,12,137,20)
        self.title_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 20px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.brand_lb.setGeometry(460,87,80,20)
        self.brand_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.place_lb.setGeometry(183,90,80,20)
        self.place_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.pro_date_lb.setGeometry(463,180,80,20)
        self.pro_date_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.state_lb.setGeometry(176,180,90,20)
        self.state_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.weight_lb.setGeometry(464,273,80,20)
        self.weight_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.place_st_lb.setGeometry(183,273,80,20)
        self.place_st_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.more_lb.setGeometry(447,350,95,20)
        self.more_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
    ##
    def Entries_UI(self):
        self.brand_line.setGeometry(360,113,190,45)
        self.brand_line.setStyleSheet('''
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
        self.palce_line.setGeometry(80,113,190,45)
        self.palce_line.setStyleSheet('''
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
        self.pro_date_line.setGeometry(360,205,190,45)
        self.pro_date_line.setReadOnly(True)
        self.pro_date_line.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.pro_date_line.setStyleSheet('''
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
        self.state_line.setGeometry(80,205,190,45)
        self.state_line.setStyleSheet('''
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
        self.weight_line.setGeometry(360,301,190,45)
        self.weight_line.setStyleSheet('''
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
        self.place_st_line.setGeometry(80,301,190,45)
        self.place_st_line.setStyleSheet('''
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
        self.more_detials.setGeometry(84,377,460,85)
        self.more_detials.setStyleSheet(''' 
            background-color: white;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 14px;
            color: black;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            padding: 3px;
            
        ''')



    ##
    def Button_UI(self):
        self.calendar_btn.setGeometry(364,212,30,30)
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
        self.save_btn.setGeometry(116,475,358,45)
        self.sub_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.save_btn.setIcon(self.sub_icon)
        self.save_btn.setIconSize(QtCore.QSize(36,36))
        self.save_btn.setText(" ذخیره اطلاعات")
        self.save_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.save_btn.setStyleSheet('''
            QPushButton {
                background-color: #3EB516;
                font-family: "Mirza";
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px;
                padding-right: 115px; /* فاصله‌ی داخلی سمت راست */
                padding-left: 115px;  /* فاصله‌ی داخلی سمت چپ */
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
    ##
    def show_calendar(self):
        self.calendar_popup = JalaliCalendar(self)
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomRight())
        self.calendar_popup.show_with_animation(pos)
    ##   
    def add_horizontal_line(self):
        self.line = QFrame(self)
        self.line.setGeometry(40, 60, 520, 1)  
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("color: white; background-color: white;")

    def center_window(self):
        screen= self.screen().availableGeometry()
        size= self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )
     ##
    def set_selected_date(self, date_str):
        self.pro_date_line.setText(date_str)
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

if __name__ == "main":
    app= QApplication(sys.argv)
    window= MoreDetails()
    window.show
    sys.exit(app.exec())