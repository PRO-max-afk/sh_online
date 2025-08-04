from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QColor, QFontDatabase
from PyQt6.QtCore import Qt
import os


class Stock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 50)
        self.setMaximumSize(170, 100)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()

        # فریم اصلی
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border-radius: 20px;")

        # لایه کلی روی فریم
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(14, 12, 14, 12)
        frame_layout.setSpacing(12)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        # آیکون
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(45, 45)
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_path = self.get_asset_path("clock_18481836 (1).png")
        if icon_path:
            icon_pix = QPixmap(icon_path)
            self.icon_label.setPixmap(icon_pix)

        # لایه متن‌ها
        text_layout = QVBoxLayout()
        text_layout.setSpacing(10)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.number_label = QLabel("0")
        self.number_label.setStyleSheet("color: black; font-family: PoetsenOne; font-size: 18px; font-weight: bold;")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("پایان اعتبار تخفیف")
        self.text_label.setStyleSheet("color: #666666; font-family: B Nazanin; font-size: 12px; font-weight: bold;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        text_layout.addWidget(self.number_label)
        text_layout.addWidget(self.text_label)

        frame_layout.addWidget(self.icon_label)
        frame_layout.addLayout(text_layout)

        # لایه اصلی
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)

    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None

    def set_product_info(self, number: int):
        self.number_label.setText(str(number))

    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")

        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return

        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf", ".TTF")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
