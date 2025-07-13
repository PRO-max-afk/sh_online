from PyQt6.QtWidgets import (QApplication,QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QGraphicsColorizeEffect,QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
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
        self.load_all_fonts()

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
        main_layout.addWidget(self.create_frame3()) # برای بلند تنظیم دو فریم بالا فریم سوم را ساختم
      
        self.setLayout(main_layout)
        self.stack_items.addWidget(self.itms_page)

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(15, 30, 20, 0)
        top_bar.setSpacing(10)

        title_label = QLabel("تنظیمات محصولات")
        title_label.setStyleSheet('''
            color: black;
            font-family: Mirza;
            font-size: 20px;
            font-weight: blod;
        ''')

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
        frame1.setMinimumHeight(340)
        frame1.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")

        frame_shadow= QGraphicsDropShadowEffect(self)
        frame_shadow.setBlurRadius(10)
        frame_shadow.setOffset(0,5)
        frame_shadow.setColor(QColor(0,0,0,70))
        frame1.setGraphicsEffect(frame_shadow)


        # لایه داخل فریم
        frame1_layout = QVBoxLayout()
        frame1_layout.setContentsMargins(0, 0, 0, 0)
        frame1_layout.setSpacing(10)

        frame1_title_label = QLabel("تغییر محصولات")
        frame1_title_label.setStyleSheet("background-color:transparent; color: black; font-family: Mirza,'B Nazanin'; font-size: 18px; font-weight: bold;")
        frame1_title_label.setMinimumHeight(25)

        frame1_layout.addWidget(frame1_title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        frame1_search_input = QLineEdit()
        frame1_search_input.setContentsMargins(0, 0, 30, 0)
        frame1_search_input.setPlaceholderText("جستجوی محصولات ...")
        frame1_search_input.setFixedSize(250, 45)
        frame1_search_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #222222;
            font-size: 14px;
            font-family: B Nazanin, 'arial';
            font-weight: bold;
            padding: 5px;
        """)
        frame1_layout.addWidget(frame1_search_input, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        frame1_layout.addStretch()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        frame1_search_input.setGraphicsEffect(shadow)

        fields = [
            "نام محصول: ", "بارکد محصول: ", "قیمت خرید: ",
            "قیمت فروش: ", "قیمت عمده: ", "تعداد محصول: ",
            "تعداد هر بسته: ", "تاریخ تولید", "تاریخ انقضاء: "
        ]

        # به جای frame1_layout، لایه‌ای که قبلاً به فریم اختصاص داده‌ای قرار بده
        for i in range(0, len(fields), 3):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.setContentsMargins(0, 0, 0, 0)  # در صورت نیاز تنظیم کن
            row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for j in range(3):
                if i + j < len(fields):
                    label = QLabel(fields[i + j])
                    label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                    label.setFixedWidth(80)

                    line_edit = QLineEdit()
                    line_edit.setFixedSize(200, 40)
                    line_edit.setStyleSheet("""
                        background-color: white;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 12px;
                        color: #222;
                    """)

                    pair_layout = QHBoxLayout()
                    pair_layout.setSpacing(5)
                    pair_layout.addWidget(label)
                    pair_layout.addWidget(line_edit)
                    pair_layout.addStretch()

                    row_layout.addLayout(pair_layout)

            # لایه افقی را به لایه اصلی فریم اضافه کن (مثلاً frame1_layout)
            frame1_layout.addLayout(row_layout)
            frame1_layout.addStretch()

            bottom_layout = QHBoxLayout()
            bottom_layout.setContentsMargins(20, 0, 20, 0)
            bottom_layout.setSpacing(20)

            # دکمه سمت راست
            save_button = QPushButton("ذخیره تغییرات")
            save_button.setFixedSize(120, 40)
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #00C853;
                    color: white;
                    border-radius: 8px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #00B44A;
                }
            """)

            # آیکون وسط
            center_icon = QLabel()
            center_icon.setPixmap(QPixmap(self.get_asset_path("Upload.png")).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            center_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # دکمه سمت چپ
            upload_button = QPushButton("آپلود تصویر")
            upload_button.setFixedSize(100, 40)
            upload_button.setStyleSheet("""
                QPushButton {
                    background-color: #304FFE;
                    color: white;
                    border-radius: 8px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1E40FF;
                }
            """)

            # ترتیب افزودن به layout: چپ ← وسط ← راست
            bottom_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignLeft)
            bottom_layout.addStretch()
            bottom_layout.addWidget(center_icon)
            bottom_layout.addStretch()
            bottom_layout.addWidget(upload_button, alignment=Qt.AlignmentFlag.AlignRight)

        # افزودن این layout به layout اصلی فریم
        frame1_layout.addLayout(bottom_layout)

        frame1.setLayout(frame1_layout)

        return frame1
    
    def create_frame2(self):
        frame2 = QFrame()
        frame2.setMinimumHeight(140)
        frame2.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        frame2.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        frame_shadow= QGraphicsDropShadowEffect(self)
        frame_shadow.setBlurRadius(10)
        frame_shadow.setOffset(0,5)
        frame_shadow.setColor(QColor(0,0,0,70))
        frame2.setGraphicsEffect(frame_shadow)

        frame2_vlayout = QVBoxLayout()
        frame2_vlayout.setContentsMargins(10, 10, 10, 10)
        frame2_vlayout.setSpacing(10)

        # عنوان بالای فرم
        frame2_title_label = QLabel("ساخت بارکد")
        frame2_title_label.setStyleSheet('''color: black; font-family: Mirza,'B Nazanin'; font-weight: bold; font-size:16px;''')
        frame2_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame2_vlayout.addWidget(frame2_title_label)

        # لایه افقی اصلی
        frame2_hlayout = QHBoxLayout()
        frame2_hlayout.setSpacing(20)
        frame2_hlayout.setContentsMargins(10, 0, 10, 0)

        fields = ["نام محصول:", "تولید بارکد:", "انتخاب مسیر:"]
        line_edits = []

        for field in fields:
            label = QLabel(field)
            label.setStyleSheet('''
                background-color: white;
                color: black;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 16px;
            ''')
            label.setFixedWidth(100)  # اطمینان از هم‌راستایی
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            line_edit = QLineEdit()
            line_edit.setStyleSheet("""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                color: #222;
            """)
            line_edit.setMinimumWidth(150)
            line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            line_edits.append(line_edit)

            # بسته‌بندی هر لیبل و ورودی در یک layout جدا
            pair_layout = QHBoxLayout()
            pair_layout.setSpacing(10)
            pair_layout.addWidget(label)
            pair_layout.addWidget(line_edit)

            pair_widget = QWidget()
            pair_widget.setLayout(pair_layout)
            pair_widget.setStyleSheet("background-color: white;")
            pair_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            frame2_hlayout.addWidget(pair_widget)

        # آیکون بارکد
        barcode_icon = QLabel()
        barcode_icon.setPixmap(QPixmap(self.get_asset_path('barcode_2089366.png')).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
        barcode_icon.setStyleSheet("background-color: white; border-radius: 5px;")
        barcode_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        frame2_hlayout.addWidget(barcode_icon)

        # دکمه ساخت بارکد
        generate_barcode_button = QPushButton("ساخت بارکد")
        generate_barcode_button.setIcon(QIcon(self.get_asset_path("Check Mark.png")))
        generate_barcode_button.setIconSize(QSize(24, 24))
        generate_barcode_button.setMinimumWidth(110)
        generate_barcode_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        generate_barcode_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        generate_barcode_button.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-family: Mirza;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #00B44A;
            }
        """)
        frame2_hlayout.addWidget(generate_barcode_button)

        # افزودن لایه افقی به لایه عمودی اصلی
        frame2_vlayout.addLayout(frame2_hlayout)

        frame2.setLayout(frame2_vlayout)
        return frame2
    
    def create_frame3(self):
        frame3=QFrame()
        frame3.setStyleSheet("background-color:transparent; border-radius:10px;")    
        return frame3



    def back_settings(self):
        from settings import Settings
        self.settings_main= Settings()
        self.stack_items.addWidget(self.settings_main)
        self.stack_items.setCurrentWidget(self.settings_main)
        self.settings_main.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        ##animation:
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.settings_main.move(start_pos)
        ##
        animation= QPropertyAnimation(self.settings_main, b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
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
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ItemsSettings()
    window.show()
    sys.exit(app.exec())