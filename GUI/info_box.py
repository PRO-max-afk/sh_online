from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFont, QColor, QFontDatabase
from PyQt6.QtCore import Qt
import os

class ProductBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 340)
        self.setStyleSheet("background-color: transparent;")

        self.frame = QFrame(self)
        self.frame.setGeometry(10, 10, 250, 320)
        self.frame.setStyleSheet("background-color: white; border-radius: 15px;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.frame.setGraphicsEffect(shadow)

        # عنوان فروشگاه
        self.store_label = QLabel("فروشگاه تک", self.frame)
        self.store_label.setStyleSheet('''
            color: black;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 16px;
        ''')
        self.store_label.setGeometry(15, 20, 220, 20)
        self.store_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # تصویر محصول (خالی تا بعداً ست شود)
        self.image_label = QLabel(self.frame)
        self.image_label.setGeometry(60, 40, 120, 90)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line = QFrame(self.frame)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("color: #cccccc;")
        self.line.setGeometry(10, 140, 220, 2)

        # ایجاد لیبل‌ها
        self.name_lb = QLabel("نام محصول:", self.frame)
        self.na_lb = QLabel("", self.frame)
        self.barcode_lb = QLabel("بارکد محصول:", self.frame)
        self.bar_lb = QLabel("", self.frame)
        self.buy_price = QLabel("قیمت خرید:", self.frame)
        self.bu_lb = QLabel("", self.frame)
        self.sale_label = QLabel("قیمت فروش:", self.frame)
        self.sa_lb = QLabel("", self.frame)
        self.number_lb = QLabel("تعداد محصول:", self.frame)
        self.nu_lb = QLabel("", self.frame)
        self.expire_date = QLabel("تاریخ انقضاء:", self.frame)
        self.exp_lb = QLabel("", self.frame)

        self.label_UI()

    def label_UI(self):
        ## تنظیم استایل لیبل‌ها
        labels = [
            (self.name_lb, 184, 160, 67, 30),
            (self.na_lb, 137, 160, 48, 30),
            (self.barcode_lb, 45, 160, 75, 30),
            (self.bar_lb, 0, 160, 45, 30),
            (self.buy_price, 184, 210, 67, 30),
            (self.bu_lb, 135, 210, 48, 30),
            (self.sale_label, 48, 210, 75, 30),
            (self.sa_lb, 0, 210, 44, 30),
            (self.number_lb, 177, 260, 75, 30),
            (self.nu_lb, 128, 260, 48, 30),
            (self.expire_date, 59, 260, 70, 30),
            (self.exp_lb, 0, 260, 58, 30),
        ]
        for label, x, y, w, h in labels:
            label.setGeometry(x, y, 0, 0)
            label.setFixedSize(w, h)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            label.setStyleSheet('''
                font-family: B Nazanin;
                background-color: white;
                font-weight: bold;
                font-size: 14px;
                color: black;
            ''')

    def set_product_info(self, name, barcode, buy_price, sale_price, number, expire_date, image_path="default.png"):
        """تنظیم اطلاعات محصول روی جعبه"""
        self.na_lb.setText(name)
        self.bar_lb.setText(barcode)
        self.bu_lb.setText(str(buy_price))
        self.sa_lb.setText(str(sale_price))
        self.nu_lb.setText(str(number))
        self.exp_lb.setText(expire_date)

        # بارگذاری عکس
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            pixmap = QPixmap("default.png").scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.image_label.setPixmap(pixmap)
