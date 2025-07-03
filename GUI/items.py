from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent,QPoint,QPropertyAnimation,QEasingCurve,QSize
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush,QPixmap
from PyQt6 import QtCore
from circle import CircularSpinner
import sqlite3
import pymysql
import requests
from notifi_box import Notification
from user_info import UserFetchThread
import threading
from switch import ToggleSwitch
from message_b import MessageBox
from switch import ToggleSwitch
import os
import sys

class ItemsSettings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #D9D9D9")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        self.stack_items= QStackedWidget()
        self.setCentralWidget(self.stack_items)
        self.itms_page= QWidget()

        # لایه اصلی
        main_layout = QVBoxLayout(self.itms_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # اضافه کردن تاپ‌بار و فریم به لایه اصلی
        main_layout.addLayout(self.create_top_bar())
        main_layout.addSpacing(5)
        main_layout.addWidget(self.create_frame1())
        main_layout.addWidget(self.create_frame2())

        self.setLayout(main_layout)
        self.stack_items.addWidget(self.itms_page)

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(15, 30, 20, 0)
        top_bar.setSpacing(10)

        title_label = QLabel("تنظیمات محصولات")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        back_button = QPushButton()
        back_button.setIcon(QIcon(self.get_asset_path('back.png')))
        back_button.setIconSize(QSize(40, 40))
        back_button.setFixedSize(50, 50)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #f8faff;
            }
        """)
        back_button.clicked.connect(self.back_settings)
        top_bar.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        top_bar.addStretch()
        top_bar.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop)

        return top_bar

    def create_frame1(self):
        # ساخت فریم
        frame1 = QFrame()
        frame1.setFixedHeight(340)
        frame1.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")

        # لایه داخل فریم
        frame1_layout = QVBoxLayout()
        frame1_layout.setContentsMargins(0, 0, 0, 0)
        frame1_layout.setSpacing(10)

        frame1_title_label = QLabel("تغییر محصولات")
        frame1_title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        frame1_layout.addWidget(frame1_title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        frame1_search_input = QLineEdit()
        frame1_search_input.setContentsMargins(0, 0, 30, 0)
        frame1_search_input.setPlaceholderText("جستجوی محصولات ...")
        frame1_search_input.setFixedSize(200, 40)
        frame1_search_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #222222;
            font-size: 12px;
        """)
        frame1_layout.addWidget(frame1_search_input, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        frame1_layout.addStretch()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        frame1_search_input.setGraphicsEffect(shadow)

        frame1.setLayout(frame1_layout)

        return frame1
    
    def create_frame2(self):
        frame2 = QFrame()
        frame2.setFixedHeight(150)
        frame2.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)

        frame2_vlayout = QVBoxLayout()
        frame2_vlayout.setContentsMargins(0, 0, 0, 0)
        frame2_vlayout.setSpacing(10)

        frame2_title_label = QLabel("ساخت بارکد")
        frame2_title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame2_vlayout.addWidget(frame2_title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        frame2_hlayout = QHBoxLayout()
        frame2_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame2_hlayout.setSpacing(20)
        frame2_label1 = QLabel("نام محصول")
        frame2_label1.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame2_QLineEdit1 = QLineEdit()
        frame2_QLineEdit1.setFixedSize(200, 40)
        frame2_QLineEdit1.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; color: #222222; font-size: 12px;")
        
        frame2_label2 = QLabel("تولید بارکد")
        frame2_label2.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame2_QLineEdit2 = QLineEdit()
        frame2_QLineEdit2.setFixedSize(200, 40)
        frame2_QLineEdit2.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; color: #222222; font-size: 12px;")
        
        frame2_label3 = QLabel("انتخاب مسیر")
        frame2_label3.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame2_QLineEdit3 = QLineEdit()
        frame2_QLineEdit3.setFixedSize(200, 40)
        frame2_QLineEdit3.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; color: #222222; font-size: 12px;")

        frame2_hlayout.addWidget(frame2_label1)
        frame2_hlayout.addWidget(frame2_QLineEdit1)
        
        frame2_hlayout.addWidget(frame2_label2)
        frame2_hlayout.addWidget(frame2_QLineEdit2)
        
        frame2_hlayout.addWidget(frame2_label3)
        frame2_hlayout.addWidget(frame2_QLineEdit3)
        frame2_hlayout.addStretch()

        barcode_icon = QLabel()
        barcode_icon.setPixmap(QPixmap(self.get_asset_path('Barcode.png')).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))

        frame2_hlayout.addWidget(barcode_icon)
    
        frame2_vlayout.addLayout(frame2_hlayout)
        frame2.setLayout(frame2_vlayout)

        return frame2
    ##
    def back_settings(self):
        from settings import Settings

        self.settings= Settings()
        self.stack_items.addWidget(self.settings)

        
        self.stack_items.setCurrentWidget(self.settings)
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
    

