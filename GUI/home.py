from PyQt6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
QSizePolicy,QCompleter,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QEvent,QSize
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QBrush
from PyQt6 import QtCore,QtGui,QtWidgets
import jdatetime
import sqlite3
import threading
import datetime
from message_b import MessageBox
from switch import ToggleSwitch
import os
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from notification import Frame2
from dasboard import Dashboard
from order import Orders
from finance import Money
from inventory import Inventory
from settings import Settings
from notifi_check import NotificationChecker
from notifi_box import Notification
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QColor, QPalette
from db_connection import Connection
from globals import shown_notifications
from functools import partial

class BlackTextDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor("black"))
        editor.setPalette(palette)
        return editor

class EditHighlightDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # وقتی آیتم انتخاب شده، هایلایت خاکستری + متن سیاه
        opt = QtWidgets.QStyleOptionViewItem(option)
        if opt.state & QtWidgets.QStyle.StateFlag.State_Selected:
            opt.palette.setColor(QPalette.ColorRole.Highlight, QColor("#d3d3d3"))
            opt.palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        super().paint(painter, opt, index)

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        pal = editor.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor("#d3d3d3"))  # پس‌زمینه ادیتور
        pal.setColor(QPalette.ColorRole.Text, QColor("#000000"))  # متن ادیتور
        pal.setColor(QPalette.ColorRole.Highlight, QColor("#d3d3d3"))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        editor.setPalette(pal)
        editor.setAutoFillBackground(True)
        return editor

