from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QTableWidgetItem,QGridLayout,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread, pyqtSignal
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont
from PyQt6 import QtCore
import jdatetime
import os
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from notification import Frame2
from dasboard import Dashboard
from order import Orders
from finance import Money
from inventory import Inventory
from settings import Settings

class WidgetManager(QFrame):
    def __init__(self, parent):
        super().__init__(parent)  # ✅ درستش اینه
        self.parent = parent
        self.stack = QStackedWidget(parent)
        self.frames = {}

        self.frame2 = None
        self.das_frame = None
        self.frame_order = None
        self.finance_frame = None
        self.inventory_frame = None
        self.settings_frame = None

        self.create_frame1()
        self.invoice_counter = 1
        self.invoices = {}

        self.label_ui()
        self.set_today_date()
        self.set_today_time()
        self.Button_ui()
        self.Entries_ui()


    def create_frame1(self):
        frame1 = QFrame()
        frame1.setStyleSheet("background-color: #D9D9D9;")
        ##
        main_layout = QVBoxLayout(frame1)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("فروش محصولات", self)
        self.search_line = QLineEdit(self)
        self.serach_btn = QPushButton("جستجو", self)

        ##
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.search_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.serach_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        ##
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
        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
        ##
        # میانی: جدول و فرم
        middle_layout = QHBoxLayout()

        # جدول فروش
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        table_layout = QVBoxLayout(table_frame)

        self.table_title = QLabel("بل فروشات")
        self.table_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["بارکد محصول", "نام محصول", "قیمت واحد", "قیمت کل"])
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { border: 2px solid black; color: black; font-family: B Nazanin; font-size: 14px; font-weight: bold; } QHeaderView::section { background-color: transparent; border: 1px solid gray; color: black; border-radius: 9px; font-family: B Nazanin; font-size: 16px; font-weight: bold;  }")
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        table_layout.addWidget(self.table_title)
        table_layout.addWidget(self.table)

        # فرم فروش
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        ##inputs
        self.form_layout = QVBoxLayout(form_frame)
        self.title_layout= QHBoxLayout()
        

        self.form_title = QLabel("فرم فروشات")
        self.form_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.barcode_input= QLineEdit()
        self.barcode_input.setPlaceholderText("بارکد محصول")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام محصول")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("مقدار")
        self.qty_input.textChanged.connect(self.update_total_price)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("قیمت واحد")
        self.unit_price_input.textChanged.connect(self.update_total_price)

        self.total_price_input = QLineEdit()
        self.total_price_input.setPlaceholderText("قیمت کل")
        self.total_price_input.setReadOnly(True)

        self.add_button = QPushButton("اضافه کردن")
        self.add_button.setStyleSheet("background-color: #2A64C5; color: white; padding: 10px; border-radius: 6px;")
        self.add_button.clicked.connect(self.add_product)
        ##
        self.title_layout.addWidget(self.form_title)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.addLayout(self.title_layout)
        ##
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
        self.faktur_label = QLabel("فاکتورها")


        self.print_button = QPushButton()
        self.print_button.clicked.connect(self.print_invoice)
        ##
        label_layout.addWidget(self.print_button)
        label_layout.addStretch()
        label_layout.addWidget(self.faktur_label)
        ###
        
        ###
        

        self.invoice_list = QListWidget()
        self.invoice_list.itemClicked.connect(self.load_invoice)
        self.invoice_list.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        bottom_layout.addLayout(label_layout)
        bottom_layout.addWidget(self.invoice_list)

        main_layout.addWidget(bottom_frame,2)


        self.frames["frame1"] = frame1
        self.stack.addWidget(frame1)
    ##
    def Entries_ui(self):
        self.search_line.setMinimumHeight(60)
        self.search_line.setMaximumHeight(70)
        self.search_line.setMaximumWidth(700)
        self.search_line.setAlignment(Qt.AlignmentFlag.AlignLeft)
        #self.search_line.textChanged.connect(self.show_spinner_and_load_dataes)
        self.search_line.setPlaceholderText("جستجو محصولات...")
        self.search_line.setStyleSheet('''
            font-size: 17px;
            color: black;
            font-family: B Nazanin;
            font-weight: bold;
            background-color: white;
            border: 5px solid transparent;
            border-radius: 30px;
            padding: 5px;
            margin-right: 50px;
        ''')
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.search_line.setGraphicsEffect(shadow)
        ##
        for input in (self.barcode_input, self.name_input, self.qty_input,self.unit_price_input, self.total_price_input):
            self.form_layout.addWidget(input)
            input.setFixedHeight(40)
            
            if input == self.barcode_input:
                font_family = 'Arial'
            else:
                font_family = '"B Nazanin", Mirza'  # در صورت عدم موجود بودن فونت اول، Arial استفاده می‌شود
            
            input.setStyleSheet(f'''
                color: black;
                font-family: {font_family};
                font-weight: bold;
                font-size: 16px;
                border: 2px solid black;
                padding: 5px;
                border-radius: 5px;
            ''')

        self.form_layout.addWidget(self.add_button)

    ##
    def label_ui(self):
        self.label.setMinimumSize(200, 40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        self.form_title.setFixedHeight(30)  # یا setMaximumHeight
        self.form_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.form_title.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.faktur_label.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
    ''')
        ##
        self.invoice_list.setStyleSheet('''
        color: black;
        font-family: B Nazanin;
        font-weight: bold;
        font-size: 14px;
        padding: 5px;
                                        
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

    ''')
        ##
        self.table_title.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')

    ##
    def Button_ui(self):
        self.serach_btn.setMinimumSize(100, 30)
        self.serach_btn.setMaximumSize(140, 40)
        #self.serach_btn.clicked.connect(self.show_spinner_and_load_dataes)
        self.serach_btn.setStyleSheet('''
            QPushButton {
                background-color: #2251DB;
                font-family: "B Nazanin";
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
        ##
        printer_icon= QIcon(self.get_asset_path("print_7848732.png"))
        self.print_button.setIcon(printer_icon)
        self.print_button.setIconSize(QtCore.QSize(35,35))
        self.print_button.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 2px solid black;
                padding: 5px;

            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')    
      
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
    def add_product(self):
        barcode = self.barcode_input.text().strip()
        name = self.name_input.text().strip()
        qty = self.qty_input.text().strip()
        unit_price = self.unit_price_input.text().strip()
        total_price = self.total_price_input.text()

        if barcode and name and qty and unit_price and total_price:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # به ترتیب صحیح اضافه کن
            self.table.setItem(row, 0, QTableWidgetItem(str(barcode)))      # بارکد محصول
            self.table.setItem(row, 1, QTableWidgetItem(name))              # نام محصول
            self.table.setItem(row, 2, QTableWidgetItem(unit_price))        # قیمت واحد
            self.table.setItem(row, 3, QTableWidgetItem(total_price))       # قیمت کل

            for col in range(4):
                item = self.table.item(row, col)
                if item:
                    item.setForeground(Qt.GlobalColor.black)

            # پاکسازی فیلدها
            self.barcode_input.clear()
            self.name_input.clear()
            self.qty_input.clear()
            self.unit_price_input.clear()
            self.total_price_input.clear()


    def update_total_price(self):
        try:
            qty = float(self.qty_input.text())
            unit_price = float(self.unit_price_input.text())
            total = qty * unit_price
            self.total_price_input.setText(str(round(total, 2)))
        except ValueError:
            self.total_price_input.clear()

    def print_invoice(self):
        items = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 2).text()
            unit = self.table.item(row, 1).text()
            total = self.table.item(row, 0).text()
            items.append((name, unit, total))

        invoice_number = f"فاکتور {self.invoice_counter}"
        self.invoices[invoice_number] = items
        self.invoice_list.addItem(invoice_number)
        self.invoice_counter += 1

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            html = "<h2 align='center'>فاکتور فروش</h2><table border='1' width='100%' cellspacing='0' cellpadding='4'><tr><th>قیمت کل </th><th> واحد</th><th>نام محصول</th></tr>"
            for name, unit, total in items:
                html += f"<tr><td>{total}</td><td>{unit}</td><td>{name}</td></tr>"
            html += "</table>"
            doc.setHtml(html)
            doc.print(printer)
            self.table.clear()

    def load_invoice(self, item):
        invoice_name = item.text()
        if invoice_name in self.invoices:
            self.table.setRowCount(0)
            for name, unit, total in self.invoices[invoice_name]:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(total))
                self.table.setItem(row, 1, QTableWidgetItem(unit))
                self.table.setItem(row, 2, QTableWidgetItem(name))
    ##
    def get_stack(self):
        return self.stack

    def switch_frame(self, frame_name):
        if frame_name == "frame2":
            if not self.frame2:
                self.frame2 = Frame2()
                self.frames["frame2"] = self.frame2
                self.stack.addWidget(self.frame2)
        
        if frame_name == "dash_frame":
            if not self.das_frame:
                self.das_frame= Dashboard()
                self.frames["dash_frame"] = self.das_frame
                self.stack.addWidget(self.das_frame)

        if frame_name == "frame_order":
            if not self.frame_order:
                self.frame_order= Orders()
                self.frames["frame_order"] = self.frame_order
                self.stack.addWidget(self.frame_order)

        if frame_name == "finance_frame":
            if not self.finance_frame:
                self.finance_frame= Money()
                self.frames["finance_frame"] = self.finance_frame
                self.stack.addWidget(self.finance_frame)

        if frame_name == "inventory_frame":
            if not self.inventory_frame:
                self.inventory_frame= Inventory()
                self.frames["inventory_frame"] = self.inventory_frame
                self.stack.addWidget(self.inventory_frame)

        if frame_name == "settings_frame":
            if not self.settings_frame:
                self.settings_frame= Settings()
                self.frames["settings_frame"] = self.settings_frame
                self.stack.addWidget(self.settings_frame)

        if frame_name in self.frames:
            self.stack.setCurrentWidget(self.frames[frame_name])

    ##
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ##
