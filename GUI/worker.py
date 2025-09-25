from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect,QTextEdit,QStyledItemDelegate, QSizePolicy,QScrollArea,QComboBox,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QPainterPath,QFontDatabase,QPixmap,QPen,QFont,QPainter
from PyQt6 import QtCore
from PyQt6.QtCharts import QChart, QChartView, QPieSeries
import sqlite3
import os

class Worker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_all_fonts()
        self.In_UI()
        self.Button_UI()
        self.Label_UI()
        self.Input_UI()
        self.table_View()
        self.syce_to_server()
    
    def In_UI(self):
        self.worker_stack= QStackedWidget()
        self.setCentralWidget(self.worker_stack)
        self.worker_page= QWidget()
        ##
        self.main_layout= QVBoxLayout(self.worker_page)
        ##
        self.top_page= QHBoxLayout()
        self.top_title= QLabel("گزارش کارمندان")
        self.top_page.setAlignment(Qt.AlignmentFlag.AlignTop)
        ##
        self.back_btn= QPushButton()
        back_layout= QHBoxLayout()
        back_layout.addWidget(self.back_btn)
        ##top
        self.top_page.addLayout(back_layout)
        self.top_page.addStretch(2)
        self.top_page.addWidget(self.top_title)
        ##middle
        self.middle_layout= QVBoxLayout()
        self.middle_layout.addWidget(self.create_main_frame(),3)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        ###
        self.main_layout.addLayout(self.top_page)
        self.main_layout.addLayout(self.middle_layout)
        ###
        self.worker_stack.addWidget(self.worker_page)
    ##
    def create_main_frame(self):
        frame = QFrame()
        frame.setMaximumHeight(900)
        frame.setStyleSheet("background-color: white; border-radius: 12px;")
        frame_layout = QVBoxLayout(frame)

        ## --- بالای صفحه
        top_frame = QHBoxLayout()
        self.top_lable = QLabel("مدیریت کارمندان")
        top_frame.addWidget(self.top_lable)
        top_frame.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        ## --- دکمه‌ها
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن کارمندان")
        self.renew_btn = QPushButton("اجرای معاش کارمندان")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.renew_btn)
        # تغییر این خط:
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        ##
        self.table=QTableWidget()

        ## --- اضافه کردن به لایه اصلی
        frame_layout.setSpacing(10)
        frame_layout.addLayout(top_frame)
        frame_layout.addLayout(btn_layout)
        frame_layout.addWidget(self.table,3,alignment=Qt.AlignmentFlag.AlignTop)

        return frame
    ##
    def Button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.open_finance)
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
        plus_icon= QIcon(self.get_asset_path("Plus Math.png"))
        self.add_btn.setIcon(plus_icon)
        self.add_btn.setText("افزدون کارمند")
        self.add_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.add_btn.setIconSize(QtCore.QSize(25,25))
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.add_btn.clicked.connect(self.open_form)
        self.add_btn.setStyleSheet('''
            QPushButton{
                background-color: #2251DB;
                font-family: Vazir;
                font-size: 15px;
                color: white;
                border-radius: 7px;
                padding: 5px;
                padding-left: 10px;
                margin-right:5px;
                                   }
                QPushButton:hover{
                        background-color: #498bf5;
                                   }
                QPushButton:pressed {
                    background-color: #2251DB;
                }
            ''')
        ##
        self.renew_btn.setText("اجراء معاش کارمندان")
        self.renew_btn.setIcon(plus_icon)
        self.renew_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.renew_btn.setIconSize(QtCore.QSize(25,25))
        self.renew_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.renew_btn.clicked.connect(self.open_salary)
        self.renew_btn.setStyleSheet('''
            QPushButton{
                background-color: #2251DB;
                font-family: Vazir;
                font-size: 15px;
                color: white;
                border-radius: 7px;
                text-align: center;
                padding: 5px;
                padding-left: 10px;
                margin-right:5px;
                                   }
                QPushButton:hover{
                        background-color: #498bf5;
                                   }
                QPushButton:pressed {
                    background-color: #2251DB;
                }
            ''')
         
    ##
    def Label_UI(self):
        self.top_title.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        self.top_lable.setStyleSheet('''
            font-size: 18px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
    ##
    def Input_UI(self):
        pass
    ##
    def table_View(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["آیدی","نام کارمند","راه ارتباطی","موقف کاری","وضعیت معاش","معاش کارمند","عملیه ها"])
        header= self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        ## column size arrange
        for i in range(self.table.columnCount()):
            if i== 7:
                header.setSectionResizeMode(i,QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(i,60)
            else:
                header.setSectionResizeMode(i,QHeaderView.ResizeMode.Stretch)
        ##
        self.table.setStyleSheet("""
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
                padding: 5px;
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
    ##
    def open_finance(self):
        from finance import Money
        self.finance= Money()
        self.worker_stack.addWidget(self.finance)
        self.worker_stack.setCurrentWidget(self.finance)
        ##
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.finance.move(start_pos)
        ##
        animation= QPropertyAnimation(self.finance,b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    ##fuctoions
    def open_form(self):
        from worker_info import Worker_Form
        self.worker= Worker_Form(worker_page=self)
        self.worker.exec()
    ##
    def show_wk_info(self):
        status_salary= None
        self.table.setRowCount(0)
        self.table.setShowGrid(True)
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no db worker found")
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user = cursor.fetchone()[0]

            cursor.execute('''
                SELECT employee_id,
                    first_name || ' ' || last_name as full_name,
                    phone, email, position, salary
                FROM employees
                WHERE user_id=?
            ''', (id_user,))
            result = cursor.fetchall()

            if result:
                for id_m, full_name, phone, email, position, salary in result:
                    # ---- شرط salary ----
                    if salary == 0:
                        status_salary = "اجراء شده"
                    elif salary > 0:
                        status_salary = "طلب کار"
                    else:
                        status_salary = "بدهکار"

                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(self._make_cell(str(id_m))))
                    self.table.setItem(row, 1, QTableWidgetItem(self._make_cell(full_name)))

                    # ---- شرط شماره تماس یا ایمیل ----
                    if phone and phone.strip():  # اگر شماره تماس موجود بود
                        contact_info = phone
                    else:  # اگر شماره تماس خالی بود
                        contact_info = email
                    ## salary int
                    if salary.is_integer():
                        salary=int(salary)
                    else:
                        salary=salary

                    self.table.setItem(row, 2, QTableWidgetItem(self._make_cell(contact_info)))
                    self.table.setItem(row, 3, QTableWidgetItem(self._make_cell(position)))
                    #
                    self.table.setItem(row, 4, QTableWidgetItem(self._make_cell(status_salary)))
                    self.table.setItem(row, 5, QTableWidgetItem(self._make_cell(str(salary))))

                    # === دکمه ویرایش ===
                    edit_btn = QPushButton()
                    edit_btn.setIcon(QIcon(self.get_asset_path("edit_2122.png")))
                    edit_btn.setIconSize(QtCore.QSize(20, 20))
                    edit_btn.setFixedSize(28, 28)
                    edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    edit_btn.clicked.connect(lambda _, r=row: self.add_info(r))
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

                    # === دکمه حذف ===
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
                    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    btn_layout.setContentsMargins(0, 0, 0, 0)

                    self.table.setCellWidget(row, 6, btn_widget)
                    self.table.setRowHeight(row, 50)

        except sqlite3.Error as e:
            print(f"worker db problem:{e}")

    #for cneter info in the table
    def _make_cell(self, text):
        item= QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.black)
        return item
    ##
    def syce_to_server(self):
        from sync_worker import WorkerThread
        self.work= WorkerThread()
        self.work.start()

        if hasattr(self,'synced_timer'):
            self.synced_timer= QTimer(self)
            self.synced_timer.timeout.connect(self.syce_to_server)
            self.synced_timer.start(30*1000)

    ##events
    def showEvent(self, event):
        self.show_wk_info()
        return super().showEvent(event)
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
    ##
    def open_salary(self):
        from worker_salary import Worker_Salary
        self.worker_salary= Worker_Salary()
        self.worker_salary.exec()
    ##
    def add_info(self, row):
        from worker_salary import Worker_Salary

        amount_item = self.table.item(row, 5)
        name_item = self.table.item(row, 1)

        if not amount_item or not name_item:
            print(f"⚠ سلول خالی یا یافت نشد (row={row})")
            return

        amount = amount_item.text()
        name = name_item.text()

        work = Worker_Salary(self)
        work.set_info(quantity=amount, name=name)
        work.exec()

