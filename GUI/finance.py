from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtCore import Qt,QTimer,QThread, pyqtSignal,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QFontDatabase
from PyQt6 import QtCore
import jdatetime
import os
from decimal import Decimal
import threading
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt


class Money(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.set_today_date()
        self.set_today_time()
        self.button_UI()
        self.load_all_fonts()


    def init_ui(self):
        self.stack= QStackedWidget()
        self.setCentralWidget(self.stack)

        self.finance_page = QWidget()
        main_layout = QVBoxLayout(self.finance_page)

        # ScrollArea setup
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #eee;
                width: 10px;
                margin: 4px 0 4px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #999;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("گزارشات مالی فروشگاه", self)
        title_label= QHBoxLayout()
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        title_label.addWidget(self.label)


        ##
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        ##
        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)

        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(1)
        top_layout.addLayout(title_label) 
        

        # لایه جعبه‌ها
        self.box_layout = QGridLayout()
        self.box_layout.setSpacing(20)
        scroll_layout.addLayout(self.box_layout)
        scroll_layout.addStretch()

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(50)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_layout.addWidget(scroll_area)

        self.setStyleSheet("background-color: #D9D9D9;")
        ### buttons:
        self.sell_reports= QToolButton()
        self.buy_reports= QToolButton()
        self.harvest_reports= QToolButton()
        self.barrow_reports= QToolButton()
        self.item_reports= QToolButton()

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
        ##
        self.stack.addWidget(self.finance_page)

    
    def label_UI(self):
        self.label.setMinimumSize(200, 40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;
        ''')

   ##
    def button_UI(self):
        ##
        self.sell_reports.clicked.connect(self.page_sell)
        self.buy_reports.clicked.connect(self.page_buy)
        self.harvest_reports.clicked.connect(self.page_harvest)
        self.barrow_reports.clicked.connect(self.page_barrow)
        # آیکون و متن‌ها
        buttons_info = [
            (self.sell_reports, "sale-report_11357276.png", "گزارش فروش"),
            (self.buy_reports, "shopping-analytics_18086140.png", "گزارش خرید"),
            (self.harvest_reports, "clipboard_8915058.png", "گزارش برداشت ها"),
            (self.barrow_reports, "report_18765735.png", "گزارش قرض ها"),
            (self.item_reports, "clipboard_6932327.png", "گزارش محصولات")
        ]

        buttons = []
        for btn, icon_file, text in buttons_info:
            icon = QIcon(self.get_asset_path(icon_file))
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(90, 90))  # بزرگ‌تر شد
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumSize(160, 160)
            btn.setMaximumSize(200, 200)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet('''
                QToolButton {
                    background-color: #ffffff;
                    border: 1px solid #dcdcdc;
                    border-radius: 16px;
                    padding: 15px;
                    font-family: B Nazanin;
                    font-size: 18px;
                    font-weight: bold;
                    color: #333333;
                }
                QToolButton:hover {
                    background-color: #f2f2f2;
                }
                QToolButton:pressed {
                    background-color: white;
                }
            ''')
            buttons.append(btn)

        # اضافه کردن دکمه‌ها به `QGridLayout` به صورت سطری - ستونی
        max_per_row = 4
        for i, btn in enumerate(buttons):
            row = i // max_per_row
            col = i % max_per_row
            self.box_layout.addWidget(btn, row, col)
    ##
    def set_today_date(self):
        today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_label.setText(f"تاریخ: {today_jalali}")
        self.date_label.setMinimumHeight(30)
        self.date_label.setMaximumHeight(70)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_label.setStyleSheet('''
            font-size: 18px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
            margin-left:20px
        ''')
    ##
    def set_today_time(self):
        weekdays_fa = {
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌ شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج ‌شنبه',
            'Friday': 'جمعه',
        }
        weekday_en = jdatetime.date.today().togregorian().strftime("%A")
        weekday_fa = weekdays_fa.get(weekday_en, 'نامشخص')

        self.time_label.setText(f"امروز: {weekday_fa}")
        self.time_label.setMinimumHeight(30)
        self.time_label.setMaximumHeight(50)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.time_label.setStyleSheet('''
            font-size: 16px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-left:30px;
        ''')
    
    ##
    def page_sell(self):
        from sell_reports import SalesDashboard
        self.sell_page= SalesDashboard()
        self.stack.addWidget(self.sell_page)
        
        ## out of page
        self.sell_page.move(self.stack.width(),0)
        self.stack.setCurrentWidget(self.sell_page)
        ##
        self.animate= QPropertyAnimation(self.sell_page, b'pos',self)
        self.animate.setDuration(700)
        self.animate.setStartValue(QPoint(self.stack.width(),0))
        self.animate.setEndValue(QPoint(0,0))
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##
    ##
    def page_buy(self):
        from buy_reports import BuyDashboard
        self.buy_page= BuyDashboard()
        self.stack.addWidget(self.buy_page)
        
        ## out of page
        self.buy_page.move(self.stack.width(),0)
        self.stack.setCurrentWidget(self.buy_page)
        ##
        self.animate= QPropertyAnimation(self.buy_page, b'pos',self)
        self.animate.setDuration(700)
        self.animate.setStartValue(QPoint(self.stack.width(),0))
        self.animate.setEndValue(QPoint(0,0))
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##
    def page_harvest(self):
        from harvest import Harvest
        self.harvetst_page= Harvest()
        self.stack.addWidget(self.harvetst_page)
        
        ## out of page
        self.harvetst_page.move(self.stack.width(),0)
        self.stack.setCurrentWidget(self.harvetst_page)
        ##
        self.animate= QPropertyAnimation(self.harvetst_page, b'pos',self)
        self.animate.setDuration(700)
        self.animate.setStartValue(QPoint(self.stack.width(),0))
        self.animate.setEndValue(QPoint(0,0))
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##
    def page_barrow(self):
        from barrow import Barrow
        self.barrow_page= Barrow()
        self.stack.addWidget(self.barrow_page)
        
        ## out of page
        self.barrow_page.move(self.stack.width(),0)
        self.stack.setCurrentWidget(self.barrow_page)
        ##
        self.animate= QPropertyAnimation(self.barrow_page, b'pos',self)
        self.animate.setDuration(700)
        self.animate.setStartValue(QPoint(self.stack.width(),0))
        self.animate.setEndValue(QPoint(0,0))
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##images
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
    
    
    