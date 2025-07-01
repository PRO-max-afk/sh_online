from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFont, QColor, QFontDatabase
from PyQt6.QtCore import Qt
import os

class ProductBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(270, 360)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()

        self.frame = QFrame(self)
        self.frame.setGeometry(10, 10, 270, 340)
        self.frame.setStyleSheet("background-color: white; border-radius: 20px;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.frame.setGraphicsEffect(shadow)

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
        self.barcode_lb = QLabel("بارکد:", self.frame)
        self.bar_lb = QLabel("", self.frame)
        self.buy_price = QLabel("قیمت خرید:", self.frame)
        self.bu_lb = QLabel("", self.frame)
        self.sale_label = QLabel("قیمت فروش:", self.frame)
        self.sa_lb = QLabel("", self.frame)
        self.number_lb = QLabel("تعداد محصول:", self.frame)
        self.nu_lb = QLabel("", self.frame)
        self.expire_date = QLabel("تاریخ انقضاء:", self.frame)
        self.exp_lb = QLabel("", self.frame)
        self.big_s_lb= QLabel("موجودی فعلی:",self.frame)
        self.bg_lb= QLabel("",self.frame)
        self.big_price= QLabel("قمیت عمده:",self.frame)
        self.big_sa_lb= QLabel("",self.frame)

        self.label_UI()

    def label_UI(self):
        labels = [
            (self.name_lb, 198, 160),
            (self.na_lb, 145, 160),
            (self.barcode_lb, 85, 160),
            (self.bar_lb, 3, 160),
            (self.buy_price, 190, 210),
            (self.bu_lb, 150, 210),
            (self.sale_label, 59, 210),
            (self.sa_lb, 15, 210),
            (self.number_lb, 185, 260),
            (self.nu_lb, 150, 260),
            (self.expire_date, 63, 260),
            (self.exp_lb, 5, 260),
            (self.big_s_lb,190,300),
            (self.bg_lb,145,300),
            (self.big_price,59,300),
            (self.big_sa_lb,15,300)
        ]
        for label, x, y in labels:
            label.move(x, y)
            label.setStyleSheet('''
                font-family: B Nazanin;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                color: black;
            ''')
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def set_product_info(self, name, barcode, buy_price, sale_price, number, expire_date,big_sub,big_price,image_path="default.png"):
        self.na_lb.setText(name)
        self.na_lb.adjustSize()
        
        self.bar_lb.setText(barcode)
        self.bar_lb.adjustSize()
        
        self.bu_lb.setText(str(buy_price))
        self.bu_lb.adjustSize()
        
        self.sa_lb.setText(str(sale_price))
        self.sa_lb.adjustSize()
        
        self.nu_lb.setText(str(number))
        self.nu_lb.adjustSize()
        
        self.exp_lb.setText(expire_date)
        self.exp_lb.adjustSize()

        self.bg_lb.setText(str(big_sub))
        self.bg_lb.adjustSize()

        self.big_sa_lb.setText(str(big_price))
        self.big_sa_lb.adjustSize()


        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(120, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            pixmap = QPixmap("default.png").scaled(120, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        
        self.image_label.setPixmap(pixmap)
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
    ##