class WidgetManager(QWidget):
    def __init__(self, parent):
        super().__init__(parent)  # ✅ درستش اینه
        self.parent = parent
        self.stack = QStackedWidget(parent)
        self.frames = {}
        self.denied_buttons= []

        self.frame2 = None
        self.das_frame = None
        self.frame_order = None
        self.finance_frame = None
        self.inventory_frame = None
        self.settings_frame = None

        self.create_frame1()
        self.invoice_counter = 1
        self.invoices = {}
        self.barcode_searching = False
        self.barcode= None
        ##هشدار ها
        self.notification_queue = []  # صف مرکزی نوتیفیکیشن‌ها
        self.notification_showing = False

        self.label_ui()
        self.set_today_date()
        self.set_today_time()
        self.Button_ui()
        self.Entries_ui()
        self.auto_synced()
        self.set_factor_number()
        self.added_products = []  # هر آیتم: دیکشنری حاوی اطلاعات محصول
        self.temp_loaded_invoice = []
        self.load_today_invoices()
        self.load_all_fonts()
        self.update_info_invnenvtory()
        self.get_info()
        self.select_name_products()
        self.start_notification_checker()

    def create_frame1(self):
        self.frame1 = QFrame()
        self.frame1.setStyleSheet("background-color: #D9D9D9;")
        ##
        main_layout = QVBoxLayout(self.frame1)
        
        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("فروش محصولات", self)


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
        top_layout.addWidget(self.label, 1)

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        
        # میانی: جدول و فرم
        middle_layout = QHBoxLayout()

        # جدول فروش
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        ##
        table_layout = QVBoxLayout(table_frame)
        ##
        self.top_layout= QHBoxLayout()
        #
        self.table_title = QLabel("بل فروشات")
        self.table_title.setAlignment( Qt.AlignmentFlag.AlignHCenter)
        self.ta_lb= QLabel("")
        self.ta_lb.setAlignment( Qt.AlignmentFlag.AlignRight)
        ##
        self.save_btns= QPushButton()
        ##
        self.clear_btn= QPushButton()
        ##
        self.top_layout.addWidget(self.save_btns)
        self.top_layout.addSpacing(230)
        self.top_layout.addWidget(self.table_title)
        self.top_layout.addStretch(1)
        self.top_layout.addWidget(self.clear_btn)
        self.top_layout.addSpacing(20)
    
        
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
        self.factor_layout.addWidget(self.factor_number)
        self.factor_layout.addWidget(self.factor_lb) 
        ##
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["نام محصول", "قیمت","تعداد", "واحد", "تخفیف","قیمت کل","عملیات"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setVisible(False)  # عدم نمایش شماره ردیف
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)  # اضافه برای نمایش خط‌ها
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # بعد از setStyleSheet:
        self.table.setItemDelegate(EditHighlightDelegate())
        # بهتر: انتخاب تک‌سلولی حتماً روشن باشد
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                font-family: Roboto,'B Nazanin';
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
                gridline-color: black;
                selection-background-color: #d3d3d3;   /* برای برخی استایل‌ها لازم می‌شود */
                selection-color: black;
            }
            QHeaderView::section {
                background-color: transparent;
                border: 1px solid black;
                color: black;
                font-family: Roboto,'B Nazanin';
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;
            }
            QTableWidget::item:selected:active,
            QTableWidget::item:selected:!active {
                background: #d3d3d3;
                color: black;
            }

            QScrollArea { border: none; }
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::handle:vertical:hover { background: #666; }
        """)


        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.table.itemChanged.connect(self.calculate_total_price)
        ###
        table_layout.addLayout(self.factor_layout)
        table_layout.addLayout(self.top_layout)
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

        self.less_sale= QLabel("پرچون")
        self.big_sale =QLabel("عمده")
        self.switch= ToggleSwitch()
        self.switch.setChecked(False)
        self.switch.clicked = lambda: print("ON") if self.switch.isChecked() else print("OFF")
        self.radio_layout.addWidget(self.less_sale)
        self.radio_layout.addWidget(self.switch)
        self.radio_layout.addWidget(self.big_sale)
       
        ##
        self.form_title = QLabel("فرم فروشات")
        self.form_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.barcode_input= QLineEdit()
        self.barcode_input.setPlaceholderText("بارکد محصول")
        # self.barcode_input.textChanged.connect(self.auto_search)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام محصول")
        self.name_input.textChanged.connect(self.auto_search_name)

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
        self.title_layout.addStretch(3)
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
        # در __init__ یا setup:
        self.name_input.installEventFilter(self)
        self.qty_input.installEventFilter(self)
        self.barcode_input.installEventFilter(self)
        # فریم شناور اعلان
        self.notification_frame = QFrame(self.frame1)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.frame1.width(), 0)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()


        self.frames["frame1"] = self.frame1
        self.stack.addWidget(self.frame1)
        ##
        
    ##
    def Entries_ui(self):

        for input in (self.barcode_input, self.name_input,self.unit_price_input,self.qty_input,self.discount_input, self.total_price_input):
            self.form_layout.addWidget(input)
            input.setFixedHeight(40)
            
            if input == self.barcode_input:
                font_family = 'Arial'
            else:
                font_family = 'Roboto,"B Nazanin"'  # در صورت عدم موجود بودن فونت اول، Arial استفاده می‌شود
            
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
        QListWidget {
            color: black;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 14px;
            padding: 5px;
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
        for label in (self.less_sale,self.big_sale):
            label.setStyleSheet('''
                color: black;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 12px;
            ''')
        ##
        self.invoice_list.itemClicked.connect(self.load_invoice)

    ##
    def clear_table(self):
        if self.table.rowCount() > 0:
            self.table.setRowCount(0)  # پاک کردن تمام ردیف‌ها به شکل ایمن
            self.table.clearContents()  # پاک کردن محتویات سلول‌ها
            self.table.setShowGrid(False)
    ##

    def Button_ui(self):
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
                    color: white;
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
        save_icon= QIcon(self.get_asset_path("save-icon.png"))
        self.save_btns.setIcon(save_icon)
        self.save_btns.setIconSize(QtCore.QSize(30,30))
        self.save_btns.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.save_btns.clicked.connect(self.save_prouducts)
        self.save_btns.setText("ذخیره محصول  ")
        self.save_btns.setStyleSheet('''
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
        ##
        clear_icon= QIcon(self.get_asset_path("paint-brush.png"))
        self.clear_btn.setIcon(clear_icon)
        self.clear_btn.setIconSize(QtCore.QSize(28,28))
        self.clear_btn.clicked.connect(self.clear_table)
        self.clear_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.clear_btn.setText("پاک کردن جدول  ")
        self.clear_btn.setStyleSheet('''
            QPushButton{
                background-color: white;
                color: black;
                font-family: B Nazanin;
                font-weight: bold;
                font-size: 14px;
                padding-right: 40px;
                padding-left: 0px;          
                                        }
        QPushButton:pressed{
            color: black;
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

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

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
        self.barcode_searching = True  # شروع پردازش بارکد

        barcode = self.barcode_input.text().strip()
        if not barcode:
            self.barcode_searching = False
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("Database not found.")
            self.barcode_searching = False
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            is_switch_on = self.switch.isChecked()

            if is_switch_on:
                cursor.execute("SELECT name, big_price,barcode FROM products WHERE barcode = ?", (barcode,))
            else:
                cursor.execute("SELECT name, sale_price,barcode FROM products WHERE barcode = ?", (barcode,))

            result = cursor.fetchone()

            if result:
                name, price,barcode = result
                self.name_input.setText(name)
                self.unit_price_input.setText(str(price))
                self.barcode= str(barcode)
            else:
                self.name_input.setText('')
                self.unit_price_input.setText('')

        except sqlite3.Error as e:
            print(f"Database error during barcode search: {e}")

        finally:
            conn.close()
            self.barcode_searching = False  # پایان پردازش بارکد


    ##
    def search_name_pro(self):
        name= self.name_input.text().strip()
        is_switch_on = self.switch.isChecked()
        if not name:
            MessageBox("لطفاً نام محصول را وارد کنید",title="یادآوری",type="warning").show()
        conn_sq=None
        cursor_sq= None

        # خواندن شناسه کاربر از دیتابیس محلی
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return
        try:
            if is_switch_on:
                ##
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute('''
                select barcode,big_price,name
                From products WHERE  TRIM(name)=?''',(name,))
                result= cursor_sq.fetchone()
            else:
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute('''
                select barcode,sale_price,name
                From products WHERE  TRIM(name)=?''',(name,))
                result= cursor_sq.fetchone()
            
            if result:
                    self.barcode_input.clear()
                    self.barcode_input.insert(str(result[0]))
                    print(f"{result[0]}: barcode")
                    self.barcode= result[0]
                    ##
                    self.unit_price_input.clear()
                    self.unit_price_input.insert(str(result[1]))
                    ##
                    self.qty_input.setText(str(1))

    
        except sqlite3.Error as e:
            MessageBox(f"{e}: خطا در دیتابیس",type="error",title="خطا").show()
    ##
    def auto_search_name(self):
        text = self.name_input.text().strip()
        if text:  # اگر حتی یک حرف نوشته شده باشد
            self.search_name_pro()
    ##
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):

            if source == self.barcode_input:
                self.barcode_input.selectAll()
                if getattr(self, 'barcode_ready', False) and self.barcode_input.hasSelectedText():
                    self.add_product()
                    self.barcode_ready = False
                    return True

                self.search_barcode()
                self.barcode_input.selectAll()
                self.barcode_ready = True

                def delayed_add():
                    if self.barcode_input.hasSelectedText() and self.barcode_input.hasFocus():
                        self.add_product()
                        self.barcode_ready = False

                QTimer.singleShot(6000, delayed_add)
                return True

            elif source == self.name_input:
                self.name_input.selectAll()
                if getattr(self, 'name_ready',False) and self.name_input.hasSelectedText():
                    self.add_product()
                    self.name_ready= False
                    return True
                self.search_name_pro()
                self.name_input.selectAll()
                self.name_ready= True
                
                def delay_product():
                    if self.name_input.hasSelectedText() and self.name_input.hasFocus():
                        self.add_product()
                        self.name_ready= False
                QTimer.singleShot(3000,delay_product)
                return True

            elif source in [self.qty_input, self.unit_price_input, self.discount_input]:
                qty = self.qty_input.text().strip()
                if qty:
                    self.add_product()
                return True

        return super().eventFilter(source, event)

    ##
    def auto_search(self):
        text= self.barcode_input.text().strip()
        name= self.name_input.text().strip()
        if text:
            self.search_barcode()
        elif name:
            self.search_name_pro()
    ##
    def add_product(self):
        barcode = self.barcode_input.text().strip()
        name = self.name_input.text().strip()
        qty = self.qty_input.text()
        unit_price = self.unit_price_input.text()
        discount = self.discount_input.text()
        total_price = self.total_price_input.text()
        is_switch_on = self.switch.isChecked()
        total_profit= 0
        item_price= 0

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        if barcode and name and qty and unit_price and total_price:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT big_category, quantity,sale_unit, big_quantity,big_price,buy_price FROM products WHERE barcode = ?", (barcode,))
                product_info = cursor.fetchone()
                if not product_info:
                    MessageBox("محصول یافت نشد!", title="خطا", type="error").show()
                    return
                self.barcode= barcode

                big_category, stock_quantity,sale_unit, big_quantity,big_price,buy_price = product_info
                print(sale_unit)
                unit_price = float(unit_price or 0)
                if unit_price.is_integer():
                    unit_price= int(unit_price)
                qty = float(qty or 1)
                if qty.is_integer():
                    qty= int(qty)
                discount = float(discount or 0)
                if big_quantity == 0:
                    big_quantity= 1
                if discount.is_integer():
                    discount= int(discount)
                item_price= float(buy_price/big_quantity)
                print(f"قمیت فی دانه :{item_price}")

                if is_switch_on:
                    s_type = big_category
                    quantity = qty * float(big_quantity or 1)
                    sale_type = "عمده"
                    total_profit = float((big_price - buy_price - discount) * qty)
                else:
                    s_type = sale_unit
                    quantity = qty
                    sale_type = "پرچون"
                    
                    total_profit= float((unit_price - item_price - discount) * qty)
                print(f"total_profit: {total_profit} ")

                # بررسی موجودی انبار:
                if quantity > float(stock_quantity):
                    MessageBox(f"موجودی محصول {name} کافی نیست", title="ناموفق", type="warning").show()
                    return
                # بررسی تکراری بودن محصول:
                for i, product in enumerate(self.added_products):
                    if product['barcode'] == barcode and product['s_type'] == s_type:
                        total_quantity = product['quantity'] + quantity
                        if total_quantity > float(stock_quantity):
                            MessageBox(f"موجودی کافی برای افزودن {name} وجود ندارد", title="ناموفق", type="warning").show()
                            return

                        product['quantity'] = total_quantity
                        product['raw_qty'] += qty
                        product['total'] += float(total_price)
                    
                        self.table.setItem(i, 2, self._make_cell(str(product['raw_qty'])))
                        self.table.setItem(i, 5, self._make_cell(str(product['total'])))

                        # ✅ پاک‌سازی فیلدها حتی اگر فقط بروزرسانی شده باشد
                        self.barcode_input.clear()
                        self.name_input.clear()
                        self.qty_input.clear()
                        self.unit_price_input.clear()
                        self.discount_input.clear()
                        self.total_price_input.clear()
                        self.switch.setChecked(False)
                        return

                # اگر تکراری نبود، سطر جدید اضافه شود
                row = self.table.rowCount()
                self.table.insertRow(row)
                ####
                # دکمه حذف
                denied_btn = QPushButton()
                denied_icon = QIcon(self.get_asset_path("MacOS Close.png"))
                denied_btn.setIcon(denied_icon)
                denied_btn.setIconSize(QtCore.QSize(25, 25))
                denied_btn.setStyleSheet('''
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                ''')
                ##
                self.edit_btn= QPushButton()
                self.edit_btn.setIcon(QIcon(self.get_asset_path("Edit.png")))
                self.edit_btn.setIconSize(QSize(25,25))
                self.edit_btn.setStyleSheet('background-color: transparent;')

                # اتصال دکمه به تابع حذف ردیف مخصوص خود
                denied_btn.clicked.connect(partial(self.delete_product))
                self.edit_btn.clicked.connect(partial(self.enable_edditing))

                # ذخیره در لیست دکمه‌ها
                btn_widget= QWidget()
                btn_layout= QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0,0,0,0)
                btn_layout.setSpacing(5)
                btn_layout.addWidget(denied_btn)
                btn_layout.addWidget(self.edit_btn)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                btn_widget.setStyleSheet("background-color: transparent;")

                self.denied_buttons.append(self.edit_btn)
                self.denied_buttons.append(denied_btn)

                # درج اطلاعات در جدول
                self.table.setItem(row, 0, self._make_cell(name))
                self.table.setItem(row, 1, self._make_cell(str(unit_price)))
                self.table.setItem(row, 2, self._make_cell(str(qty)))
                self.table.setItem(row, 3, self._make_cell(s_type))
                self.table.setItem(row, 4, self._make_cell(str(discount)))
                self.table.setItem(row, 5, self._make_cell(total_price))
                self.table.setCellWidget(row, 6, btn_widget)

                self.added_products.append({
                    "barcode": barcode,
                    "name": name,
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "number": quantity,
                    "raw_qty": qty,
                    "profit": total_profit,
                    "s_type": s_type,
                    "sale_type": sale_type,
                    "type" : sale_unit,
                    "discount": discount,
                    "profit" : total_profit,
                    "total": float(total_price),
                })

                # ✅ پاک‌سازی فیلدها بعد از درج جدید
                self.barcode_input.clear()
                self.name_input.clear()
                self.qty_input.clear()
                self.unit_price_input.clear()
                self.discount_input.clear()
                self.total_price_input.clear()
                self.switch.setChecked(False)
                self.table.setShowGrid(True)
                self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            except sqlite3.Error as e:
                MessageBox(text=f"{e}: خطا در دیتابیس", title="ناموفق", type="error").show()
            finally:
                conn.close()
    ##
    def save_prouducts(self):
        items = self.added_products if self.added_products else self.temp_loaded_invoice

        if not items:
            MessageBox("هیچ محصولی به فاکتور اضافه نشده است", title="خطا", type="warning").show()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        barcode = self.barcode
        print(barcode)
        factor_number = self.factor_value
        date = datetime.date.today().strftime("%Y/%m/%d")
        date_ent = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

        invoice_key = f"فاکتور {factor_number}"
        self.invoices[invoice_key] = self.added_products

        # حذف آیتم تکراری
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

            for product in items:
                barcode = product['barcode']
                name = product['name']
                unit_price = product['unit_price']
                quantity = product['quantity']       # برای ذخیره در دیتابیس
                s_type = product['s_type']
                sale_type = product['sale_type']
                discount_val = product['discount']
                final_total = product['total']
                profit= product['profit']

                cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
                product_quantity_row = cursor.fetchone()
                product_quantity = product_quantity_row[0] if product_quantity_row else 0

                if float(quantity) > product_quantity:
                    MessageBox(f"موجودی محصول {name} کافی نیست", title="ناموفق", type="warning").show()
                    continue
                is_synced=0
                cursor.execute('''
                    INSERT INTO sale_factor (barcode, product_name, factor_number, sale_price, sale_date, quantity,
                        product_type, sale_type, discount, profit,total, created_at, user_id, is_synced)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                ''', (
                    barcode, name, factor_number, unit_price, date, quantity, s_type, sale_type,
                    discount_val, profit,final_total, date_ent, id_user, is_synced
                ))

            cursor.execute("INSERT INTO factor_number(sale_id) VALUES (?)", (factor_number,))
            #type_save= "sale"
            #cursor.execute("update products set type_save=? where barcode=?",(type_save,barcode))
            conn.commit()
            MessageBox(text="اطلاعات موفقانه ذخیره شد✅",title="موفقانه",type="info").show()

            # بازخوانی فاکتورهای امروز برای نمایش
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

                if not any(self.invoice_list.item(i).text() == invoice_key for i in range(self.invoice_list.count())):
                    self.invoice_list.addItem(invoice_key)

            conn.close()

            self.factor_value = None
            self.set_factor_number()
            self.factor_number.setText(f"{self.factor_value}")
            items = self.added_products.copy()
            self.added_products.clear()
            self.temp_loaded_invoice.clear()
            self.table.setRowCount(0)
            self.table.setShowGrid(False)


        except sqlite3.Error as e:
            print(f"{e}: خطا در پایگاه داده")
            MessageBox(f"خطا در پایگاه داده: {e}", title="❌ خطا", type="error").show()
            return
    ##
    def enable_edditing(self):
        button= self.sender()
        for row in range(self.table.rowCount()):
            cell_widget= self.table.cellWidget(row,6)
            if cell_widget:
                if button in cell_widget.findChildren(QPushButton):
                    self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
                    self.table.setCurrentCell(row,2)
                    item= self.table.item(row,2)
                    if item:
                        # تغییر رنگ پس زمینه و متن
                        item.setData(QtCore.Qt.ItemDataRole.BackgroundRole, QtGui.QColor("#d3d3d3"))
                        item.setData(QtCore.Qt.ItemDataRole.ForegroundRole, QtGui.QColor("#000000"))

                        self.table.editItem(item)
                        break


    ##
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
        items = self.added_products if self.added_products else self.temp_loaded_invoice

        if not items:
            MessageBox("هیچ محصولی به فاکتور اضافه نشده است", title="خطا", type="warning").show()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        barcode = self.barcode
        factor_number = self.factor_value
        date = datetime.date.today().strftime("%Y/%m/%d")
        date_ent = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

        invoice_key = f"فاکتور {factor_number}"
        self.invoices[invoice_key] = self.added_products

        # حذف آیتم تکراری
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

            for product in items:
                barcode = product['barcode']
                name = product['name']
                unit_price = product['unit_price']
                quantity = product['quantity']       # برای ذخیره در دیتابیس
                s_type = product['s_type']
                sale_type = product['sale_type']
                discount_val = product['discount']
                final_total = product['total']
                profit= product['profit']

                cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
                product_quantity_row = cursor.fetchone()
                product_quantity = product_quantity_row[0] if product_quantity_row else 0

                if float(quantity) > product_quantity:
                    MessageBox(f"موجودی محصول {name} کافی نیست", title="ناموفق", type="warning").show()
                    continue

                cursor.execute('''
                    INSERT INTO sale_factor (barcode, product_name, factor_number, sale_price, sale_date, quantity,
                        product_type, sale_type, discount, profit,total, created_at, user_id, is_synced)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                ''', (
                    barcode, name, factor_number, unit_price, date, quantity, s_type, sale_type,
                    discount_val,profit, final_total, date_ent, id_user, 0
                ))

            cursor.execute("INSERT INTO factor_number(sale_id) VALUES (?)", (factor_number,))
            #type_save= "sale"
            #cursor.execute("update products set type_save=? where barcode=?",(type_save,barcode))
            conn.commit()

            # بازخوانی فاکتورهای امروز برای نمایش
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
                cursor.execute("select address,phone from printer LIMIT 1")
                result= cursor.fetchone()
                cursor.execute("select store_name from logo limit 1")
                name_result= cursor.fetchone()
                address= "خالی"
                phone= "خالی"
                store_name= "خالی"
                if result:
                    address= result[0]
                    phone= result[1]
                else:
                    address= "خالی"
                    phone= "خالی"
                if name_result:
                        store_name= name_result[0]
                else:
                    store_name= "خالی"

                



                if not any(self.invoice_list.item(i).text() == invoice_key for i in range(self.invoice_list.count())):
                    self.invoice_list.addItem(invoice_key)

            conn.close()

            self.factor_value = None
            self.set_factor_number()
            self.factor_number.setText(f"{self.factor_value}")
            items = self.added_products.copy()
            self.added_products.clear()
            self.temp_loaded_invoice.clear()
            self.table.setRowCount(0)

        except sqlite3.Error as e:
            print(f"{e}: خطا در پایگاه داده")
            MessageBox(f"خطا در پایگاه داده: {e}", title="❌ خطا", type="error").show()
            return

        # چاپ فاکتور
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        doc = QTextDocument()

        total_sum = sum(float(p['total']) for p in items)

        html = f"""
            <html>
            <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Roboto,'B Nazanin';
                    direction: rtl;
                    background-color: white;
                }}
                .container {{
                    text-align: center;
                    display: flex;
                    justify-content: center;
                    margin: 0 auto;
                    width: 500px;
                }}
                .center {{
                    text-align: center;
                    margin-bottom: 3px;
                }}
                .factor{{
                    font-size: 10pt;
                    font-family: Roboto, 'B Nazanin';
                    font-weight: bold;
                }}
                table {{
                    width: 100%;
                    margin: 8px 0;
                    border-collapse: collapse;
                    font-size: 14pt;
                    margin-right: 70px;
                }}
                th, td {{
                    padding: 8px;
                    border: none;
                    font-size: 11pt;
                }}
                thead th {{
                    border-top: 1px dashed gray;
                    border-bottom: 1px solid gray;
                    font-weight: bold;
                }}
                th.price-col {{
                    width: 30%;
                    text-align: left;
                }}
                th.qty-col {{
                    width: 40%;
                    
                }}
                th.name-col {{
                    width: 40%;
                    text-align: right;
                }}
                td.price-col {{
                    text-align: left;
                }}
                td.qty-col {{
                    text-align: center;
                }}
                td.name-col {{
                    text-align: right;
                }}
                .total-row th {{
                    border-top: 1px solid gray;
                    padding-top: 10px;
                }}
                .logo {{
                    text-align: center;
                    margin-top: 20px;
                    font-weight: bold;
                    font-size: 12pt;
                }}
            </style>
            </head>
            <body>
            <div class="container">
                <div>
                    <h1>{store_name}</h1>
                    <div class="center">{address}</div>
                    <div class= "center"> {phone} </div>
                    <table>
                        <tr>
                            <td><b class="factor">{factor_number} :نمبر فاکتور</b></td>
                            <td style="text-align: left;"><b class="factor">{date} :تاریخ</b></td>
                        </tr>
                    </table>

                    <table>
                        <thead>
                            <tr>
                                <th class="price-col">قیمت</th>
                                <th class="qty-col">تعداد</th>
                                <th class="name-col">نام</th>          
                            </tr>
                        </thead>
                        <tbody>
            """

            # اضافه کردن ردیف‌های محصول
        for product in items:
                name = product['name']
                product_type = product['type']
                numer = product['number']
                final = product['total']
                qua = round(numer)
                html += f"""
                    <tr>
                        <td class="price-col">{final:.2f}</td>
                        <td class="qty-col">
                            <div style="width: 100%; display: flex; justify-content: space-between;">
                                <span style="text-align: left;">{product_type}</span>
                                <span style="text-align: right;">{qua}</span>
                            </div>
                        </td>
                        <td class="name-col">{name}</td>
                    </tr>
                """


            # مجموع، تخفیف و پرداخت‌شده
        html += f"""
                        </tbody>
                        <tfoot>
                            <tr>
                                <th style="text-align: left; border-top: 1px solid gray;" colspan="2">{total_sum:.2f}</th>
                                <th style="text-align: right;border-top: 1px solid gray;" colspan="1">مجموع کل</th>
                            </tr>
                            <tr>
                                <th colspan="2" style="text-align: left;">{total_sum:.2f}</th>
                                <th style="text-align: right;">پرداخت شده</th>
                            </tr>
                        </tfoot>
                    </table>

                    <div class="logo">
                        <div>//</div>
                        <div><b>AQSA GROUP</b></div>
                    </div>
                </div>
            </div>
            </body>
            </html>
            """

        doc.setHtml(html)
        doc.print(printer)

        self.table.setRowCount(0)
        self.table.setShowGrid(False)
    ##
    def synced_to_server_to_sale(self):
        db_connect= Connection().get_connection()
        if not db_connect:
            return
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print("no db home offline found!")
            return
    
        ##offline
        conn_sq = sqlite3.connect(db_path)
        cursor_sq = conn_sq.cursor()
        cursor_sq.execute('''
            SELECT product_name, factor_number, barcode,
                sale_date, sale_price, quantity, product_type,
                sale_type, discount,profit,total, user_id,created_at
            FROM sale_factor WHERE is_synced = 0
        ''')

        unsynced_products = cursor_sq.fetchall()

        try:
            ##online
            cursor= db_connect.cursor()
    
            for product in unsynced_products:
                (product_name, factor_number, barcode, sale_date, sale_price,
                quantity, product_type, sale_type, discount, profit,total, user_id, created_at) = product


                cursor.execute('''
                        INSERT INTO sale_factor(product_name, barcode, factor_number, sale_date, sale_price,
                            quantity, product_type, sale_type, discount, profit,total, user_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                    ''', (
                        product_name, barcode, factor_number, sale_date, sale_price,
                        quantity, product_type, sale_type, discount,profit, total, user_id, created_at
                    ))
                print(f"✅ item {barcode}  added")
                ## update products
                cursor_sq.execute("UPDATE products SET is_synced=0 where barcode=?",(barcode,))
                print(f"✅ اطلاعات با موفقیت به {barcode} رسید")


            db_connect.commit()
            

            cursor_sq.execute("UPDATE sale_factor SET is_synced = 1 WHERE is_synced = 0")
            conn_sq.commit()
            

        except Exception as e:
            print("❌ خطا در همگام‌سازی:", e)

        finally:
            conn_sq.close()
            if db_connect:
                db_connect.close()
   ##
    def calculate_total_price(self, item):
        row = item.row()
        col = item.column()

        # فقط اگر ستون قیمت (1)، تعداد (2) یا تخفیف (4) تغییر کرد
        if col in [1, 2, 4]:
            try:
                price = float(self.table.item(row, 1).text())
                count = float(self.table.item(row, 2).text())
                discount = float(self.table.item(row, 4).text())

                total = (price * count) - discount
                total_item = QTableWidgetItem(str(round(total, 2)))
                total_item.setFlags(total_item.flags() ^ Qt.ItemFlag.ItemIsEditable)  # غیرفعال‌سازی ویرایش برای قیمت کل
                total_item.setForeground(QBrush(Qt.GlobalColor.black))  # متن سیاه
                self.table.setItem(row, 5, total_item)

            except Exception as e:
                print("خطا در محاسبه قیمت کل:", e)

    def load_invoice(self, item):
        invoice_name = item.text()

        if invoice_name in self.invoices:
            self.temp_loaded_invoice = []  # پاک کردن لیست موقت
            self.table.setRowCount(0)  # حذف همه ردیف‌های قبلی
            self.table.setShowGrid(True)
            self.table.blockSignals(True)

            for name, price, number, unit, discount, total in self.invoices[invoice_name]:
                row = self.table.rowCount()
                # دکمه حذف
                denied_btn = QPushButton()
                denied_icon = QIcon(self.get_asset_path("MacOS Close.png"))
                denied_btn.setIcon(denied_icon)
                denied_btn.setIconSize(QtCore.QSize(25, 25))
                denied_btn.setStyleSheet('''
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                ''')

                # اتصال دکمه به تابع حذف ردیف مخصوص خود
                denied_btn.clicked.connect(self.delete_product)

                # ذخیره در لیست دکمه‌ها
                self.denied_buttons.append(denied_btn)
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(self._make_cell(str(name))))
                self.table.setItem(row, 1, QTableWidgetItem(self._make_cell(str(price))))
                self.table.setItem(row, 2, QTableWidgetItem(self._make_cell(str(number))))
                self.table.setItem(row, 3, QTableWidgetItem(self._make_cell(str(unit))))
                self.table.setItem(row, 4, QTableWidgetItem(self._make_cell(str(discount))))
                self.table.setItem(row, 5, QTableWidgetItem(self._make_cell(str(total))))
                self.table.setCellWidget(row,6,denied_btn)
                self.calculate_total_price(self.table.item(row, 1))

                # واکشی barcode از دیتابیس براساس نام و قیمت (در صورت نیاز می‌توان دقیق‌تر کرد)
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # رفتن یک سطح بالاتر از پوشه GUI
                root_dir = os.path.dirname(base_dir)
                db_path = os.path.join(root_dir, 'Data', 'sh_online.db')
                barcode = None

                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT barcode FROM products WHERE name = ? AND sale_price = ?", (name, price))
                    row_data = cursor.fetchone()
                    if row_data:
                        barcode = row_data[0]
                    conn.close()
                except Exception as e:
                    print(f"خطا در واکشی بارکد: {e}")

                # ذخیره در لیست موقت
                self.temp_loaded_invoice.append({
                    "name": name,
                    "unit_price": price,
                    "quantity": number,
                    "s_type": unit,
                    "discount": discount,
                    "total": total,
                    "barcode": barcode,  # حالا مقدار دارد
                    "sale_type": "",
                    "raw_qty": number
                })

            self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
            self.table.blockSignals(False)       
    
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

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

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
    def delete_product(self, row=None):
        # گرفتن ردیف انتخاب‌شده یا ردیف ورودی
        if row is None:
            row = self.table.currentRow()

        # اگر هیچ ردیفی انتخاب نشده بود
        if row < 0:
            MessageBox("هیچ محصولی انتخاب نشده است", title="خطا", type="warning").show()
            return

        # گرفتن آیتم ستون نام محصول
        name_item = self.table.item(row, 0)
        if not name_item:
            MessageBox("خطا در دریافت اطلاعات سطر انتخاب‌شده", title="خطا", type="error").show()
            return
        name = name_item.text()

        # تأیید حذف
        confirm_box = MessageBox(
            f"آیا مطمئن هستید که می‌خواهید محصول '{name}' را حذف کنید؟",
            title="تأیید حذف",
            type="question",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm_box.show() != QMessageBox.StandardButton.Yes:
            return

        # اگر محصول هنوز ذخیره نشده (فقط در added_products است)
        items = self.added_products
        for i, item in enumerate(items):
            if item.get("name") == name:
                del items[i]
                break

        # حذف از جدول UI
        self.table.removeRow(row)

        # اگر محصول از دیتابیس لود شده باشد
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # گرفتن شماره فاکتور
            current_item = self.invoice_list.currentItem()
            factor_number = None
            if current_item:
                factor_number = current_item.text().replace("فاکتور ", "").strip()

            if factor_number:
                for i, item in enumerate(self.temp_loaded_invoice):
                    if item.get("name") == name:
                        barcode = item.get("barcode")
                        qty = item.get("quantity", 0)

                        # برگرداندن موجودی انبار
                        if barcode:
                            cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
                            result = cursor.fetchone()
                            if result:
                                new_qty = float(result[0]) + float(qty)
                                cursor.execute(
                                    "UPDATE products SET quantity=?, is_synced=0 WHERE barcode=?",
                                    (new_qty, barcode)
                                )

                        # حذف از دیتابیس
                        cursor.execute("""
                            DELETE FROM sale_factor 
                            WHERE product_name=? AND barcode=? AND factor_number=?
                        """, (name, barcode, factor_number))

                        del self.temp_loaded_invoice[i]
                        break

                conn.commit()

                # حذف فاکتور اگر خالی شد
                cursor.execute("SELECT COUNT(*) FROM sale_factor WHERE factor_number=?", (factor_number,))
                if cursor.fetchone()[0] == 0:
                    for idx in range(self.invoice_list.count()):
                        if self.invoice_list.item(idx).text() == f"فاکتور {factor_number}":
                            self.invoice_list.takeItem(idx)
                            break

            conn.close()

        except sqlite3.Error as e:
            MessageBox(f"{e} : خطا در حذف یا بروزرسانی محصول", title="خطای دیتابیس", type="error").show()



    ##
    def select_name_products(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            print("no such file")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT name FROM products')
            result = cursor.fetchall()

            name_list = [row[0] for row in result if row[0]]

            completer = QCompleter(name_list, self.name_input)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.popup().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            completer.popup().setStyleSheet('''
                QListView {
                    background-color: white;
                    color: black;
                    font-size: 14px;
                    font-family: 'B Nazanin';
                    border: 1px solid gray;
                    padding: 4px;
                    selection-background-color: white;
                    selection-color: white;
                }
            ''')

            def show_completer_if_focused(text):
                if not self.barcode_searching:
                    completer.complete()

            self.name_input.textEdited.connect(show_completer_if_focused)
            self.name_input.setCompleter(completer)

        except sqlite3.Error as e:
            print(f"{e}: failed searching names")
        finally:
            conn.close()

    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.frame1.width(), self.notification_frame.height())
        return super().resizeEvent(event)

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
    def update_info_invnenvtory(self):
        from synce_updated import UpdateThread


        # فقط اگر ترد قبلی وجود نداشت یا تمام شده بود، یک ترد جدید بساز
        if not hasattr(self, "thread_to_server") or not self.thread_to_server.isRunning():
            self.thread_to_server = UpdateThread()

            self.thread_to_server.start()

        # ⏱ فقط یکبار تایمر بساز (اگر از قبل ساخته نشده باشد)
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer(self)
            self.update_timer.timeout.connect(self.update_info_invnenvtory)
            self.update_timer.start(15 * 1000)  # هر ۱۵ ثانیه
    ##
    def get_info(self):
        from fixdes import FixThread
        self.thread_to_get= FixThread()
        self.thread_to_get.start()

    ##
    def start_notification_checker(self):
        self.notif_checker = NotificationChecker()
        self.notif_checker.new_message.connect(self.show_notification_message)  # بدون ()
        self.notif_checker.exp_msg.connect(self.show_notification_exp)
        self.notif_checker.disc_msgs.connect(self.show_notification_disc)
        self.notif_checker.qua_msg.connect(self.show_quantity_msg)
        self.notif_checker.start()
    ##
    def enqueue_notification(self, pro_name: str, message: str):
        notif_key = f"{pro_name}:{message}"
        if notif_key in shown_notifications:
            return  # این هشدار قبلاً نمایش داده شده

        shown_notifications.add(notif_key)
        self.notification_queue.append((pro_name, message))
        if not self.notification_showing:
            self.show_next_notification()


    ##messages:
    def show_next_notification(self):
        if not self.notification_queue:
            self.notification_showing = False
            self.notification_frame.setFixedHeight(0)
            self.notification_frame.setGeometry(0, 0, self.frame1.width(), 0)
            return

        self.notification_showing = True
        pro_name, message = self.notification_queue.pop(0)

        # حذف ویجت‌های قبلی از notification_frame
        for child in self.notification_frame.children():
            if isinstance(child, QWidget) and child != self.notification_frame.layout():
                child.deleteLater()

        notif = Notification(
            pro_name=pro_name,
            message=message,
            parent_frame=self.notification_frame,
            icon_path=self.get_asset_path("alarm.png")
        )

        notif.setParent(self.notification_frame)
        notif.resize(notif.sizeHint())
        
        # 🔥 مرکز قرار دادن دستی
        x = (self.notification_frame.width() - notif.width()) // 2
        y = 0
        notif.move(x, y)

        self.notification_frame.setFixedHeight(100)
        self.notification_frame.setGeometry(0, 0, self.frame1.width(), 100)

        notif.closed.connect(self.show_next_notification)
        notif.show()




    ##
    def show_notification_message(self, pro_name: str, message: str):
        self.enqueue_notification(pro_name, message)
    ##
    def show_notification_exp(self, pro_names: list):
        for name in pro_names:
            self.enqueue_notification(name, "محصول انقضاء شده است لطفاً بررسی کنید")
    ##
    def show_notification_disc(self, product_names: list):

        for name in product_names:
            self.enqueue_notification("پایان اعتبار تخفیف", f"محصول {name} مدت اعتبار تخفیف آن به پایان رسید")
    ##
    def show_quantity_msg(self, product_names: list):
        for name in product_names:
            self.enqueue_notification("موجودی محصول", f"محصول {name} موجودی آن رو به اتمام است")
                    

        
