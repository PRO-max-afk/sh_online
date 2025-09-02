from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout,QPushButton,
    QGraphicsDropShadowEffect, QFileDialog,QStyledItemDelegate,QSizePolicy,QAbstractItemView,QWidget,QComboBox,QTableWidgetItem,QTableWidget,QHeaderView)
from PyQt6.QtGui import QPalette,QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QSize,QPoint,QPropertyAnimation,QEasingCurve,QTimer
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os,sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
from item_thread import ItemThread
from circle import CircularSpinner
from notifi_box import Notification
from spitial_calendar import JalaliCalendar
class CutomerBarrow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._anim = None  # نگهداری رفرنس انیمیشن

        self.IN_UI()
        self.Button_UI()
        self.Label_UI()
        self.table_UI()
        self.row_data()
        self.load_all_fonts()

    def IN_UI(self):
        self.customer = QStackedWidget()
        self.setCentralWidget(self.customer)

        self.customer_page = QWidget()
        self.main_layout = QVBoxLayout(self.customer_page)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # نوار بالا
        self.top_layout = QHBoxLayout()
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cutomer_label = QLabel()

        self.title_layout = QHBoxLayout()
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.title_layout.addWidget(self.cutomer_label)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.back_btn = QPushButton()
        self.btn_layout.addWidget(self.back_btn)

        self.top_layout.addLayout(self.btn_layout)
        self.top_layout.addStretch()
        self.top_layout.addLayout(self.title_layout)

        # بدنه میانی
        self.middle_layout = QHBoxLayout()

        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        self.table_layout = QVBoxLayout(table_frame)
        self.top_frame= QHBoxLayout()
        ##
        self.title_lb= QLabel()
        self.select_barrow= QComboBox()
        ##
        self.top_frame.addWidget(self.select_barrow)
        self.top_frame.addWidget(self.title_lb)
        self.top_frame.setAlignment(Qt.AlignmentFlag.AlignRight)
        ##
        self.table_layout.addLayout(self.top_frame)


        # ⚠️ جدول را با والد مناسب بساز
        self.table = QTableWidget(0, 5, table_frame)
        self.table_layout.addWidget(self.table)
        self.table_layout.setContentsMargins(50,50,50,50)

        # چینش‌ها
        self.main_layout.addLayout(self.top_layout)
        self.middle_layout.addWidget(table_frame)  # به جای addLayout، خود ویجت فریم را اضافه کن
        self.main_layout.addLayout(self.middle_layout)  # ⚠️ قبلاً فراموش شده بود

        self.customer.addWidget(self.customer_page)
        self.customer.setCurrentWidget(self.customer_page)

    def Button_UI(self):
        icon_path = self.get_asset_path("left.png")
        if icon_path:
            back_icon = QIcon(icon_path)
            self.back_btn.setIcon(back_icon)
            self.back_btn.setIconSize(QSize(50, 50))
        self.back_btn.clicked.connect(self.open_reports)
        self.back_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.back_btn.setStyleSheet("""
            QPushButton{
                background-color: transparent;
                border-radius: 27px;
                padding: 5px;
            }
            QPushButton:hover{
                background-color: rgba(0,0,0,0.04);
            }
        """)
        self.select_barrow.addItems(["همه","قرضدار ها","طلب کار ها"])
        self.select_barrow.setCurrentIndex(0)
        self.select_barrow.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.select_barrow.currentTextChanged.connect(self.filter_info)
        self.select_barrow.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 15px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px; /* فضای کافی برای فلش در سمت چپ */
                padding-left: 40px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: white;  /* پس‌زمینه سفید */
                color: black;             /* متن سیاه */
                text-align: left;        /* تراز متن به راست */
                font-family: "B Nazanin";
                font-size: 15px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;  /* رنگ انتخاب آیتم */
            }

        ''')

    def Label_UI(self):
        self.cutomer_label.setText("گزارش قرض مشتریان")
        self.cutomer_label.setMaximumSize(150, 50)
        self.cutomer_label.setMinimumSize(90, 40)
        self.cutomer_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.cutomer_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;
        """)
        self.title_lb.setText("لیست قرضدار ها")
        self.title_lb.setMaximumSize(150, 50)
        self.title_lb.setMinimumSize(90, 40)
        self.title_lb.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.title_lb.setStyleSheet("""
            font-size: 17px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        """)

    def table_UI(self):
        self.table.setHorizontalHeaderLabels(["نام", "شماره تماس", "تاریخ", "وضعیت","مقدار"])
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 🔹 انتخاب را غیرفعال کن (هیچ رنگی تغییر نکند)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.table.setAlternatingRowColors(True)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # اندازه ستون‌ها
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # استایل‌دهی
        self.table.setStyleSheet("""
            QTableWidget {
                border:None;
                font-family: Roboto,'B Nazanin';
                font-size: 14px;
                color: black;
                border-radius: 12px;
                gridline-color: transparent; /* حذف خطوط داخلی */
                alternate-background-color: #f5f5f5; /* رنگ ردیف‌های زوج */
                background-color: #ffffff;          /* رنگ ردیف‌های فرد */
            }
            QTableWidget::item {
                border: none;      
                padding: 8px;      
            }
            QTableWidget::item:selected {
                background: transparent;  /* حذف رنگ انتخاب */
                color: black;
            }
            QHeaderView::section {
                background-color: #7E22CE; 
                color: white;
                font-family: 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                border: none;  
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px; 
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;  
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
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
        """)

        
    def row_data(self):
        self.table.setRowCount(0)
        self.table.setShowGrid(True)
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data','sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db")
            return
        try:
            conn=sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute('''
                Select name,phone,date,amount,type from barrow where type in('طلب مردم','برده گی')
            ''')
            result= cursor.fetchall()
            if result:
                for name,phone,date,amount,types in result:
                    if amount == 0:
                        types = "صفر"
                    elif types == "برده گی":
                        types = "قرضدار"
                    else:
                        types = "طلب کار"

                    row= self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(name))
                    self.table.setItem(row,1, QTableWidgetItem(str(phone)))
                    self.table.setItem(row,2, QTableWidgetItem(self._make_cell(date)))
                    self.table.setItem(row,3, QTableWidgetItem(self._make_cell(types)))
                    self.table.setItem(row,4, QTableWidgetItem(self._make_cell(str(amount))))
        except sqlite3.Error as e:
            print(f"db proble:{e}")
    ##
    def filter_info(self):
        filter_type= self.select_barrow.currentText()
        self.table.setRowCount(0)
        self.table.setShowGrid(True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no offline db")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            # شرط فیلتر
            if filter_type == "همه":
                cursor.execute('''
                    SELECT name, phone, date, amount, type 
                    FROM barrow 
                    WHERE type IN ('طلب مردم','برده گی')
                ''')
            elif filter_type == "طلب کار ها":
                cursor.execute('''
                    SELECT name, phone, date, amount, type 
                    FROM barrow 
                    WHERE type = 'طلب مردم'
                ''')
            elif filter_type == "قرضدار ها":
                cursor.execute('''
                    SELECT name, phone, date, amount, type 
                    FROM barrow 
                    WHERE type = 'برده گی'
                ''')

            result = cursor.fetchall()
            if result:
                for name, phone, date, amount, types in result:
                    if amount == 0:
                        types = "صفر"
                    elif types == "برده گی":
                        types = "قرضدار"
                    else:
                        types = "طلب کار"


                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(name))
                    self.table.setItem(row, 1, QTableWidgetItem(str(phone)))
                    self.table.setItem(row, 2, QTableWidgetItem(self._make_cell(date)))
                    self.table.setItem(row, 3, QTableWidgetItem(self._make_cell(types)))
                    self.table.setItem(row, 4, QTableWidgetItem(self._make_cell(str(amount))))
        except sqlite3.Error as e:
            print(f"db select info:{e}")

            
    ##
    def _make_cell(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.black)
        return item

    def open_reports(self):
        from finance import Money
        self.finace = Money()
        self.customer.addWidget(self.finace)
        self.customer.setCurrentWidget(self.finace)
        self.finace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        # انیمیشن: رفرنس را نگه دار تا GC نشود
        start_pos = QPoint(-self.width(), 0)
        end_pos = QPoint(0, 0)
        self.finace.move(start_pos)
        self._anim = QPropertyAnimation(self.finace, b'pos', self)
        self._anim.setDuration(700)
        self._anim.setStartValue(start_pos)
        self._anim.setEndValue(end_pos)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()

    # ===== ابزارها =====
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None

    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")
        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return
        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf", ".ttc")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")