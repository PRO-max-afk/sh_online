from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QSizePolicy,QPushButton,QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath,QIcon
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os

class Order_Box(QWidget):
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
        ##
        table_layout= QVBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        table_layout.setContentsMargins(0,0,0,0)
        table_layout.setSpacing(0)
        ##
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["مقدار", "نام"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # تنظیم استایل
        self.table.setStyleSheet('''
            QTableWidget {
                font-family: B Nazanin;
                font-size: 12px;
                border: none;
                color: black;
                font-weight: bold;
                background-color: transparent;
                gridline-color: black;
            }
            QHeaderView::section {
                background-color: orange;
                font-weight: bold;
                font-size: 12px;
                height: 20px;
            }
        ''')

        # تعیین سایز ستون‌ها
        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 70)

        # تنظیم ارتفاع ردیف‌ها
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 20)

        

        # وسط‌چین کردن محتوای سطرها
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is None:
                    item = QTableWidgetItem("")
                    self.table.setItem(row, col, item)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        ##
        self.table.setMinimumHeight(60)
        self.table.setMaximumHeight(100)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # سایز ثابت برای جلوگیری از کش آمدن در Layout
        self.table.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        table_layout.addWidget(self.table)
        
        # تصویر
        self.image_label = QLabel()
        self.image_label.setFixedSize(80, 80)
        ##
        image_layout= QHBoxLayout()
        image_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignRight)
        image_layout.addWidget(self.image_label)
        ##
        right_layout= QVBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
   
        btn_layout= QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        # لیبل‌ها
        self.number_order= QLabel("شماره سفارش:")
        self.number= QLabel("")
        self.name_lb = QLabel("نام شخص:")
        self.na_lb = QLabel("")
        self.address_lb = QLabel("آدرس مشتری:")
        self.address = QLabel("")
        self.plag_lb= QLabel("پلاک خانه:")
        self.plag= QLabel("")
        self.phone_lb = QLabel("شماره تماس:")
        self.phone = QLabel("")

        ##
        self.accept_btn = QPushButton("قبول")
        self.reject_btn = QPushButton("رد")

        self.accept_btn.setStyleSheet('''
            QPushButton{
                background-color: limegreen; 
                color: white; 
                font-family: B Nazanin; 
                font-weight: bold;
                padding: 6px 20px; 
                border-radius: 5px;
                                      }
            QPushButton:hover{
                    background-color: #b2fa7f;
                                    }
            QPushButton:Pressed{
                background-color: limegreen;
                                      }
            ''')
        self.reject_btn.setStyleSheet('''
            QPushButton{
                background-color: red; 
                color: white; 
                font-family: B Nazanin; 
                font-weight: bold;
                padding: 6px 20px; 
                border-radius: 5px;
                                      }
            QPushButton:hover{
                    background-color: #f55353;
                                    }
            QPushButton:Pressed{
                background-color: red;
                                      }
        ''')
        
        btn_layout.addWidget(self.reject_btn)
        btn_layout.addWidget(self.accept_btn)
       

        self.set_label_style(self.number_order)
        self.set_label_style(self.number)
        self.set_label_style(self.name_lb)
        self.set_label_style(self.na_lb)
        self.set_label_style(self.address_lb)
        self.set_label_style(self.address)
        self.set_label_style(self.plag_lb)
        self.set_label_style(self.plag)
        self.set_label_style(self.phone_lb)
        self.set_label_style(self.phone)

        # ستون‌بندی افقی برای هر ردیف اطلاعات
        right_layout.addLayout(self.label_pair(self.number, self.number_order))
        right_layout.addLayout(self.label_pair(self.na_lb,self.name_lb))
        right_layout.addLayout(self.label_pair(self.address,self.address_lb))
        right_layout.addLayout(self.label_pair(self.plag,self.plag_lb))
        right_layout.addLayout(self.label_pair(self.phone,self.phone_lb))
        
        frame_layout.addLayout(table_layout)  # اضافه کردن جدول در سمت چپ
        frame_layout.addSpacing(100)
        frame_layout.addLayout(btn_layout)
        frame_layout.addSpacing(900)
        frame_layout.addLayout(right_layout)    # ابتدا right_layout اضافه شود
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
        hbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        return hbox
    ##
    def set_product_info(self, name, number, address, plaged,phone,image_path="default.png", product_name="", quantity=""):
        self.na_lb.setText(name)

        self.number.setText(str(number))

        self.address.setText(address)

        self.plag.setText(str(plaged))
        
        self.phone.setText(str(phone))

        # تنظیم مقادیر جدول
        self.table.setItem(0, 1, QTableWidgetItem(product_name))
        self.table.setItem(0, 0, QTableWidgetItem(str(quantity)))

        # تنظیم تصویر
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
