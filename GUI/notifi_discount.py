from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QSizePolicy,QPushButton
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath,QIcon,QFontDatabase
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os

class Notifi_Discount_Box(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 130)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()
        self.name= None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: white; border-radius: 20px;")
        main_layout.addWidget(self.frame)


        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.frame.setGraphicsEffect(shadow)

        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 10, 20, 10)
        frame_layout.setSpacing(15)
        

        # تصویر
        self.image_label = QLabel()
        self.image_label.setFixedSize(80, 80)
        ##
        image_layout= QHBoxLayout()
        image_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        image_layout.addWidget(self.image_label)
        ##
        right_layout= QVBoxLayout()
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
   
        # ستون اطلاعات سمت راست
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # لیبل‌ها
        self.name_lb = QLabel("نام محصول:")
        self.na_lb = QLabel("")
        self.number_lb = QLabel("تعداد محصول:")
        self.nu_lb = QLabel("")
        self.disount_precent= QLabel("فیصدی تخفیف%:")
        self.disc_lb= QLabel("")
        self.nt_lb= QLabel("")
        ##
        self.text_lb= QLabel("پایان اعتبار تخفیف")
        self.text_lb.setStyleSheet("color: gray; font-family: B Nazanin; font-weight: bold; font-size: 14px;")
        self.text_lb.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        ##
        self.renew_btn= QPushButton()
        renew_icon= QIcon(self.get_asset_path("refresh_12178617.png"))
        self.renew_btn.setIcon(renew_icon)
        self.renew_btn.setText("تمدید اعتبار تخفیف  ")
        self.renew_btn.setIconSize(QtCore.QSize(30,30))
        self.renew_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.renew_btn.clicked.connect(self.open_discount_form)
        self.renew_btn.setStyleSheet('''
        QPushButton{
                background-color: white;
                color: black;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 14px;
                padding-right: 15px;
                padding-left: 0px;          
                                        }
        QPushButton:hover{
            text-decoration: underline;
                                      }
        QPushButton:pressed{
            color: blue;
                                      }

            
        ''')

        self.set_label_style(self.name_lb)
        self.set_label_style(self.na_lb)
        self.set_label_style(self.number_lb)
        self.set_label_style(self.nu_lb)
        self.set_label_style(self.disount_precent)
        self.set_label_style(self.disc_lb)

        # ستون‌بندی افقی برای هر ردیف اطلاعات
        right_layout.addLayout(self.label_pair(self.na_lb,self.name_lb))
        right_layout.addLayout(self.label_pair(self.nu_lb,self.number_lb))
        right_layout.addLayout(self.label_pair(self.disc_lb, self.disount_precent))
        right_layout.addWidget(self.text_lb)
        #
        
        info_layout.addWidget(self.nt_lb)
        #info_layout.addWidget(self.nt_lb)
        info_layout.addWidget(self.renew_btn)

        # اضافه کردن به چیدمان اصلی فریم
        frame_layout.addLayout(info_layout)
        frame_layout.addStretch(1)  
        frame_layout.addLayout(right_layout)     # ابتدا right_layout اضافه شود
        frame_layout.addLayout(image_layout)
        

    def set_label_style(self, label):
        label.setStyleSheet('''
            font-family: Roboto,'B Nazanin';
            background-color: transparent;
            font-weight: bold;
            font-size: 16px;
            color: black;
        ''')
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def label_pair(self, label1, label2):
        hbox = QHBoxLayout()
        hbox.addWidget(label1)
        hbox.addWidget(label2)
        hbox.addStretch()
        return hbox

    def set_product_info(self, name, number,discount_percent,image_path="default.png"):
        self.na_lb.setText(name)
        self.na_lb.adjustSize()
        self.name= name

        self.nu_lb.setText(str(number))
        self.nu_lb.adjustSize()

        
        self.disc_lb.setText(str(discount_percent))
        self.disc_lb.adjustSize()
        
        self.image_label.setFixedSize(80,80)
        self.image_label.setScaledContents(True)
        if image_path and os.path.exists(image_path):
            original_pixmap = QPixmap(image_path)
        else:
            original_pixmap = QPixmap("default.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.image_label.setPixmap(original_pixmap)
    ##
    def open_discount_form(self):
        from discount import ProductDiscount
        form= ProductDiscount()
        form.set_info(name=self.name)
        form.exec()
        
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None

        # دریافت اطلاعات دیتابیس از سرور
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
    