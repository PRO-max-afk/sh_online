from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent,QPoint,QPropertyAnimation,QEasingCurve
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

class UserSettings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.feild_UI()
        self.Button_UI()

        


    def init_ui(self):
        self.stack_widget= QStackedWidget()
        self.setCentralWidget(self.stack_widget)
        
        self.user_settings= QWidget()

        main_layout = QVBoxLayout(self.user_settings)
        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("تنظیمات کاربران", self)

        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        datetime_layout = QVBoxLayout()
        self.back_btn= QPushButton()
        datetime_layout.addWidget(self.back_btn)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.label, 1)
        ##
        middle_layout= QGridLayout()
        ###
        user_frame= QFrame()
        user_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        user_frame.setMaximumHeight(170)  # 👈 تنظیم ارتفاع فریم دقیق و جمع‌وجور

        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        user_frame.setGraphicsEffect(shadow)

        ##
        mn_us_lay= QVBoxLayout(user_frame)
        user_layout = QHBoxLayout()
        ##
        tt_layout= QHBoxLayout()
        self.tite_label= QLabel("معلومات کاربر")
        title_lab= QLabel("")
        title_lab.setFixedHeight(50)
        tt_layout.addWidget(self.tite_label)
        tt_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    
        ##
        name_layout= QHBoxLayout()
        self.name_label= QLabel("نام کاربر")
        self.name_line= QLineEdit()
        #
        name_layout.addStretch(0)
        name_layout.addWidget(self.name_line)
        name_layout.addWidget(self.name_label)
        
        ##
        last_layout= QHBoxLayout()
        self.last_name= QLabel("نام فامیلی کاربر")
        self.last_line= QLineEdit()
        #
        last_layout.addStretch(0)
        last_layout.addWidget(self.last_line)
        last_layout.addWidget(self.last_name)
        
       
        ###
        user_layout.addLayout(last_layout)
        user_layout.addLayout(name_layout)
        ##
        tta_lbb= QLabel("")
        tta_lbb.setFixedHeight(50)

        mn_us_lay.addLayout(tt_layout)
        mn_us_lay.addLayout(user_layout)
        mn_us_lay.addWidget(tta_lbb)


        ###ٌ#
        password_frame = QFrame()
        password_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        password_frame.setMaximumHeight(170)  # 👈 تنظیم ارتفاع فریم دقیق و جمع‌وجور

        shadows = QGraphicsDropShadowEffect(self)
        shadows.setBlurRadius(12)
        shadows.setXOffset(0)
        shadows.setYOffset(5)
        shadows.setColor(QColor(0, 0, 0, 70))
        password_frame.setGraphicsEffect(shadows)

        # چیدمان کلی
        mn_lay= QVBoxLayout(password_frame)
        password_layout = QHBoxLayout()

        ###
        titel_layout = QHBoxLayout()
        self.titel_label = QLabel("تغییر رمزعبور")
        self.titel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titel_layout.addWidget(self.titel_label)
        titel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # چیدمان‌ها با فاصله‌ی کم
        old_layout = QHBoxLayout()
        self.old_line = QLineEdit()
        self.old_label = QLabel("رمز عبور قدیمی")
        old_layout.addStretch(0)
        old_layout.addWidget(self.old_line)
        old_layout.addWidget(self.old_label)
        ##
        new_p_layout = QHBoxLayout()
        self.new_password = QLabel("رمز عبور جدید")
        self.new_p_line = QLineEdit()
        self.new_p_line.setEchoMode(QLineEdit.EchoMode.Password)
        #
        new_p_layout.addStretch(0)
        new_p_layout.addWidget(self.new_p_line)
        new_p_layout.addWidget(self.new_password)
        
       
        ##
        confirm_layout = QHBoxLayout()
        self.confirm_password = QLabel("تایید رمزعبور")
        self.confirm_p_line = QLineEdit()
        self.confirm_p_line.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addStretch(0)
        confirm_layout.addWidget(self.confirm_p_line)
        confirm_layout.addWidget(self.confirm_password)
        
        # اضافه‌کردن به چیدمان اصلی
        password_layout.addLayout(confirm_layout)
        password_layout.addLayout(new_p_layout)
        password_layout.addLayout(old_layout)
        
        ###
        tta_Lb= QLabel("")
        tta_Lb.setFixedHeight(50)
        
        ##
        mn_lay.addLayout(titel_layout)
        mn_lay.addLayout(password_layout)
        mn_lay.addWidget(tta_Lb)
        
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
        self.stack_widget.addWidget(self.user_settings)
    
   ##
    def label_UI(self):
        self.label.setMinimumSize(120,20)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        for label in (self.name_label,self.last_name,self.old_label,self.new_password,self.confirm_password):
            label.setMinimumSize(90,5)
            label.setFixedHeight(40)
            label.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
            label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        
        for title in (self.titel_label,self.tite_label):
            title.setMinimumSize(90,5)
            title.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')

    ##
    def Button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.back_settings)
        self.back_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.back_btn.setStyleSheet('''
        QPushButton{
            background-color: transparent;
            border-radius: 27px;
            padding: 5px;
                                    }
        QPushButton:hover{
            background-color: #f5f5f5;
                                    }
        QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            } 
        ''')
        
    ##
    def feild_UI(self):
        for input in (self.name_line,self.last_line,self.new_p_line,self.old_line,self.confirm_p_line):
            input.setFixedSize(200,40)
            input.setPlaceholderText("Enter...")
            input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            input.setStyleSheet('''
                QLineEdit {
                background-color: white;
                font-family:  "Roboto","Arial";
                font-weight: bold;
                font-size: 14px;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #e3e4e6;
            }
        ''')
        
        # تنظیم ترتیب فوکوس به صورت راست به چپ
        self.setTabOrder(self.name_line, self.last_line)
        self.setTabOrder(self.last_line, self.old_line)
        self.setTabOrder(self.old_line, self.new_p_line)
        self.setTabOrder(self.new_p_line, self.confirm_p_line)
        

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
    def back_settings(self):
        from settings import Settings

        self.settings= Settings()
        self.stack_widget.addWidget(self.settings)

        
        self.stack_widget.setCurrentWidget(self.settings)
        ##
        start_pos = QPoint(-self.width(), 0)
        end_pos = QPoint(0, 0)
        self.settings.move(start_pos)
        ##
        self.animate= QPropertyAnimation(self.settings, b"pos",self)
        self.animate.setDuration(700)
        self.animate.setStartValue(start_pos)
        self.animate.setEndValue(end_pos)
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##
    def un_hide(self):
        pass




