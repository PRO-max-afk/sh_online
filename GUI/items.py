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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        frame1_search_input.setGraphicsEffect(shadow)

        fields = [
            "نام محصول", "بارکد محصول", "قیمت فروش",
            "قیمت خرید", "تعداد محصول", "تعداد هر بسته",
            "قیمت عمده", "تاریخ تولید", "تاریخ انقضا"
        ]

        # به جای frame1_layout، لایه‌ای که قبلاً به فریم اختصاص داده‌ای قرار بده
        for i in range(0, len(fields), 3):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(15)
            row_layout.setContentsMargins(0, 0, 0, 0)  # در صورت نیاز تنظیم کن

            for j in range(3):
                if i + j < len(fields):
                    label = QLabel(fields[i + j])
                    label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

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

        frame1.setLayout(frame1_layout)

        return frame1
    
    def create_frame2(self):
        frame2 = QFrame()
        frame2.setFixedHeight(150)
        frame2.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
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
        frame2_hlayout.setSpacing(25)
        frame2_hlayout.setContentsMargins(20, 0, 20, 0)

        fields = ["نام محصول", "تولید بارکد", "انتخاب مسیر"]
        line_edits = []

        for field in fields:
            label = QLabel(field)
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            line_edit = QLineEdit()
            line_edit.setStyleSheet("""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                color: #222;
            """)
            line_edit.setFixedSize(200, 40)
            line_edits.append(line_edit)

            container = QHBoxLayout()
            container.setContentsMargins(20, 0, 5, 0)
            container.addWidget(label)
            container.addWidget(line_edit)
            frame2_hlayout.addLayout(container)


        barcode_icon = QLabel()
        barcode_icon.setPixmap(QPixmap('assets/Barcode.png').scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        barcode_icon.setPixmap(QPixmap(self.get_asset_path('Barcode.png')).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        barcode_icon.setStyleSheet("background-color: white; border-radius: 5px;")
        frame2_hlayout.addWidget(barcode_icon)
    
        frame2_vlayout.addLayout(frame2_hlayout)

        generate_barcode_button = QPushButton("ساخت بارکد")
        generate_barcode_button.setIcon(QIcon(self.get_asset_path("Check Mark.png")))
        generate_barcode_button.setIconSize(QSize(24, 24))
        generate_barcode_button.setFixedSize(130, 40)
        generate_barcode_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        generate_barcode_button.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                padding: 5px 10px;
        }
            QPushButton:hover {
                background-color: #00B44A;
        }
    """)
        frame2_hlayout.addWidget(generate_barcode_button)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(40, 0, 0, 10)
        button_layout.addStretch()
        button_layout.addWidget(generate_barcode_button)

        frame2_vlayout.addLayout(button_layout)

        frame2.setLayout(frame2_vlayout)

        return frame2

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
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ItemsSettings()
    window.show()
    sys.exit(app.exec())