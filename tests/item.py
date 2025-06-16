from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread, pyqtSignal
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont
from PyQt6 import QtCore
import jdatetime


class WidgetManager(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.stack = QStackedWidget(parent)
        self.frames = {}
        self.frame2 = None  # در ابتدا فریم ۲ ایجاد نمی‌شود
        self.das_frame= None
        self.frame_order= None
        self.finance_frame= None
        self.inventory_frame= None
        self.settings_frame= None

        self.invoice_counter = 1
        self.invoices = {}
        ####
        self.setup_ui()
        self.label_ui()
        self.set_today_date()
        self.set_today_time()
        self.Button_ui()
        self.Entries_ui()
        

    ##UI
    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("فروش محصولات", self)
        self.search_line = QLineEdit(self)
        self.serach_btn = QPushButton("جستجو", self)


        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.search_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.serach_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.serach_btn)
        top_layout.addWidget(self.search_line, 3)
        top_layout.addWidget(self.label, 1)

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)


        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()

        # میانی: جدول و فرم
        middle_layout = QHBoxLayout()

        # جدول فروش
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        table_layout = QVBoxLayout(table_frame)

        table_title = QLabel("بل فروشات")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        table_title.setStyleSheet("color: black;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["اقلام فروخته شده","نمبر فاکتور","قیمت کل", "قیمت واحد", "نام محصول"])
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { border: 1px solid gray; color: black; } QHeaderView::section { background-color: transparent; border: 1px solid gray; color: black; border-radius: 7px; }")
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.table)

        # فرم فروش
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        form_layout = QVBoxLayout(form_frame)

        form_title = QLabel("فرم فروشات")
        form_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        form_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_title.setStyleSheet("color: black;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام محصول")
        self.name_input.setFixedHeight(35)
        self.name_input.setStyleSheet("color: black;")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("مقدار")
        self.qty_input.setFixedHeight(35)
        self.qty_input.setStyleSheet("color: black;")
        self.qty_input.textChanged.connect(self.update_total_price)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("قیمت واحد")
        self.unit_price_input.setFixedHeight(35)
        self.unit_price_input.setStyleSheet("color: black;")
        self.unit_price_input.textChanged.connect(self.update_total_price)

        self.total_price_input = QLineEdit()
        self.total_price_input.setPlaceholderText("قیمت کل")
        self.total_price_input.setFixedHeight(35)
        self.total_price_input.setStyleSheet("color: black;")
        self.total_price_input.setReadOnly(True)

        add_button = QPushButton("اضافه کردن")
        add_button.setStyleSheet("background-color: #2A64C5; color: white; padding: 10px; border-radius: 6px;")
        add_button.clicked.connect(self.add_product)

        form_layout.addWidget(form_title)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.unit_price_input)
        form_layout.addWidget(self.total_price_input)
        form_layout.addWidget(add_button)

        middle_layout.addWidget(table_frame, 2)
        middle_layout.addWidget(form_frame, 1)
        middle_layout.setSpacing(20)

        main_layout.addLayout(middle_layout,3)

        # پایین: فاکتورها
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        bottom_frame.setMinimumHeight(150)
        bottom_layout = QVBoxLayout(bottom_frame)

        label_layout = QHBoxLayout()
        faktur_label = QLabel("فاکتورها")
        faktur_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        faktur_label.setStyleSheet("color: black;")

        print_button = QPushButton("پرینت")
        print_button.setStyleSheet("background-color: #f2f2f2; padding: 8px 20px; border-radius: 6px; color: black;")
        print_button.clicked.connect(self.print_invoice)

        label_layout.addWidget(faktur_label)
        label_layout.addStretch()
        label_layout.addWidget(print_button)

        self.invoice_list = QListWidget()
        self.invoice_list.setStyleSheet("color: black;")
        self.invoice_list.itemClicked.connect(self.load_invoice)

        bottom_layout.addLayout(label_layout)
        bottom_layout.addWidget(self.invoice_list)

        main_layout.addWidget(bottom_frame,2)