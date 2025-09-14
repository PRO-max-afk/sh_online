from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect,QTextEdit,QStyledItemDelegate, QSizePolicy,QScrollArea,QComboBox,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QPainterPath,QFontDatabase,QPixmap,QBrush,QPalette,QPainter
from PyQt6 import QtCore
from circle import CircularSpinner
import sqlite3
import pymysql
import requests
from notifi_box import Notification
from calendars import JalaliCalendar
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import threading
from switch import ToggleSwitch
from message_b import MessageBox
from switch import ToggleSwitch
import os
from db_connection import Connection
from reme import Customer_Pay
from reme_buy import Customer_Buy
from reme_sell import Customer_Sell

class Customer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.in_UI()
        self.load_all_fonts()
        self.lable_UI()
        self.Button_UI()

    def in_UI(self):
        self.cust_widget= QStackedWidget()
        self.setCentralWidget(self.cust_widget)
        self.customer_page= QWidget()
        ##
        main_layout= QVBoxLayout(self.customer_page)
        top_layout= QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        ##
        self.top_label= QLabel("گزارش حساب مشتریان")
        back_layout= QHBoxLayout()
        self.back_btn= QPushButton()
        back_layout.addWidget(self.back_btn)
        ###
        top_layout.addLayout(back_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.top_label)
        ### middle page
        middle_layout= QHBoxLayout()
        ##
        middle_layout.addWidget(self.frame2(),1)
        middle_layout.addWidget(self.frame1(),2)
        

        ##
        main_layout.addSpacing(10)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addStretch()
        self.cust_widget.addWidget(self.customer_page)
    ##
    def frame1(self):
        frame1= QFrame()
        frame1.setStyleSheet("background-color: white; border-radius: 15px;")
        frame_layout= QVBoxLayout(frame1)
        frame_layout.setSpacing(5)
        ##
        self.man_lable= QLabel()
        frame_layout.addWidget(self.man_lable, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight))
        ###
        box_layout= QHBoxLayout()
        ##
        self.customer_p= Customer_Pay()
        self.customer_b= Customer_Buy()
        self.customer_s= Customer_Sell()
        #
        box_layout.addWidget(self.customer_p)
        box_layout.addWidget(self.customer_b)
        box_layout.addWidget(self.customer_s)
        ###
        frame_layout.addLayout(box_layout)
        return frame1
    ##
    def frame2(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 15px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(10)
        frame_layout.setContentsMargins(15, 15, 15, 15)

        # --- بخش بالا (عکس + اطلاعات کاربر) ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # عکس پروفایل دایره‌ای
        self.profile_label = QLabel()
        pixmap = QPixmap(self.get_asset_path("man_18663555.png"))
        self.profile_label.setPixmap(self.make_round_pixmap(pixmap, 60))  # تصویر دایره‌ای
        self.profile_label.setFixedSize(60, 60)
        self.profile_label.setScaledContents(True)
        top_layout.addWidget(self.profile_label, alignment=Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignRight)

        # اطلاعات کاربر
        info_layout = QVBoxLayout()
        self.name_label = QLabel("مصطفی نعیمی")
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; font-family: B Nazanin;")

        self.phone_label = QLabel("03123456789")
        self.phone_label.setStyleSheet("font-size: 14px; color: black; font-family: B Nazanin;")

        self.email_label = QLabel("mostafafa.naim/@example.com")
        self.email_label.setStyleSheet("font-size: 13px; color: gray; font-family: B Nazanin;")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.phone_label)
        info_layout.addWidget(self.email_label)

        top_layout.addLayout(info_layout)
        top_layout.addStretch()

        # --- بخش پایین (دکمه/Label سبز) ---
        self.green_btn = QLabel("حب نحلی")
        self.green_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_btn.setStyleSheet("""
            background-color: #E9FFF1;
            color: #00994d;
            font-size: 16px;
            font-family: B Nazanin;
            font-weight: bold;
            border-radius: 10px;
            padding: 6px 15px;
        """)

        # افزودن به لایه اصلی
        frame_layout.addLayout(top_layout)
        #frame_layout.addWidget(self.green_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return frame


    ##
    def lable_UI(self):
        self.top_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        man_icon= QPixmap(self.get_asset_path("man_18663555.png"))
        self.man_lable.setPixmap(self.make_round_pixmap(man_icon,70))
        self.man_lable.setScaledContents(True)
        self.man_lable.setFixedSize(70,70)
    ##
    def Button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.open_reports)
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

    ##
    def make_round_pixmap(self,pixmap: QPixmap, size: int = 50) -> QPixmap:
        # تغییر اندازه
        pixmap = pixmap.scaled(
                size, size, 
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)

        # ماسک دایره‌ای
        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded
    ##
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
    ###
    def open_reports(self):
        from finance import Money
        self.finace= Money()
        self.cust_widget.addWidget(self.finace)
        self.cust_widget.setCurrentWidget(self.finace)
        
        ##animation:
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.finace.move(start_pos)
        ##
        animation= QPropertyAnimation(self.finace, b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    
