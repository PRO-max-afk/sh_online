from PyQt6.QtWidgets import (
    QWidget, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt


class ProductBox(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 340)
        self.setStyleSheet("background-color: transparent;")
        

        # ایجاد فریم اصلی (کارت سفید)
        self.frame = QFrame(self)
        self.frame.setGeometry(10, 10, 250, 320)
        self.frame.setStyleSheet("background-color: white; border-radius: 15px;")

        # اضافه کردن سایه به فریم
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.frame.setGraphicsEffect(shadow)

        # عنوان بالا
        self.store_label = QLabel("فروشگاه تک", self.frame)
        self.store_label.setStyleSheet('''
            color: black;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 16px;
            ''')
        self.store_label.setGeometry(15, 20, 220, 20)
        self.store_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # تصویر محصول
        self.image_label = QLabel(self.frame)
        pixmap = QPixmap(image_path).scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setGeometry(60, 40, 120, 90)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # خط جداکننده
        self.line = QFrame(self.frame)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("color: #cccccc;")
        self.line.setGeometry(10, 140, 220, 2)

        # متن‌ها
        self.name_lb= QLabel("نام محصول:", self.frame)
        self.na_lb= QLabel("پنیر ماه",self.frame)
        self.barcode_lb= QLabel("بارکد محصول:", self.frame)
        self.bar_lb= QLabel("242421",self.frame)
        self.buy_price= QLabel("قیمت خرید:", self.frame)
        self.bu_lb= QLabel("250", self.frame)
        self.sale_label= QLabel("قیمت فروش:", self.frame)
        self.sa_lb= QLabel("300", self.frame)
        self.number_lb= QLabel("تعداد محصول:", self.frame)
        self.nu_lb= QLabel("200", self.frame)
        self.expire_date= QLabel("تاریخ انقصاء:", self.frame)
        self.exp_lb= QLabel("1404/10/05", self.frame) 
        self.label_UI()

    def add_label(self, text, x, y):
        label = QLabel(text, self.frame)
        label.setStyleSheet('''
            font-family: B Nazanin;
            background-color: yellow;
            font-weight: bold;
            font-size: 15px;
            color: black;
            ''')
        label.setGeometry(x, y, 110, 20)
        label.setFixedSize(125,30)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)

    ##
    def label_UI(self):
        self.name_lb.setGeometry(184,160,0,0)
        self.name_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.name_lb.setFixedSize(67,30)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
        ''')
        ##
        self.na_lb.setGeometry(137,160,0,0)
        self.na_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.na_lb.setFixedSize(48,30)
        self.na_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 14px;
            color: black;
            text-align:center;
        ''')
        ##
        self.barcode_lb.setGeometry(45,160,0,0)
        self.barcode_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.barcode_lb.setFixedSize(75,30)
        self.barcode_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: center;
        ''')
        ##
        self.bar_lb.setGeometry(0,160,0,0)
        self.bar_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bar_lb.setFixedSize(45,30)
        self.bar_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 14px;
            color: black;
            text-align: center;
        ''')
        ##
        self.buy_price.setGeometry(184,210,0,0)
        self.buy_price.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.buy_price.setFixedSize(67,30)
        self.buy_price.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: center;
        ''')
        ##
        self.bu_lb.setGeometry(135,210,0,0)
        self.bu_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bu_lb.setFixedSize(48,30)
        self.bu_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 14px;
            color: black;
            text-align: center;
        ''')
        ##
        self.sale_label.setGeometry(48,210,0,0)
        self.sale_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.sale_label.setFixedSize(75,30)
        self.sale_label.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: center;
        ''')
        ##
        self.sa_lb.setGeometry(0,210,0,0)
        self.sa_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.sa_lb.setFixedSize(44,30)
        self.sa_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 14px;
            color: black;
        ''')
        ##
        self.number_lb.setGeometry(177,260,0,0)
        self.number_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.number_lb.setFixedSize(75,30)
        self.number_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: right;
        ''')
        ##
        self.nu_lb.setGeometry(128,260,0,0)
        self.nu_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.nu_lb.setFixedSize(48,30)
        self.nu_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: center;
        ''')
        ##
        ##
        self.expire_date.setGeometry(59,260,0,0)
        self.expire_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.expire_date.setFixedSize(70,30)
        self.expire_date.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 15px;
            color: black;
            text-align: center;
        ''')
        ##
        self.exp_lb.setGeometry(0,260,0,0)
        self.exp_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.exp_lb.setFixedSize(58,30)
        self.exp_lb.setStyleSheet('''
            font-family: B Nazanin;
            background-color: white;
            font-weight: bold;
            font-size: 14px;
            color: black;
        ''')