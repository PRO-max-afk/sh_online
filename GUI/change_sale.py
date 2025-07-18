from PyQt6.QtWidgets import (QApplication,QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QFileDialog,QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,pyqtSignal,QEvent,QPoint,QPropertyAnimation,QEasingCurve,QSize
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush,QPixmap
import sqlite3
from message_b import MessageBox
from barcode import EAN13
from barcode.writer import ImageWriter
import os,random
import datetime
import sys


class ChangingFactor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #D9D9D9;")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self.load_all_fonts()

    def setup_ui(self):
        self.stack_items = QStackedWidget()
        self.setCentralWidget(self.stack_items)
        self.items_page = QWidget()

        main_layout = QVBoxLayout(self.items_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addLayout(self.create_top_bar())
        main_layout.addWidget(self.create_frame())
        main_layout.addWidget(self.Invisible_frame())

        self.stack_items.addWidget(self.items_page)

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(15, 30, 20, 0)
        top_bar.setSpacing(10)

        title_label = QLabel("تغییرات فاکتور")
        title_label.setStyleSheet("color: black; font-family: Mirza; font-size: 20px; font-weight: bold;")

        back_button = QPushButton()
        back_button.setIcon(QIcon(self.get_asset_path('left.png')))
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

        top_bar.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        top_bar.addStretch()
        top_bar.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop)

        return top_bar
    
    def create_frame(self):
        frame = QFrame()
        frame.setMaximumHeight(400)
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")

        frame_shadow= QGraphicsDropShadowEffect(self)
        frame_shadow.setBlurRadius(10)
        frame_shadow.setOffset(0,5)
        frame_shadow.setColor(QColor(0,0,0,70))
        frame.setGraphicsEffect(frame_shadow)

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(10)

        frame_title_label = QLabel("تغییر فاکتور فروش")
        frame_title_label.setStyleSheet("background-color:transparent; color: black; font-family: Mirza,'B Nazanin'; font-size: 18px; font-weight: bold;")
        frame_title_label.setMinimumHeight(25)

        frame_layout.addWidget(frame_title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.frame_search_input = QLineEdit()
        self.frame_search_input.setContentsMargins(0, 0, 30, 0)
        self.frame_search_input.setPlaceholderText("نمبر فاکتور...")
        self.frame_search_input.setFixedSize(200, 40)
        self.frame_search_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #222222;
            font-size: 14px;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            padding: 5px;
        """)
        frame_layout.addWidget(self.frame_search_input, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        frame_layout.addStretch()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.frame_search_input.setGraphicsEffect(shadow)

        frame.setLayout(frame_layout)

        return frame
    
    def Invisible_frame(self):
        invisible_frame = QFrame()
        invisible_frame.setMaximumHeight(300)
        invisible_frame.setStyleSheet("background-color: transparent; border: none;")
        
        invisible_frame_layout = QVBoxLayout()
        invisible_frame_layout.setContentsMargins(0, 0, 0, 0)
        invisible_frame_layout.setSpacing(10)

        invisible_frame_layout.addWidget(invisible_frame)

        return invisible_frame


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
    window = ChangingFactor()
    window.show()
    sys.exit(app.exec())