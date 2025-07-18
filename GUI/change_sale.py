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

        self.setLayout(main_layout)
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