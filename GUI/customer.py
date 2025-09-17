from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect,QTextEdit,QStyledItemDelegate, QSizePolicy,QScrollArea,QComboBox,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QPainterPath,QFontDatabase,QPixmap,QPen,QFont,QPainter
from PyQt6 import QtCore
from PyQt6.QtCharts import QChart, QChartView, QPieSeries
import sqlite3
import os
from db_connection import Connection
from reme import Customer_Pay
from reme_buy import Customer_Buy
from reme_sell import Customer_Sell

class Customer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.in_UI()
        self.load_all_fonts()
        self.lable_UI()
        self.Button_UI()
        self.table_UI()
        self.show_customers()
        self.synced_auto_timer()

    def in_UI(self):
        self.cust_widget= QStackedWidget()
        self.setCentralWidget(self.cust_widget)
        self.customer_page= QWidget()
        ##
        main_layout= QVBoxLayout(self.customer_page)
        top_layout= QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        ##
        self.top_label= QLabel("گزارش حساب مشتریان")
        back_layout= QHBoxLayout()
        self.back_btn= QPushButton()
        back_layout.addWidget(self.back_btn)
        ###
        top_layout.addLayout(back_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.top_label)
        ### middle page
        # لایه اصلی افقی
        middle_layout = QGridLayout()

        # ستون 0 → frame2 بالا و frame3 پایین
        middle_layout.addWidget(self.frame2(), 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        middle_layout.addWidget(self.frame3(), 1, 0)

        # ستون 1 → frame1
        middle_layout.addWidget(self.frame1(), 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignTop)

        
        

        ##
        main_layout.addSpacing(10)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addStretch()
        self.cust_widget.addWidget(self.customer_page)
    ##
    def frame1(self):
        frame1= QFrame()
        frame1.setStyleSheet("background-color: white; border-radius: 15px;")
        frame_layout= QVBoxLayout(frame1)
        frame_layout.setSpacing(5)
        ##
        top_layout= QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.man_lable= QLabel()
        self.customer_name= QLabel("")
        ##
        self.add_btn= QPushButton()
        self.add_btn.setContentsMargins(10,40,0,0)
        ##
        top_layout.addWidget(self.add_btn,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch(1)
        top_layout.addWidget(self.customer_name, alignment=(Qt.AlignmentFlag.AlignRight))
        top_layout.addWidget(self.man_lable, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight))
        frame_layout.addLayout(top_layout)
        ###
        box_layout= QHBoxLayout()
        ##
        self.customer_p= Customer_Pay()
        self.customer_b= Customer_Buy()
        self.customer_s= Customer_Sell()
        #
        box_layout.addWidget(self.customer_p)
        box_layout.addWidget(self.customer_b)
        box_layout.addWidget(self.customer_s)
        ###
        self.list_lb= QLabel("لیست مشتریان")
        ##
        table_layout= QHBoxLayout()
        self.customer_table= QTableWidget(0,4)
        table_layout.addWidget(self.customer_table,1)
        

        ###
        frame_layout.addLayout(box_layout)
        frame_layout.addSpacing(20)
        frame_layout.addWidget(self.list_lb,alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight))
        frame_layout.addLayout(table_layout)
        return frame1
    ##
    def frame2(self):
        frame = QFrame()
        frame.setMaximumWidth(300)
        frame.setStyleSheet("background-color: white; border-radius: 15px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(10)
        frame_layout.setContentsMargins(15, 15, 15, 15)

        # --- بخش بالا (عکس + اطلاعات کاربر) ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # عکس پروفایل دایره‌ای
        self.profile_label = QLabel()
        pixmap = QPixmap(self.get_asset_path("man_18663555.png"))
        self.profile_label.setPixmap(self.make_round_pixmap(pixmap, 60))  # تصویر دایره‌ای
        self.profile_label.setFixedSize(60, 60)
        self.profile_label.setScaledContents(True)
        top_layout.addWidget(self.profile_label, alignment=Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignRight)

        # اطلاعات کاربر
        info_layout = QVBoxLayout()
        self.name_label = QLabel("نامشخص")
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; font-family: B Nazanin;")

        self.phone_label = QLabel("بدون شماره تماس")
        self.phone_label.setStyleSheet("font-size: 15px; color: black; font-family: Roboto;")

        self.email_label = QLabel("gamail@example.com")
        self.email_label.setStyleSheet("font-size: 13px; color: gray; font-family: Roboto,'B Nazanin';")

        info_layout.addWidget(self.name_label,alignment=Qt.AlignmentFlag.AlignHCenter)
        info_layout.addWidget(self.phone_label,alignment=Qt.AlignmentFlag.AlignHCenter)
        info_layout.addWidget(self.email_label)

        top_layout.addLayout(info_layout)
        top_layout.addStretch()

        # --- بخش پایین (دکمه/Label سبز) ---
        self.green_btn = QLabel("حب نحلی")
        self.green_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_btn.setStyleSheet("""
            background-color: #E9FFF1;
            color: #00994d;
            font-size: 16px;
            font-family: B Nazanin;
            font-weight: bold;
            border-radius: 10px;
            padding: 6px 15px;
        """)

        # افزودن به لایه اصلی
        frame_layout.addLayout(top_layout)
        #frame_layout.addWidget(self.green_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return frame
    ##
    def frame3(self): 
        frame = QFrame()
        frame.setMaximumWidth(300)
        frame.setStyleSheet("background-color: white; border-radius: 15px;")
        frame_layout = QVBoxLayout(frame)

        # --- سری دایره (Donut) ---
        self.pie_series = QPieSeries()
        self.pie_series.setHoleSize(0.45)   # donut chart
        self.pie_series.append("قرض", 1)
        self.pie_series.append("پرداخت",1 )

        # تغییر رنگ هر Slice + نمایش لیبل
        slices = self.pie_series.slices()
        if len(slices) > 0:
            slices[0].setColor(QColor("#56B2E3"))  # آبی
            slices[0].setPen(QPen(Qt.PenStyle.NoPen))
            slices[0].setLabelVisible(True)
            slices[0].setLabelColor(Qt.GlobalColor.black)
            slices[0].setLabelFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        if len(slices) > 1:
            slices[1].setColor(QColor("#F28768"))  # سرخ
            slices[1].setPen(QPen(Qt.PenStyle.NoPen))
            slices[1].setLabelVisible(True)
            slices[1].setLabelColor(Qt.GlobalColor.black)
            slices[1].setLabelFont(QFont("B Nazanin", 12, QFont.Weight.Bold))

        # --- ساخت چارت ---
        chart = QChart()
        chart.addSeries(self.pie_series)
        chart.setTitle("وضعیت حساب")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.legend().setVisible(True)
        chart.legend().setFont(QFont("B Nazanin", 11))
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # فعال‌سازی انیمیشن
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        # --- ساخت ویو ---
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        frame_layout.addWidget(chart_view)
        return frame

    ##
    def lable_UI(self):
        self.top_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        self.customer_name.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: Roboto,'B Nazanin';
        ''')
        ##
        self.list_lb.setContentsMargins(10,10,10,10)
        self.list_lb.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: Roboto,'B Nazanin';
        
        ''')
        ##
        man_icon= QPixmap(self.get_asset_path("man_18663555.png"))
        self.man_lable.setPixmap(self.make_round_pixmap(man_icon,70))
        self.man_lable.setScaledContents(True)
        self.man_lable.setFixedSize(70,70)
    ##
    def Button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.open_reports)
        self.back_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.back_btn.setStyleSheet('''
        QPushButton{
            background-color: transparent;
            border-radius: 27px;
            padding: 5px;
                                    }
        QPushButton:hover{
            background-color: #f5f5f5;
                                    }
        QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            } 
        ''')
        ##
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.add_btn.setMaximumSize(150,45)
        self.add_btn.clicked.connect(self.open_form)
        self.add_btn.setText("افزودن مشتری")
        self.add_btn.setStyleSheet('''
            QPushButton {
                background-color: #2251DB;
                font-family: "B Nazanin";
                font-size: 15px;
                font-weight: bold;
                color: white;
                border-radius: 7px;
                text-align: center;
                padding: 5px;

            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        ''')
    ##
    def table_UI(self):
        self.customer_table.setHorizontalHeaderLabels(["کد مشتری","نام مشتری","شماره تماس","عملیات"])
        header=self.customer_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.customer_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.customer_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        for table in range(self.customer_table.columnCount()):
            if table == 4:  # ستون عملیات
                header.setSectionResizeMode(table, QHeaderView.ResizeMode.Fixed)
                self.customer_table.setColumnWidth(table, 60)
            else:
                header.setSectionResizeMode(table, QHeaderView.ResizeMode.Stretch)

        #
        self.customer_table.setStyleSheet('''
            QTableWidget {
                border:None;
                font-family: Roboto,'B Nazanin';
                font-size: 15px;
                color: black;
                border-radius: 12px;
                gridline-color: transparent; /* حذف خطوط داخلی */
                alternate-background-color: #f5f5f5; /* رنگ ردیف‌های زوج */
                background-color: #ffffff;          /* رنگ ردیف‌های فرد */
            }
            QTableWidget::item {
                border-bottom: 1px solid #d8e6e3;      
                padding: 8px;      
            }
            QTableWidget::item:selected {
                background: transparent;  /* حذف رنگ انتخاب */
                color: black;
            }
            QHeaderView::section {
                background-color: transparent; 
                color: black;
                font-family: 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
                padding: 5px;
                border-top: 1px solid #d8e6e3;
                border-bottom: 1px solid #d8e6e3;  
            }
            QHeaderView::section:first {
                border-top-left-radius: 0px; 
            }
            QHeaderView::section:last {
                border-top-right-radius: 0px;  
            }
            QScrollBar:vertical {
                background: #eee;
                width: 10px;
                margin: 4px 0 4px 0;
                border-radius: 0px;
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
        ''')


    ##
    def make_round_pixmap(self,pixmap: QPixmap, size: int = 50) -> QPixmap:
        # تغییر اندازه
        pixmap = pixmap.scaled(
                size, size, 
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)

        # ماسک دایره‌ای
        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded
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
    ###
    def open_reports(self):
        from finance import Money
        self.finace= Money()
        self.cust_widget.addWidget(self.finace)
        self.cust_widget.setCurrentWidget(self.finace)
        
        ##animation:
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.finace.move(start_pos)
        ##
        animation= QPropertyAnimation(self.finace, b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    ##
    def open_form(self):
        from customer_info import Customer_Form
        form= Customer_Form(customer_page=self)
        form.exec()
    ##
    def showEvent(self, event):
        self.show_customers()
        return super().showEvent(event)
    ##
    def synced_auto_timer(self):
        from sync_customer import CustomerThread
        self.customer_thread= CustomerThread()
        self.customer_thread.start()
    
        if hasattr(self, 'synced_timer'):
            self.synced_timer= QTimer(self)
            self.synced_timer.timeout.connect(self.synced_auto_timer)
            self.synced_timer.start(30 *1000)
    ##
    def show_customers(self):
        self.customer_table.setRowCount(0)
        self.customer_table.setShowGrid(True)

        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            print(f'{db_path}: not found in select action')
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user= cursor.fetchone()[0]
            cursor.execute("select id,name,last_name,phone from customers where user_id=?",(id_user,))
            result= cursor.fetchall()
            if result:
                for id_e,name,last_name,phone in result:
                    full_name= f"{name} {last_name}"
                    row= self.customer_table.rowCount()
                    self.customer_table.insertRow(row)
                    self.customer_table.setItem(row,0,QTableWidgetItem(self._make_cell(str(id_e))))
                    self.customer_table.setItem(row,1,QTableWidgetItem(self._make_cell(full_name)))
                    self.customer_table.setItem(row,2,QTableWidgetItem(self._make_cell(str(phone))))
                    # === دکمه ویرایش ===
                    edit_btn = QPushButton()
                    edit_btn.setIcon(QIcon(self.get_asset_path("edit_2122.png")))
                    edit_btn.setIconSize(QtCore.QSize(20, 20))
                    edit_btn.setFixedSize(28, 28)   # اندازه ثابت دکمه
                    edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    edit_btn.clicked.connect(lambda _, r=row: self.select_info(r))
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            border: none;
                            background-color: transparent;
                        }
                        QPushButton:hover {
                            background-color: #eaeaea;
                            border-radius: 10px;
                        }
                        QPushButton::Pressed{
                            background-color: white;
                            border-radius: 10px;
                                           }
                    """)
                    
                    ##
                    denied_btn = QPushButton()
                    denied_icon = QIcon(self.get_asset_path("Trash Can.png"))
                    denied_btn.setIcon(denied_icon)
                    denied_btn.setIconSize(QtCore.QSize(25, 25))
                    denied_btn.setStyleSheet('''
                        QPushButton {
                            border: none;
                            background-color: transparent;
                        }
                        QPushButton:hover {
                            background-color: #eaeaea;
                            border-radius: 7px;
                        }
                        QPushButton::Pressed{
                            background-color: white;
                            border-radius: 7px;
                                           }
                    ''')
                    # === ویجت حاوی دکمه ===
                    btn_widget = QWidget()
                    btn_widget.setStyleSheet("background-color: transparent;")
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.addWidget(denied_btn)
                    btn_layout.addWidget(edit_btn)
                    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # وسط‌چین
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    self.customer_table.setCellWidget(row,3,btn_widget)
                    self.customer_table.setRowHeight(row,50)


        except sqlite3.Error as e:
            print(f"searching data problem:{e}")
    ##
    def select_info(self,row):
        id_e = self.customer_table.item(row,0).text()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no db file found in select_info function")
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            ##
            cursor.execute("select SUM(amount) as total_barrow from barrow WHERE cus_id=? AND type='برده گی' OR  type='طلب مردم' ",(id_e,))
            b_result = cursor.fetchone()
            ##
            cursor.execute("SELECT SUM(amount) as total_deposit from barrow where cus_id=? AND type='رسیده گی' ",(id_e,))
            r_result = cursor.fetchone()
            ##
            cursor.execute("select name,phone,email,last_name from customers where id=?",(id_e,))
            info_result = cursor.fetchone()
            ##
            b_total = b_result[0] if b_result and b_result[0] is not None else 0
            r_total = r_result[0] if r_result and r_result[0] is not None else 0

            if info_result:
                name = info_result[0]
                last = info_result[3]
                full_name = f'{name} {last}'
                self.name_label.setText(full_name)
                self.customer_name.setText(full_name)
                self.phone_label.setText(str(info_result[1]))
                self.email_label.setText(info_result[2])
            else:
                self.name_label.setText("نامشخص")
                self.customer_name.setText("")
                self.phone_label.setText("بدون شماره تماس")
                self.email_label.setText("بدون ایمیل آدرس")

            # ارسال به UI
            if b_total.is_integer() and r_total.is_integer():
                b_total = int(b_total)
                r_total = int(r_total)

            self.customer_b.set_product_info(number=b_total)
            self.customer_s.set_product_info(number=r_total)

            # --- آپدیت Pie Chart ---
            self.pie_series.clear()

            if b_total == 0 and r_total == 0:
                # حالت بدون داده
                self.pie_series.append("بدون داده", 1)
                slice0 = self.pie_series.slices()[0]
                slice0.setColor(QColor("#CCCCCC"))   # خاکستری
                slice0.setPen(QPen(Qt.PenStyle.NoPen))
                slice0.setLabelVisible(True)
                slice0.setLabelColor(Qt.GlobalColor.black)
                slice0.setLabelFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
            else:
                # حالت نرمال
                self.pie_series.append("قرض", b_total)
                self.pie_series.append("پرداخت", r_total)

                slices = self.pie_series.slices()
                if len(slices) > 0:
                    slices[0].setColor(QColor("#56B2E3"))  # آبی
                    slices[0].setPen(QPen(Qt.PenStyle.NoPen))
                    slices[0].setLabelVisible(True)
                    slices[0].setLabelColor(Qt.GlobalColor.black)
                    slices[0].setLabelFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
                if len(slices) > 1:
                    slices[1].setColor(QColor("#F28768"))  # نارنجی-سرخ
                    slices[1].setPen(QPen(Qt.PenStyle.NoPen))
                    slices[1].setLabelVisible(True)
                    slices[1].setLabelColor(Qt.GlobalColor.black)
                    slices[1].setLabelFont(QFont("B Nazanin", 12, QFont.Weight.Bold))

        except sqlite3.Error as e:
            print(f"db problem: {e}")


    ##
    def _make_cell(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.black)
        return item