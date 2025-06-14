from PyQt6.QtWidgets import (QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush
from PyQt6 import QtCore
import jdatetime
import sqlite3
import pymysql
import requests
import threading
import datetime
from message_b import MessageBox
from switch import ToggleSwitch
import os
import sys

class UserSettings(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.feild_UI()
        self.set_today_date()
        self.set_today_time()
        self.Button_UI()

        


    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # ScrollArea setup
       

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("تنظیمات کاربران", self)

        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.label, 1)
        ##
        middle_layout= QGridLayout()
        ###
        user_frame= QFrame()
        user_frame.setStyleSheet("background-color: white; border-radius: 12px;")

        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        user_frame.setGraphicsEffect(shadow)

        ##
        user_layout = QHBoxLayout(user_frame)
        ##
        tt_layout= QHBoxLayout()
        self.tite_label= QLabel("معلومات کاربر")
        tt_layout.addWidget(self.tite_label)
        tt_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    
        ##
        name_layout= QVBoxLayout()
        self.name_label= QLabel("نام کاربر")
        self.name_line= QLineEdit()
        #
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_line)
        ##
        last_layout= QVBoxLayout()
        self.last_name= QLabel("نام فامیلی کاربر")
        self.last_line= QLineEdit()
        #
        last_layout.addWidget(self.last_name)
        last_layout.addWidget(self.last_line)
       
        ###
        user_layout.addLayout(tt_layout)
        user_layout.addLayout(last_layout)
        user_layout.addLayout(name_layout)
        
        
        
        ###
        password_frame= QFrame()
        password_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        
        shadows= QGraphicsDropShadowEffect(self)
        shadows.setBlurRadius(12)
        shadows.setXOffset(0)
        shadows.setYOffset(5)
        shadows.setColor(QColor(0, 0, 0, 70))
        password_frame.setGraphicsEffect(shadows)

        ##
        password_layout = QHBoxLayout(password_frame)
        ##
        titel_layout= QHBoxLayout()
        self.titel_label= QLabel("تغییر رمزعبور")
        titel_layout.addWidget(self.titel_label)
        titel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        ##
        old_layout= QVBoxLayout()
        self.old_label= QLabel("رمز عبور قدیمی")
        self.old_line= QLineEdit()
        
        #
        old_layout.addWidget(self.old_label)
        old_layout.addWidget(self.old_line)
        #old_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        ##
        new_p_layout= QVBoxLayout()
        self.new_password= QLabel("رمز عبور جدید")
        self.new_p_line= QLineEdit()
        #
        new_p_layout.addWidget(self.new_password)
        new_p_layout.addWidget(self.new_p_line)
        #new_p_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        ##
        confirm_layout= QVBoxLayout()
        self.confirm_password= QLabel("تایید رمزعبور")
        self.confirm_p_line= QLineEdit()
        confirm_layout.addWidget(self.confirm_password)
        confirm_layout.addWidget(self.confirm_p_line)
        #confirm_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        ###
        password_layout.addLayout(titel_layout)
        password_layout.addLayout(confirm_layout)
        password_layout.addLayout(new_p_layout)
        password_layout.addLayout(old_layout)

       
        ##
        list_frame= QFrame()
        list_frame.setStyleSheet("background-color: transparent; border-radius: 12px;")
        
        ##
        middle_layout.addWidget(user_frame,1,1)
        middle_layout.setSpacing(10)
        middle_layout.addWidget(password_frame,2,1)
        middle_layout.setSpacing(10)
        middle_layout.addWidget(list_frame,3,1)

        
        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
    
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
    ##
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

    ##
    def label_UI(self):
        self.label.setMinimumSize(150,30)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        self.tite_label.setMinimumSize(120,25)
        self.tite_label.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.name_label.setMinimumSize(120,25)
        self.name_label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.last_name.setMinimumSize(120,25)
        self.last_name.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.titel_label.setMinimumSize(150,25)
        self.titel_label.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.old_label.setMinimumSize(120,25)
        self.old_label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.new_password.setMinimumSize(120,25)
        self.new_password.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.confirm_password.setMinimumSize(120,25)
        self.confirm_password.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
    ##
    def Button_UI(self):
        pass
    ##
    def feild_UI(self):
        for input in (self.name_line,self.last_line,self.new_p_line,self.old_line,self.confirm_p_line):
            input.setFixedSize(200,40)
            input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            input.setStyleSheet('''
                background-color: white;
                font-family: B Nazanin,"Mirza";
                font-weight: bold;
                font-size: 15px;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 5px;
                padding: 5px;
        ''')
        ##
        for input in (self.new_p_line,self.old_line,self.confirm_p_line):
            input.setFixedSize(200,40)
            input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            input.setStyleSheet('''
                background-color: white;
                font-family: Arial,"Roboto";
                font-weight: bold;
                font-size: 15px;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 5px;
                padding: 5px;
        ''')



