from PyQt6.QtWidgets import (QApplication,QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QFileDialog,QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QEvent,QPoint,QPropertyAnimation,QEasingCurve,QSize
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QTextDocument,QBrush,QPainter,QFont
import sqlite3
from message_b import MessageBox
import os,threading
from db_connection import Connection
from PyQt6.QtPrintSupport import QPrinter,QPrintDialog
import jdatetime



class ChangingFactor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #D9D9D9;")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self.load_all_fonts()
        self.auto_search()
        self.auto_sync()
        self.sale_ids= []
        self.sale_list= []
        self.print_list= []

    def setup_ui(self):
        self.stack_items = QStackedWidget()
        self.setCentralWidget(self.stack_items)
        self.items_page = QWidget()

        main_layout = QVBoxLayout(self.items_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addLayout(self.create_top_bar())
        main_layout.addWidget(self.create_frame(),2)
        main_layout.addWidget(self.visible_frame(),1)
        main_layout.addWidget(self.Invisible_frame())

        self.stack_items.addWidget(self.items_page)

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(15, 30, 20, 0)
        top_bar.setSpacing(10)

        title_label = QLabel("تغییرات فاکتور")
        title_label.setStyleSheet("color: black; font-family: Mirza; font-size: 20px; font-weight: bold;")
        title_label.setMinimumHeight(50)

        back_button = QPushButton()
        back_button.setIcon(QIcon(self.get_asset_path('left.png')))
        back_button.setIconSize(QSize(40, 40))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(self.back_settings)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #f8faff;
            }
        """)

        top_bar.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        top_bar.addStretch()
        top_bar.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop)

        return top_bar
    
    def create_frame(self):
        frame = QFrame()
        #frame.setMaximumHeight(400)
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")

        frame_shadow= QGraphicsDropShadowEffect(self)
        frame_shadow.setBlurRadius(10)
        frame_shadow.setOffset(0,5)
        frame_shadow.setColor(QColor(0,0,0,70))
        frame.setGraphicsEffect(frame_shadow)

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(10)

        frame_title_label = QLabel("تغییر فاکتور فروش")
        frame_title_label.setStyleSheet("background-color:transparent; color: black; font-family: Mirza,'B Nazanin'; font-size: 18px; font-weight: bold;")
        frame_title_label.setMinimumHeight(25)

        frame_layout.addWidget(frame_title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.frame_search_input = QLineEdit()
        self.frame_search_input.setContentsMargins(0, 0, 30, 0)
        self.frame_search_input.setPlaceholderText("نمبر فاکتور...")
        self.frame_search_input.setFixedSize(200, 40)
        self.frame_search_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #222222;
            font-size: 14px;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            padding: 5px;
        """)
        self.frame_search_input.textChanged.connect(self.auto_search)
        frame_layout.addWidget(self.frame_search_input, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.frame_search_input.setGraphicsEffect(shadow)
        ##
        table_layout= QVBoxLayout()
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["نام", "بارکد", "تاریخ", "قیمت", "تعداد", "واحد","تخفیف", "مجموعه","عملیات"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                font-family: Roboto,'B Nazanin';
                font-size: 14px;
                font-weight: bold;
                gridline-color: black;
            }
            QHeaderView::section {
                background-color: transparent;
                border: 1px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        # responsive size policy (both horizontal and vertical expanding)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.table.itemChanged.connect(self.calculate_total_price)
        table_layout.setContentsMargins(20,0,20,0)

        # اضافه کردن بدون alignment برای اجازه رشد کامل
        table_layout.addWidget(self.table)
        
        frame_layout.addLayout(table_layout)
        frame_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 10)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        print_button = QPushButton("پرنت")
        print_button.setIcon(QIcon(self.get_asset_path('print.png')))
        print_button.setIconSize(QSize(24, 24))
        print_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        print_button.clicked.connect(self.print_factor)
        print_button.setFixedSize(100, 40)
        print_button.setStyleSheet("""
            QPushButton {
                background-color: #0047ab;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #003b91;
            }
        """)

        save_button = QPushButton("ذخیره تغییرات")
        save_button.setIcon(QIcon(self.get_asset_path('Bookmark.png')))
        save_button.setIconSize(QSize(24, 24))
        save_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        save_button.setFixedSize(120, 40)
        save_button.clicked.connect(self.change_factor)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #00cc66;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #00b359;
            }
        """)

        button_layout.addWidget(print_button)
        button_layout.addWidget(save_button)

        frame_layout.addLayout(button_layout)

        frame.setLayout(frame_layout)

        return frame
    
    def visible_frame(self):
        visible_frame = QFrame()
        #visible_frame.setMaximumHeight(350)
        visible_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        
        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setYOffset(5)
        shadow.setXOffset(0)
        shadow.setColor(QColor(0,0,0,70))
        visible_frame.setGraphicsEffect(shadow)
        
        visible_frame_layout = QVBoxLayout(visible_frame)
        visible_frame_layout.setContentsMargins(0, 0, 0, 0)
        visible_frame_layout.setSpacing(5)

        ##
        print_title= QLabel("تغییر در اطلاعات پرنتر")
        print_title.setStyleSheet('''
        background-color:transparent; 
        color: black; font-family: Mirza,'B Nazanin'; 
        font-size: 18px; font-weight: bold;
        ''')
        print_title.setMinimumHeight(30)
        ##
        labels= [
            "آدرس فروشگاه:","شماره تماس:","شماره دیگر:"
        ]

        self.print_inputs= []
        for i in range(0, len(labels),3):
            printer_layout= QHBoxLayout()
            printer_layout.setSpacing(5)
            printer_layout.setContentsMargins(0,0,0,0)
            printer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            for j in range(3):
                if i+j < len(labels):
                    label= QLabel(labels[i+j])
                    label.setStyleSheet('''
                        color: black; font-family: B Nazanin; 
                        font-size: 16px; font-weight: bold;
                    ''')
                    label.setMaximumSize(87,20)
                    label.setMinimumSize(40,10)
                    line_edit= QLineEdit()
                    line_edit.setMaximumSize(200,45)
                    line_edit.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
                    line_edit.setMinimumSize(100,20)
                    line_edit.setStyleSheet("""
                        background-color: transparent;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 15px;
                        font-family: Roboto,'B Nazanin';
                        font-weight: bold;
                        color: #222;
                    """)
                    self.print_inputs.append(line_edit)
                    pair_layout= QHBoxLayout()
                    pair_layout.setSpacing(5)
                    pair_layout.addWidget(label)
                    pair_layout.addWidget(line_edit)
                    
                    pair_container= QWidget()
                    pair_container.setStyleSheet("background-color: white;")
                    pair_container.setLayout(pair_layout)
                    printer_layout.addWidget(pair_container)

        btn_layout= QHBoxLayout()
        btn_layout.setContentsMargins(10,5,10,5)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        save_button = QPushButton("ذخیره تغییرات")
        save_button.setIcon(QIcon(self.get_asset_path('Bookmark.png')))
        save_button.setIconSize(QSize(24, 24))
        save_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        save_button.setFixedSize(120, 40)
        save_button.clicked.connect(self.change_printer)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #00cc66;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #00b359;
            }
            QPushButton:Pressed{
                background-color: #00cc66;
                                  }
        """)
        btn_layout.addWidget(save_button)
        
        visible_frame_layout.addWidget(print_title, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter))
        visible_frame_layout.addLayout(printer_layout)
        visible_frame_layout.addLayout(btn_layout)
        
        return visible_frame
    ##
    def Invisible_frame(self):
        invisible_frame = QFrame()
        #invisible_frame.setMinimumHeight(50)
        invisible_frame.setStyleSheet("background-color: transparent; border-radius: 10px;")
    
        
        invisible_frame_layout = QVBoxLayout()
        invisible_frame_layout.setContentsMargins(0, 0, 0, 0)
        invisible_frame_layout.setSpacing(10)

        invisible_frame_layout.addWidget(invisible_frame)

        return invisible_frame
    ##
    def back_settings(self):
        from settings import Settings
        self.settings_main= Settings()
        self.stack_items.addWidget(self.settings_main)
        self.stack_items.setCurrentWidget(self.settings_main)
        self.settings_main.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        ##animation:
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.settings_main.move(start_pos)
        ##
        animation= QPropertyAnimation(self.settings_main, b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start() 
    ##
    def auto_search(self):
        text= self.frame_search_input.text().strip()
        if text:
            self.search_factor()

    ##
    def _make_cell(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.black)
        return item
    ##
    def search_factor(self):
        self.factor= None
        search= str(self.frame_search_input.text())
        real_quantity=0
        item_price=0
        if not search:
            MessageBox(text="لطفاً نمبر فاکتور را وارد کنید",title="هشدار",type="warning").show()
            return
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("مسیر یافت نشد")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            
            cursor.execute('''
                SELECT sale_id,product_name,barcode,sale_date,sale_price,quantity,product_type,sale_type,discount,total
                    FROM sale_factor WHERE factor_number= ?
            ''',(search,))
            search_result= cursor.fetchall()
            self.denied_buttons= []
            list_sa= {}
            self.table.setRowCount(0)
            if search_result:
                for (sale_id,product_name,barcode,sale_date,sale_price,quantity,product_type,sale_type,discount,total) in search_result:
                    cursor.execute("select big_quantity,buy_price,big_price from products where barcode = ?",(barcode,))
                    reuslt= cursor.fetchone()
                    big_qunatity= reuslt[0]
                    buy_price= reuslt[1]
                    big_price= reuslt[2]
                    buy_price =float(buy_price) if buy_price else 0
                    big_price= float(big_price) if big_price else 0
                    item_price= float(buy_price / big_qunatity)
                    
                    self.sale_ids.append(sale_id)
                    if sale_type== "عمده":
                        real_quantity= quantity / big_qunatity
                    elif sale_type== "پرچون":
                        real_quantity = quantity
                    print(f"qunatity in search:{real_quantity}")
                    row= self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row,0,QTableWidgetItem(self._make_cell(product_name)))
                    self.table.setItem(row,1, QTableWidgetItem(self._make_cell(str(barcode))))
                    self.table.setItem(row,2,QTableWidgetItem(self._make_cell(sale_date)))
                    self.table.setItem(row,3, QTableWidgetItem(self._make_cell(str(sale_price))))
                    self.table.setItem(row,4, QTableWidgetItem(self._make_cell(str(real_quantity))))
                    self.table.setItem(row,5,QTableWidgetItem(self._make_cell(product_type)))
                    self.table.setItem(row,6, QTableWidgetItem(self._make_cell(str(discount))))
                    self.table.setItem(row,7, QTableWidgetItem(self._make_cell(str(total))))
                    # ایجاد دیکشنری اطلاعات فقط برای همین سطر
                    list_sa = {
                        "sale_id" : sale_id,
                        "buy_price" : buy_price,
                        "sale_type": sale_type,
                        "item_price" : item_price,
                        "big_price" : big_price,
                        "big_quantity" : big_qunatity
                    }
                    self.sale_list.append(list_sa)
                    self.factor= search
                    
                    ##
                    self.edit_btn= QPushButton()
                    self.edit_btn.setIcon(QIcon(self.get_asset_path("Edit.png")))
                    self.edit_btn.setIconSize(QSize(25,25))
                    self.edit_btn.setStyleSheet('background-color: transparent;')
                    #
                    self.reject_btn= QPushButton()
                    self.reject_btn.setIcon(QIcon(self.get_asset_path("MacOS Close.png")))
                    self.reject_btn.setIconSize(QSize(25,25))
                    self.reject_btn.setStyleSheet('''
                        QPushButton {
                        background-color: transparent;
                            }
                        ''')
                    # ویجت و لایه برای دکمه‌ها
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    btn_layout.setSpacing(5)
                    btn_layout.addWidget(self.reject_btn)
                    btn_layout.addWidget(self.edit_btn)
                    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    btn_widget.setStyleSheet('background-color: transparent;')
                    self.table.setCellWidget(row,8,btn_widget)
                    
                    self.edit_btn.clicked.connect(self.enable_edit_mode)
                    self.denied_buttons.append(self.reject_btn)
                    self.denied_buttons.append(self.edit_btn)
                else:
                    MessageBox(text="فاکتور پیدا نشد",title="مشکل",type="error")


        except sqlite3.Error as e:
            print(f"problem db search:{e}")
    ##
    def change_printer(self):
        address = str(self.print_inputs[0].text()).strip()
        phone = str(self.print_inputs[1].text()).strip()
        another = str(self.print_inputs[2].text()).strip()

        if not address or not phone:
            MessageBox(text="لطفاً فیلدهای لازم را پر کنید", type="warning", title="هشدار").show()
            return

        complete_phone = f"{phone} - {another}" if another else phone

        # مسیر دیتابیس
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="اطلاعات محلی پیدا نشد", type="error", title="هشدار").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # بررسی وجود داده در جدول printer
            cursor.execute('SELECT address FROM printer LIMIT 1')
            result = cursor.fetchone()

            if result is None:
                # اگر هیچ رکوردی وجود ندارد → insert شود
                cursor.execute('INSERT INTO printer(address, phone) VALUES(?, ?)', (address, complete_phone))
            else:
                # اگر رکورد وجود دارد → update شود
                cursor.execute('UPDATE printer SET address = ?, phone = ?', (address, complete_phone))

            conn.commit()

            MessageBox(text="اطلاعات با موفقیت ذخیره شد", title="موفقیت", type="info").show()

            # پاک‌کردن فیلدهای فرم
            for field in self.print_inputs:
                field.clear()

        except sqlite3.Error as e:
            print(f"خطا در دیتابیس: {e}")
    ##
    def calculate_total_price(self, item):
        row = item.row()
        col = item.column()

        # فقط اگر ستون قیمت (1)، تعداد (2) یا تخفیف (4) تغییر کرد
        if col in [3, 4, 6]:
            try:
                price = float(self.table.item(row, 3).text())
                count = float(self.table.item(row, 4).text())
                discount = float(self.table.item(row, 6).text())

                total = (price * count) - discount
                total_item = QTableWidgetItem(self._make_cell(str(round(total, 2))))
                total_item.setFlags(total_item.flags() ^ Qt.ItemFlag.ItemIsEditable)  # غیرفعال‌سازی ویرایش برای قیمت کل
                total_item.setForeground(QBrush(Qt.GlobalColor.black))  # متن سیاه
                self.table.setItem(row, 7, total_item)

            except Exception as e:
                print("خطا در محاسبه قیمت کل:", e)
    ##
    def enable_edit_mode(self):
        button = self.sender()  # دکمه‌ای که کلیک شده

        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 8)  # ستون 8 = ویجت دکمه‌ها
            if cell_widget:
                # بررسی اینکه این دکمه داخل این ویجت هست یا نه
                if button in cell_widget.findChildren(QPushButton):
                    # فعال‌سازی حالت ویرایش
                    self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

                    # انتخاب ردیف و سلول اول
                    self.table.setCurrentCell(row, 0)
                    item = self.table.item(row, 0)
                    if item:
                        self.table.editItem(item)
                    break
    ##
    def change_factor(self):
        selected_row = self.table.currentRow()
        total_profit = 0
        real_quantity= 0

        if selected_row < 0:
            MessageBox(text="هیچ ردیفی برای بروزرسانی انتخاب نشده", title="اخطار", type="warning").show()
            return

        if selected_row >= len(self.sale_ids):
            MessageBox(text="شناسه فاکتور یافت نشد", title="خطا", type="warning").show()
            return

        sale_id = self.sale_ids[selected_row]

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data", "sh_online.db")

        if not os.path.exists(db_path):
            print("مسیر پایگاه‌داده یافت نشد")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            sale_date = self.table.item(selected_row, 2).text()
            price = float(self.table.item(selected_row, 3).text())
            quantity = float(self.table.item(selected_row, 4).text())
            discount = float(self.table.item(selected_row, 6).text())
            total = float(self.table.item(selected_row, 7).text())

            # فیلتر لیست برای آیتم‌های همین فاکتور
            item_list = [i for i in self.sale_list if i['sale_id'] == sale_id]

            for profit_co in item_list:
                buy_price = profit_co['buy_price']
                sale_type = profit_co['sale_type'].strip() if profit_co['sale_type'] else ""
                item_price = profit_co['item_price']
                big_price= profit_co['big_price']
                big_quantity= profit_co['big_quantity']

                print(f"[DEBUG] sale_type: '{sale_type}'")  # بررسی مقدار واقعی

                
                if sale_type == "عمده":
                    print(f"price={price}, buy_price={buy_price}, discount={discount}, quantity={quantity}")
                    part_profit = float((big_price - buy_price - discount) * quantity)
                    print(f"سود جزئی: {part_profit}")
                    total_profit += part_profit
                    real_quantity = float(quantity * big_quantity)
                elif sale_type =="پرچون":
                    total_profit += float((price - item_price - discount) * quantity)
                    real_quantity = quantity

                

            print(f"total profit: {total_profit}")

            cursor.execute('''
                UPDATE sale_factor SET 
                    sale_date=?, sale_price=?, quantity=?, discount=?, profit=?, total=?, sync=0
                WHERE sale_id=? AND sale_type= ?
            ''', (sale_date, price, real_quantity, discount, total_profit, total, sale_id,sale_type))
            conn.commit()

            MessageBox(text="اطلاعات فاکتور موفقانه تغییر کرد", title="موفقانه", type="info").show()
            self.frame_search_input.clear()
            self.table.setRowCount(0)

        except sqlite3.Error as e:
            print(f"خطا هنگام بروزرسانی پایگاه‌داده: {e}")
    ##
    def print_factor(self):
        selected_row = self.table.currentRow()
        total_profit = 0
        real_quantity = 0
        final_total=0

        if selected_row < 0:
            MessageBox(text="هیچ ردیفی برای بروزرسانی انتخاب نشده", title="اخطار", type="warning").show()
            return

        if selected_row >= len(self.sale_ids):
            MessageBox(text="شناسه فاکتور یافت نشد", title="خطا", type="warning").show()
            return

        sale_id = self.sale_ids[selected_row]

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data", "sh_online.db")

        if not os.path.exists(db_path):
            print("مسیر پایگاه‌داده یافت نشد")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT address, phone FROM printer LIMIT 1")
            info_result = cursor.fetchone()
            cursor.execute("SELECT store_name FROM logo LIMIT 1")
            name_result = cursor.fetchone()

            stor_name = name_result[0] if name_result else "---"
            address, phone = info_result if info_result else ("---", "---")
            factor = self.factor

            # مقداردهی اولیه
            sale_date = self.table.item(selected_row, 2).text()
            price = float(self.table.item(selected_row, 3).text())
            quantity = float(self.table.item(selected_row, 4).text())
            discount = float(self.table.item(selected_row, 6).text())
            total = float(self.table.item(selected_row, 7).text())

            # آیتم‌های همین فاکتور
            item_list = [i for i in self.sale_list if i['sale_id'] == sale_id]

            for profit_co in item_list:
                buy_price = profit_co['buy_price']
                sale_type = profit_co['sale_type'].strip() if profit_co['sale_type'] else ""
                item_price = profit_co['item_price']
                big_price = profit_co['big_price']
                big_quantity = profit_co['big_quantity']

                if sale_type == "عمده":
                    part_profit = float((big_price - buy_price - discount) * quantity)
                    total_profit += part_profit
                    real_quantity = float(quantity * big_quantity)
                elif sale_type == "پرچون":
                    total_profit += float((price - item_price - discount) * quantity)
                    real_quantity = quantity
                final_total= total

            cursor.execute('''
                UPDATE sale_factor SET 
                    sale_date=?, sale_price=?, quantity=?, discount=?, profit=?, total=?,sync=0
                WHERE sale_id=? AND sale_type=? AND factor_number=?
            ''', (sale_date, price, real_quantity, discount, total_profit, total,sale_id, sale_type,factor))
            conn.commit()
            print(final_total)

            MessageBox(text="اطلاعات فاکتور موفقانه تغییر کرد", title="موفقانه", type="info").show()

            # آماده‌سازی self.print_list با کل داده‌های جدول
            self.print_list.clear()
            
            row_count = self.table.rowCount()

            for row in range(row_count):
                try:
                    price = float(self.table.item(row, 3).text())
                    quantity = float(self.table.item(row, 4).text())
                    discount = float(self.table.item(row, 6).text())
                    total = float(self.table.item(row, 7).text())
                    row_sale_id = self.sale_ids[row]
                    item_list = [i for i in self.sale_list if i['sale_id'] == row_sale_id]

                    real_quantity = quantity
                    for item in item_list:
                        sale_type = item['sale_type'].strip() if item['sale_type'] else ""
                        buy_price = item['buy_price']
                        item_price = item['item_price']
                        big_price = item['big_price']
                        big_quantity = item['big_quantity']

                        if sale_type == "عمده":
                            real_quantity = quantity * big_quantity
                        elif sale_type == "پرچون":
                            real_quantity = quantity

                    self.print_list.append({
                        "factor_number": factor,
                        "name": self.table.item(row, 0).text(),
                        "type": self.table.item(row, 5).text(),
                        "price": price,
                        "number": real_quantity,
                        "discount": discount,
                        "total": total
                    })
                except Exception as e:
                    print(f"[⚠️ خطا در پردازش ردیف {row}]: {e}")

            print("🧾 لیست چاپ:")
            for item in self.print_list:
                print(item)

            self.frame_search_input.clear()
            self.table.setRowCount(0)

        except sqlite3.Error as e:
            print(f"خطا هنگام بروزرسانی پایگاه‌داده: {e}")

        # در داخل تابع مربوط به پرینت قرار بده:
        table_items = self.print_list
        try:
            sum_total = sum(float(p['total']) for p in table_items)
            factor_number = table_items[0].get("factor_number", "---") if table_items else "---"
            date = jdatetime.date.today().strftime("%Y/%m/%d")


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
                        padding: 10px;
                    }}
                    .container {{
                        text-align: center;
                        display: flex;
                        justify-content: center;
                        margin: 0 auto
                    }}
                    table {{
                        width: 100%;
                        margin: 8px 0;
                        margin-right: 70px;
                        border-collapse: collapse;
                        font-size: 14pt;
                    }}
                    thead tr {{
                        border-top: 1px dashed gray;
                        border-bottom: 1px solid gray;
                    }}
                    tbody tr {{
                        border-bottom: 1px solid gray;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: right;
                    }}
                    .border-dashed {{
                        font-weight: bold;
                        border-top: 1px dashed gray;
                        text-align: center;
                    }}
                    .total-row{{
                        border-top: 1px solid gray;
                        width: 20px;
                    }}
                    
                    h1 {{
                        text-align: center;
                        font-size: 24pt;
                        margin: 4px 0;
                    }}
                    .center {{
                        text-align: center;
                        font-size: 12pt;
                        font-family: Roboto, 'B Nazanin';
                        margin-bottom: 3px;
                    }}
                    .date-receipt {{
                        display: flex;
                        justify-content: space-between;
                        font-size: 14px;
                        font-family: Roboto, 'B Nazanin';
                        font-style: bold;
                        margin: 4px 0 8px 0;
                        width: 20%;
                    }}
                   
                    .discount-row{{
                        font-size: 10pt;
                        font-family: Roboto, 'B Nazanin';
                        font-weight: bold;
                        direction: rtl;
                    }}
                </style>
                </head>
                <body>
                <div class= container>
                <h1>فروشگاه تک </h1>
                <div class= "center"> {address} </div>
     

                <table>
                    <tr>
                        <td>{date} :تاریخ</td>
                        <td>{factor_number} :نمبر فاکتور</td>
                        
                    </tr>
                </table>

                <table>
                <thead cla>
                    <tr>
                        <th class="border-dashed">قیمت</th>
                        <th class="border-dashed">تعداد</th>
                        <th class="border-dashed">نام</th>          
                    </tr>
            """

            # اضافه کردن ردیف‌های محصول
            for product in table_items:
                name = product['name']
                product_type = product['type']
                numer = product['number']
                final = product['total']

                html += f"""
                <tbody>
                    <tr>
                        <td style="text-align: left;">{final:.2f}</td>
                        <td style="text-align: center;">{numer} {product_type} </td>
                        <td>{name}</td>
                    </tr>
                """

            # مجموع، تخفیف و پرداخت‌شده
            html += f"""
                <tr style="border-top: 1px solid gray;", colspan="4">
                    <th class="total-row",colspan="4",style="text-align: left;">{sum_total:.2f}</th>
                    <th class="total-row",colspan="4">مجموع کل</th>
                    
                </tr>
                <tr>
                    <td class="discount-row",style="text-align: left;">{-70:.2f}-</td>
                    <td class="discount-row">تخفیف</td>
                </tr>
                <tr style="border-top: 1px solid gray;", colspan="3">
                    <th >پرداخت شده</th>
                    <th style="text-align: left;">{final_total:.2f}</th>
                </tr>
                </tbody>
            </table>

            <div class="logo">
                <div>//</div>
                <div>AQSA</div>
                <span>GROUP</span>
            </div>

            </body>
            </html>
            """

            # چاپ
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print(printer)

            print("✅ فایل HTML ذخیره و توسط QPrinter چاپ شد.")

        except Exception as e:
            print(f"[⚠️ خطا در پرینت]: {e}")

    ##
    def syncs_to_server(self):
        db_data = Connection().get_connection()
        if not db_data:
            print("no online connection!")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data", "sh_online.db")

        if not os.path.exists(db_path):
            print("مسیر پایگاه‌داده یافت نشد")
            return

        try:
            # اتصال آفلاین
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()

            cursor_sq.execute('''
                SELECT
                    barcode,sale_date, sale_price, quantity,
                    discount, profit, total, user_id,sale_type
                FROM sale_factor
                WHERE sync=0
            ''')
            unsynced_products = cursor_sq.fetchall()

            cursor_online = db_data.cursor()
            for product in unsynced_products:
                (barcode,sale_date, sale_price, quantity,
                discount, profit, total, user_id,sale_type) = product

                cursor_online.execute('''
                    UPDATE sale_factor SET
                    sale_date=%s, sale_price=%s,quantity=%s,
                    discount=%s,profit=%s,total=%s
                    WHERE user_id=%s AND barcode=%s AND sale_type= %s
                ''', (sale_date, sale_price, quantity,
                    discount, profit, total, user_id,barcode,sale_type))
                ## update products
                cursor_sq.execute("UPDATE products SET is_synced=0 where barcode=?",(barcode,))
                print(f"✅ همگام‌سازی موفق بود{barcode}")

            db_data.commit()

            # بعد از موفقیت، جدول آفلاین را بروز کن
            
            cursor_sq.execute("UPDATE sale_factor SET sync = 1 WHERE sync = 0")
            conn_sq.commit()

            

        except Exception as e:
            print(f"❌ خطا در همگام‌سازی داده‌های آفلاین و آنلاین: {e}")
    ##
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            if any(line.hasFocus() for line in self.print_inputs):
                self.change_printer()
    ##
    def auto_sync(self):
        self.syc_timer= QTimer(self)
        self.syc_timer.timeout.connect(self.start_sync)
        self.syc_timer.start(12*1000)
    def start_sync(self):
        sync_thread= threading.Thread(target=self.syncs_to_server)
        sync_thread.setDaemon(True)
        sync_thread.start()

    ##

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

