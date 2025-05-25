from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QSizePolicy,QPushButton
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath,QIcon
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os

class Notifi_Box(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 130)
        self.setStyleSheet("background-color: transparent;")

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
        self.expire_date = QLabel("تاریخ انقضاء:")
        self.exp_lb = QLabel("")
        self.text_lb= QLabel("محصولات انقضاء شده")
        self.nt_lb= QLabel("تاریخ محصول گذشته است")
        self.nt_lb.setFixedSize(140,25)
        self.nt_lb.setStyleSheet("background-color: red; font-family: Mirza; font-weight: bold; font-size: 15px; color: white; border-radius: 5px;")
        self.text_lb.setStyleSheet("color: gray; font-family: B Nazanin; font-weight: bold; font-size: 14px;")
        self.text_lb.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.nt_lb.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        ##
        self.delete_btn= QPushButton()
        delete_icon= QIcon(self.get_asset_path("trash.png"))
        self.delete_btn.setIcon(delete_icon)
        self.delete_btn.setText("حذف محصول")
        self.delete_btn.setIconSize(QtCore.QSize(20,20))
        self.delete_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.delete_btn.setStyleSheet('''
        QPushButton{
                background-color: white;
                color: red;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 12px;
                padding-right: 15px;
                padding-left: 0px;          
                                        }
        QPushButton:hover{
            text-decoration: underline;
                                      }
        QPushButton:pressed{
            color: red;
                                      }

            
        ''')

        self.set_label_style(self.name_lb)
        self.set_label_style(self.na_lb)
        self.set_label_style(self.number_lb)
        self.set_label_style(self.nu_lb)
        self.set_label_style(self.expire_date)
        self.set_label_style(self.exp_lb)

        # ستون‌بندی افقی برای هر ردیف اطلاعات
        right_layout.addLayout(self.label_pair(self.na_lb,self.name_lb))
        right_layout.addLayout(self.label_pair(self.nu_lb,self.number_lb))
        right_layout.addWidget(self.text_lb)
        #
        
        info_layout.addLayout(self.label_pair(self.exp_lb,self.expire_date))
        info_layout.addWidget(self.nt_lb)
        info_layout.addWidget(self.delete_btn)

        # اضافه کردن به چیدمان اصلی فریم
        # اضافه کردن به چیدمان اصلی فریم (ترتیب اصلاح شده)
                      # سپس استرچ برای هل دادن بقیه به چپ
        frame_layout.addLayout(info_layout)
        frame_layout.addStretch(1)  
        frame_layout.addLayout(right_layout)     # ابتدا right_layout اضافه شود
        frame_layout.addLayout(image_layout)
        

        

    def set_label_style(self, label):
        label.setStyleSheet('''
            font-family: B Nazanin;
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

    def set_product_info(self, name, number, expire_date, image_path="default.png"):
        self.na_lb.setText(name)
        self.na_lb.adjustSize()

        self.nu_lb.setText(str(number))
        self.nu_lb.adjustSize()

        self.exp_lb.setText(expire_date)
        self.exp_lb.adjustSize()

        if image_path and os.path.exists(image_path):
            original_pixmap = QPixmap(image_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        else:
            original_pixmap = QPixmap("default.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        rounded = QPixmap(80, 80)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 80, 80)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()

        self.image_label.setPixmap(rounded)
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
    ##
