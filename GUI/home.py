from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QTableWidgetItem,QGridLayout,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont
from PyQt6 import QtCore
import jdatetime
import sqlite3
import pymysql
import requests
import threading
import datetime
from message_b import MessageBox
from switch import ToggleSwitch
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
        self.auto_synced()
        self.set_factor_number()
        self.added_products = []  # هر آیتم: دیکشنری حاوی اطلاعات محصول
        self.load_today_invoices()




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
        ##
        table_layout = QVBoxLayout(table_frame)
        ##
        self.table_title = QLabel("بل فروشات")
        self.table_title.setAlignment( Qt.AlignmentFlag.AlignHCenter)
        ##
        self.date_layout= QHBoxLayout()
        self.date = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_lb= QLabel(f"تاریخ: {self.date}")
        self.date_layout.addWidget(self.date_lb)
        self.date_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        ##
        self.factor_layout= QHBoxLayout()
        self.factor_lb= QLabel("نمبر فاکتور:")
        self.factor_number= QLabel("0")
        self.factor_lb.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.factor_number.setAlignment(Qt.AlignmentFlag.AlignRight)
        ##
        self.factor_layout.addLayout(self.date_layout)
        self.factor_layout.addStretch(1)
        self.factor_layout.addWidget(self.table_title)
        self.factor_layout.addWidget(self.factor_number)
        self.factor_layout.addWidget(self.factor_lb)
        
        
        ##
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["نام محصول", "قیمت","تعداد", "واحد", "تخفیف","قیمت کل"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setVisible(False)  # عدم نمایش شماره ردیف
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)  # اضافه برای نمایش خط‌ها

        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;  /* گوشه‌ها صاف */
                gridline-color: black;
                text-align: center;
            }
            QHeaderView::section {
                background-color: transparent;
                border: 1px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;  /* صاف کردن سرستون‌ها */
            }
        """)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        
        #table_layout.addWidget(self.table_title)
        table_layout.addLayout(self.factor_layout)
        table_layout.addWidget(self.table)


        table_layout.addWidget(self.table_title)
        table_layout.addWidget(self.table)

        # فرم فروش
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        ##inputs
        self.form_layout = QVBoxLayout(form_frame)
        self.title_layout= QHBoxLayout()
        
        ##
        self.radio_layout= QHBoxLayout()
        self.radio_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        
        self.switch= ToggleSwitch()
        self.switch.setChecked(False)
        #self.switch.setFixedSize(55,30)
        self.switch.clicked = lambda: print("ON") if self.switch.isChecked() else print("OFF")
        self.radio_layout.addWidget(self.switch)
       
        ##
        self.lb_layout= QHBoxLayout()
        self.form_title = QLabel("فرم فروشات")
        self.form_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.barcode_input= QLineEdit()
        self.barcode_input.setPlaceholderText("بارکد محصول")
        self.barcode_input.textChanged.connect(self.auto_search)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام محصول")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("تعداد")
        self.qty_input.textChanged.connect(self.update_total_price)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("قیمت")
        self.unit_price_input.textChanged.connect(self.update_total_price)

        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("تخفیف")
        self.discount_input.textChanged.connect(self.update_total_price)


        self.total_price_input = QLineEdit()
        self.total_price_input.setPlaceholderText("قیمت کل")
        self.total_price_input.setReadOnly(True)

        self.add_button = QPushButton("اضافه کردن")
        self.add_button.setStyleSheet("background-color: #2A64C5; color: white; padding: 10px; border-radius: 6px;")
        self.add_button.clicked.connect(self.add_product)
        ##
        
        self.title_layout.addLayout(self.radio_layout)
        self.title_layout.addStretch(1)
        self.title_layout.addWidget(self.form_title)
        self.title_layout.addStretch(2)
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
    
        self.invoice_list = QListWidget()
        self.invoice_list.itemClicked.connect(self.load_invoice)
        self.invoice_list.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        bottom_layout.addLayout(label_layout)
        bottom_layout.addWidget(self.invoice_list)
        main_layout.addWidget(bottom_frame,1)


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
        for input in (self.barcode_input, self.name_input,self.unit_price_input,self.qty_input,self.discount_input, self.total_price_input):
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
        self.factor_lb.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        ##
        self.factor_number.setFixedHeight(20)
        self.factor_number.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: Arial;
        ''')
        ##
        self.date_lb.setFixedHeight(28)
        self.date_lb.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        self.invoice_list.itemClicked.connect(self.load_invoice)

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
        self.add_button.setStyleSheet('''
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
    def auto_synced(self):
        self.synced_timer= QTimer(self)
        self.synced_timer.timeout.connect(self.start_synce_thread)
        self.synced_timer.start( 10 * 1000)

    def start_synce_thread(self):
        synced_thread= threading.Thread(target=self.synced_to_server_to_sale)
        synced_thread.setDaemon(True)
        synced_thread.start()
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
    def set_factor_number(self):
        if hasattr(self, "factor_value") and self.factor_value:
            # اگر قبلاً مقدار گرفته شده، دوباره نگیر
            return

        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT sale_id FROM factor_number ORDER BY sale_id DESC LIMIT 1')
            result = cursor.fetchone()
            factor = result[0] if result else 0
            factor += 1

            self.factor_number.setText(f"{factor}")
            self.factor_value = factor  # فقط یک بار در هر فاکتور
            conn.close()
        except sqlite3.Error as e:
            print(f"{e}: خطا در بارگذاری نمبر فاکتور")
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
    
    ##search_action:
    def search_barcode(self):
        barcode= self.barcode_input.text().strip()
        is_switch_on = self.switch.isChecked()
        if not barcode:
            MessageBox("لطفاً بارکد محصول را وارد کنید",title="یادآوری",type="warning").show()
        conn_sq=None
        cursor_sq= None

        # خواندن شناسه کاربر از دیتابیس محلی
        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        try:
            if is_switch_on:
                ##
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute('''
                select name,big_price,barcode
                From products WHERE  barcode=?''',(barcode,))
                result= cursor_sq.fetchone()
            else:
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute('''
                select name,sale_price,barcode
                From products WHERE  barcode=?''',(barcode,))
                result= cursor_sq.fetchone()
            
            if result:
                    self.name_input.clear()
                    self.name_input.insert(str(result[0]))
                    print(f"{result[0]}: name")
                    ##
                    self.unit_price_input.clear()
                    self.unit_price_input.insert(str(result[1]))
                    ##
                    self.barocde= str(result[2])

    
        except pymysql.Error as e:
            MessageBox(f"{e}: خطا در دیتابیس",type="error",title="خطا").show()
    ##
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.barcode_input.hasFocus():
                self.search_barcode()
            elif any(line.hasFocus() for line in [
                self.qty_input,self.unit_price_input, self.discount_input,self.name_input
            ]):
                self.add_product()
    ##
    def auto_search(self):
        text= self.barcode_input.text().strip()
        if text:
            self.search_barcode()
    ##
    def add_product(self):
        barcode = self.barcode_input.text().strip()
        name = self.name_input.text().strip()
        qty = self.qty_input.text()
        unit_price = self.unit_price_input.text()
        discount = self.discount_input.text()
        total_price = self.total_price_input.text()
        is_switch_on = self.switch.isChecked()

        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        if barcode and name and qty and unit_price and total_price:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT big_category, big_sub, big_quantity FROM products WHERE barcode = ?", (barcode,))
                product_info = cursor.fetchone()
                if not product_info:
                    MessageBox("محصول یافت نشد!", title="خطا", type="error").show()
                    return

                big_category, big_sub, big_quantity = product_info

                unit_price = float(unit_price or 0)
                qty = float(qty or 0)
                discount = float(discount or 0)

                if is_switch_on:
                    s_type = big_category
                    quantity = big_sub if big_sub == big_quantity else qty
                    sale_type = "عمده"
                else:
                    s_type = 'عدد'
                    quantity = qty
                    sale_type = "پرچون"

                # درج در جدول نمایشی
                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, self._make_cell(name))
                self.table.setItem(row, 1, self._make_cell(str(unit_price)))
                self.table.setItem(row, 2, self._make_cell(str(quantity)))
                self.table.setItem(row, 3, self._make_cell(s_type))
                self.table.setItem(row, 4, self._make_cell(str(discount)))
                self.table.setItem(row, 5, self._make_cell(total_price))

                # ذخیره در لیست حافظه‌ای
                self.added_products.append({
                    "barcode": barcode,
                    "name": name,
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "s_type": s_type,
                    "sale_type": sale_type,
                    "discount": discount,
                    "total": float(total_price),
                })

                # پاک‌سازی فیلدها
                self.barcode_input.clear()
                self.name_input.clear()
                self.qty_input.clear()
                self.unit_price_input.clear()
                self.discount_input.clear()
                self.total_price_input.clear()
                self.switch.setChecked(False)

            except sqlite3.Error as e:
                MessageBox(text=f"{e}: خطا در دیتابیس", title="ناموفق", type="error").show()
            finally:
                conn.close()

    def _make_cell(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.black)
        return item


    ##
    def update_total_price(self):
        try:
            qty = float(self.qty_input.text())
            unit_price = float(self.unit_price_input.text())

            # اگر تخفیف وارد نشده بود یا خالی بود، مقدار آن را 0 در نظر بگیر
            discount_text = self.discount_input.text()
            discount = float(discount_text) if discount_text.strip() else 0.0

            total = qty * unit_price
            final_total = total - discount
            self.total_price_input.setText(str(round(final_total, 2)))
        except ValueError:
            self.total_price_input.clear()

    ##
    def print_invoice(self):
        items = []
        for row in range(self.table.rowCount()):
            names = self.table.item(row, 0).text()
            price = self.table.item(row, 1).text()
            number = self.table.item(row, 2).text()
            unit = self.table.item(row, 3).text()
            discount = self.table.item(row, 4).text()
            total = self.table.item(row, 5).text()
            items.append((names, price, number, unit, discount, total))

        if not self.added_products:
            MessageBox("هیچ محصولی به فاکتور اضافه نشده است", title="خطا", type="warning").show()
            return

        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        barcode = self.barocde
        factor_number = self.factor_value
        date = datetime.date.today().strftime("%Y/%m/%d")
        date_ent = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

        invoice_key = f"فاکتور {factor_number}"
        self.invoices[invoice_key] = items

        # حذف آیتم تکراری از لیست فاکتورها (در صورت وجود)
        for i in range(self.invoice_list.count()):
            if self.invoice_list.item(i).text() == invoice_key:
                self.invoice_list.takeItem(i)
                break

        self.invoice_list.addItem(invoice_key)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users;")
            res_id = cursor.fetchone()
            id_user = res_id[0] if res_id else None

            for product in self.added_products:
                barcode = product['barcode']
                name = product['name']
                unit_price = product['unit_price']
                quantity = product['quantity']
                s_type = product['s_type']
                sale_type = product['sale_type']
                discount_val = product['discount']
                final_total = product['total']

                cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
                product_quantity_row = cursor.fetchone()
                product_quantity = product_quantity_row[0] if product_quantity_row else 0

                if float(quantity) > product_quantity:
                    MessageBox(f"موجودی محصول {name} کافی نیست", title="ناموفق", type="warning").show()
                    continue

                cursor.execute('''
                    INSERT INTO sale_factor (barcode, product_name, factor_number, sale_price, sale_date, quantity,
                        product_type, sale_type, discount, total, created_at, user_id, is_synced)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    barcode, name, factor_number, unit_price, date, quantity, s_type, sale_type,
                    discount_val, final_total, date_ent, id_user, 0
                ))

            cursor.execute("INSERT INTO factor_number(sale_id) VALUES (?)", (factor_number,))
            conn.commit()

            # 🎯 نمایش و ذخیره فاکتورهای امروز در self.invoices
            cursor.execute("""
                SELECT factor_number FROM sale_factor
                WHERE sale_date = ?
                GROUP BY factor_number
                ORDER BY factor_number DESC
            """, (date,))
            today_factors = cursor.fetchall()

            for f in today_factors:
                factor_num = f[0]
                invoice_key = f"فاکتور {factor_num}"

                cursor.execute("""
                    SELECT product_name, sale_price, quantity, product_type, discount, total
                    FROM sale_factor
                    WHERE factor_number = ?
                """, (factor_num,))
                rows = cursor.fetchall()

                self.invoices[invoice_key] = rows

                # از افزودن دوباره آیتم جلوگیری کن
                duplicate = False
                for i in range(self.invoice_list.count()):
                    if self.invoice_list.item(i).text() == invoice_key:
                        duplicate = True
                        break
                if not duplicate:
                    self.invoice_list.addItem(invoice_key)


            conn.close()

            self.factor_value = None
            self.set_factor_number()
            self.factor_number.setText(f"{self.factor_value}")
            self.added_products.clear()
            self.table.setRowCount(0)

        except sqlite3.Error as e:
            print(f"{e}: خطا در پایگاه داده")
            MessageBox(f"خطا در پایگاه داده: {e}", title="❌ خطا", type="error").show()
        finally:
            if conn:
                conn.close()


        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()

            total_sum = sum(float(item[5]) for item in items if item[5])

            html = f"""
            <html>
            <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'B Nazanin', Mirza;
                    direction: rtl;
                    background-color: white;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    text-align: center;
                }}
                table {{
                    width: 80%;
                    margin: 0 auto;
                    border-collapse: collapse;
                    font-size: 16pt;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 12px;
                    text-align: center;
                }}
                h2 {{
                    font-size: 22pt;
                    margin-bottom: 20px;
                }}
            </style>
            </head>
            <body>
            <div class="container">
                <h3>فاکتور فروش</h3>
                <table>
                    <tr>
                        <td colspan="7">
                            <b>شماره فاکتور</b> {self.factor_value}
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            <b>تاریخ</b> {self.date}
                        </td>
                    </tr>
                    <tr>
                        <th>مجموعه</th>
                        <th>تخفیف</th>
                        <th>واحد</th>
                        <th>تعداد</th>
                        <th>قیمت</th>
                        <th>نام</th>
                        <th>شماره</th>
                    </tr>
            """

            for i, (names, price, number, unit, discount, total) in enumerate(items, 1):
                html += f"""
                    <tr>
                        <td>{total}</td>
                        <td>{discount}</td>
                        <td>{unit}</td>
                        <td>{number}</td>
                        <td>{price}</td>
                        <td>{names}</td>
                        <td>{i}</td>
                    </tr>
                """

            html += f"""
                    <tr>
                        <td colspan="7"> {total_sum} <b>:مجموع کل</b> </td>
                    </tr>
                </table>
            </div>
            </body>
            </html>
            """

            doc.setHtml(html)
            doc.print(printer)

        self.table.setRowCount(0)
        self.table.setShowGrid(False)
    ##
    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data
        except Exception as e:
            print("خطا در دریافت config:", e)
            return None
    ##
    def synced_to_server_to_sale(self):
        db_connect = self.get_db_config()
        if not db_connect:
            return

        conn_sq = sqlite3.connect("D:\\projects\\sh_online\\Data\\sh_online.db")
        cursor_sq = conn_sq.cursor()

        cursor_sq.execute('''
            SELECT product_name, factor_number, barcode,
                sale_date, sale_price, quantity, product_type,
                sale_type, discount, total, user_id, created_at
            FROM sale_factor WHERE is_synced = 0
        ''')

        unsynced_products = cursor_sq.fetchall()

        try:
            conn = pymysql.connect(
                host=db_connect["host"],
                user=db_connect["user"],
                password=db_connect["password"],
                database=db_connect["database"]
            )
            cursor = conn.cursor()

            for product in unsynced_products:
                (product_name, factor_number, barcode, sale_date, sale_price,
                quantity, product_type, sale_type, discount, total, user_id, created_at) = product


                cursor.execute('''
                        INSERT INTO sale_factor(product_name, barcode, factor_number, sale_date, sale_price,
                            quantity, product_type, sale_type, discount, total, user_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        product_name, barcode, factor_number, sale_date, sale_price,
                        quantity, product_type, sale_type, discount, total, user_id, created_at
                    ))
                print(f"✅ محصول {barcode} افزوده شد")
                ## update products
                cursor_sq.execute("UPDATE products SET is_synced=0 where barcode=?",(barcode,))


            conn.commit()
            #print("✅ اطلاعات با موفقیت به فروش رسید")

            cursor_sq.execute("UPDATE sale_factor SET is_synced = 1 WHERE is_synced = 0")
            conn_sq.commit()

        except Exception as e:
            print("❌ خطا در همگام‌سازی:", e)

        finally:
            conn_sq.close()
            if conn:
                conn.close()
   ##
    def load_invoice(self, item):
        invoice_name = item.text()

        if invoice_name in self.invoices:
            self.table.setRowCount(0)  # حذف همه ردیف‌های قبلی
            self.table.setShowGrid(True)

            for name, price, number, unit, discount, total in self.invoices[invoice_name]:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(str(price)))
                self.table.setItem(row, 2, QTableWidgetItem(str(number)))
                self.table.setItem(row, 3, QTableWidgetItem(str(unit)))
                self.table.setItem(row, 4, QTableWidgetItem(str(discount)))
                self.table.setItem(row, 5, QTableWidgetItem(str(total)))
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
    def load_today_invoices(self):
        self.invoice_list.clear()  # پاک‌سازی لیست فاکتورها

        db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            today = datetime.date.today().strftime("%Y/%m/%d")

            cursor.execute("""
                SELECT DISTINCT factor_number FROM sale_factor
                WHERE sale_date = ?
                ORDER BY factor_number DESC
            """, (today,))
            today_factors = cursor.fetchall()

            for f in today_factors:
                invoice_key = f"فاکتور {f[0]}"
                self.invoice_list.addItem(invoice_key)

            conn.close()

        except sqlite3.Error as e:
            print(f"{e}: خطا در پایگاه داده")
            MessageBox(f"خطا در پایگاه داده: {e}", title="❌ خطا", type="error").show()

    ##
