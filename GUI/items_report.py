from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout,QPushButton,
    QGraphicsDropShadowEffect, QFileDialog,QStyledItemDelegate,QSizePolicy,QAbstractItemView,QWidget,QComboBox,QTableWidgetItem,QTableWidget,QHeaderView)
from PyQt6.QtGui import QPalette,QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QDate,QPoint,QPropertyAnimation,QEasingCurve,QTimer
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os
from fpdf import FPDF
import jdatetime
from item_thread import ItemThread
from circle import CircularSpinner
from spitial_calendar import JalaliCalendar

class BlackTextDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor("black"))
        editor.setPalette(palette)
        return editor
class ItemReport(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_buttons=[]
        self.val_sale={}
        self.val_buy={}
        self.selected_month= None
        self.selected_date= None

        self.in_UI()
        self.label()
        self.Button_UI()
        self.table_UI()
        self.load_all_fonts()
        self.show_first_spinner()
    
    def in_UI(self):
        self.item_stack= QStackedWidget()
        self.setCentralWidget(self.item_stack)
        self.item_page= QWidget()
        ##
        self.main_layout= QVBoxLayout(self.item_page)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ###
        top_layout= QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ###
        self.page_lable= QLabel("گزارشات محصولات")
        self.page_lable.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Fixed)
        ##
        title_layout= QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        title_layout.addWidget(self.page_lable)
        ##
        back_layout= QHBoxLayout()
        self.back_btn= QPushButton()
        back_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        back_layout.addWidget(self.back_btn)
        ####
        top_layout.addLayout(back_layout)
        top_layout.addStretch()
        top_layout.addLayout(title_layout)
        ##tabe_frames:
        middle_layout= QHBoxLayout()
        tab_frame= QFrame()
        tab_frame.setStyleSheet("background-color: #c7c9c8; border-radius:10px;")
        tab_layout= QHBoxLayout(tab_frame)
        tab_frame.setFixedSize(300,50)

        ###middle_items:
        middle_layout.addWidget(tab_frame,alignment=Qt.AlignmentFlag.AlignHCenter)

        ###frames:
        self.sale_frame= QFrame()
        self.sale_layout= QVBoxLayout(self.sale_frame)
        ##
        self.buy_frame= QFrame()
        self.buy_layout= QVBoxLayout(self.buy_frame)
        ###stat_boxes:
        stat_layout_sale= QHBoxLayout(self.sale_frame)
        sale_stats= [
            ("تعداد محصولات فروخته شده (آنلاین) ","online_sale"),
            ("تعداد محصولات فروخته شده (حضوری)", "offline_sale"),
            ("پر فروش ترین محصول","best_item")
        ]
        for title,key in sale_stats:
            box = QFrame()
            box.setStyleSheet('''
                QFrame {
                    background: white;
                    border-radius: 10px;
                    color: black;
                    font-family: B Nazanin;
                    font-weight: bold;
                    padding: 5px;
                }
                QLabel {
                    font-size: 14px;
                    margin: 4px;
                }
            ''')
            box_layout= QVBoxLayout(box)
            shadow= QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0,0,0,70))
            box.setGraphicsEffect(shadow)
            #box labels:
            top_title= QLabel(title)
            top_title.setStyleSheet('''
                color: black;
                font-family: Mirza, 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
            ''')
            top_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            box_layout.addWidget(top_title)
            ##value
            val_label= QLabel("")
            val_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_label.setStyleSheet('''
                font-weight: bold;
                font-size: 14px;
                font-family: Arial, "B Nazanin";
            ''')
            box_layout.addWidget(val_label)
            ###key value
            self.val_sale[key]= val_label
            stat_layout_sale.addWidget(box)
        
        ###buy_boxes:
        stat_layout_buy= QHBoxLayout(self.buy_frame)
        buy_stats= [
            ("تعداد محصولات خریداری شده" , "buy_items"),
            ("تعداد محصولات تمام شده" , "low_items"),
            ("تکراری ترین خرید" , "repeated_items"),
            ("محصولات تاریخ گذشته", "expired_items")
        ]
        for titel ,keys in buy_stats:
            buy_box= QFrame()
            buy_box.setStyleSheet('''
                QFrame {
                    background: white;
                    border-radius: 10px;
                    color: black;
                    font-family: B Nazanin;
                    font-weight: bold;
                    padding: 5px;
                }
                QLabel {
                    font-size: 14px;
                    margin: 4px;
                }
            ''')
            buy_box_layout= QVBoxLayout(buy_box)

            shadow= QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0,0,0,70))
            buy_box.setGraphicsEffect(shadow)
            ##
            title_show= QLabel(titel)
            title_show.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            title_show.setStyleSheet('''
                color: black;
                font-family: Mirza, 'B Nazanin';
                font-size: 15px;
                font-weight: bold;  
            ''')
            buy_box_layout.addWidget(title_show)
            ##
            buy_label= QLabel("")
            buy_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            buy_label.setStyleSheet('''
                font-weight: bold;
                font-size: 15px;
                font-family: Arial,"B Nazanin";
                ''')
            buy_box_layout.addWidget(buy_label)
            ##
            self.val_buy[keys]= buy_label
            stat_layout_buy.addWidget(buy_box)
        ###tab buttons:
        self.sale_button= QPushButton()
        self.buy_button= QPushButton()
        ## month
        btn_layout= QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignRight)
        self.month_combo= QComboBox()
        self.calendar_btn= QPushButton()
        ##
        btn_layout.addWidget(self.calendar_btn)
        btn_layout.addWidget(self.month_combo)
        
        ##
        self.tab_frames= {
            self.sale_button: self.sale_frame,
            self.buy_button : self.buy_frame
        }
        for btn in (self.sale_button,self.buy_button):
            btn.setStyleSheet('''
                QPushButton {
                    padding: 6px 18px;
                    font-size: 16px;
                    background-color: transparent;
                    color: black;
                    font-family: B Nazanin, "Mirza";
                }
                QPushButton:hover {
                    background-color: #d0d6d5;
                }
            ''')
            btn.clicked.connect(lambda checked, b= btn: self.handle_tab_buttons(b))
            self.tab_buttons.append(btn)
            tab_layout.addWidget(btn)
        ##
        self.handle_tab_buttons(self.sale_button)
        ###tables:
        self.sale_table= QTableWidget()
        self.buy_table= QTableWidget()
        #button pdf
        self.pdf_btn= QPushButton()
        self.pdf_btns= QPushButton()
        ##hide bag frames
        self.sale_container= QVBoxLayout()
        self.sale_container.addWidget(self.sale_frame)
        self.sale_layout.addLayout(stat_layout_sale)
        self.sale_layout.addWidget(self.sale_table)
        self.sale_layout.addWidget(self.pdf_btn)

        self.buy_container= QVBoxLayout()
        self.buy_container.addWidget(self.buy_frame)
        self.buy_layout.addLayout(stat_layout_buy)
        self.buy_layout.addWidget(self.buy_table)
        self.buy_layout.addWidget(self.pdf_btns)
        ###hide for layout:
        self.info_layout= QVBoxLayout()
        self.info_layout.setSpacing(7)
        self.info_layout.addLayout(btn_layout)
        self.info_layout.addLayout(self.sale_container)
        self.info_layout.addLayout(self.buy_container)
        ####
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(middle_layout)
        #main_layout.addLayout(self.info_layout)
        ##
        self.item_stack.addWidget(self.item_page)
        
    ##
    def label(self):
        self.page_lable.setMinimumSize(200,30)
        self.page_lable.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;

        ''')
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
        ''')
        ##text tab buttons:
        self.sale_button.setText("فروش")
        self.buy_button.setText("خرید")
        ##
        self.month_combo.setMaximumWidth(150)
        self.month_combo.setStyleSheet('''
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
                padding-left: 50px;
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
        self.month_index=["حمل","ثور","جوزا","سرطان","اسد",
                          "سنبله","میزان","عقرب","قوس","جدی","دلو","حوت"]
        self.month_combo.addItems(self.month_index)
        self.month_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        ## defualt_current_month:
        today= jdatetime.date.today()
        self.month_combo.setCurrentIndex(today.month -1)
        self.month_combo.currentIndexChanged.connect(self.handle_month_change)
        ##
        self.cale_icon= QIcon(self.get_asset_path("calendar_8265298.png"))
        self.calendar_btn.setIcon(self.cale_icon)
        self.calendar_btn.setIconSize(QtCore.QSize(30,30))
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                padding: 10px;
                border-radius: 12px; /* گردی برای همه حالت‌ها */
                }
            QPushButton:hover {
                background-color: #f5f5f5;
                }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
                }
        ''')
        self.calendar_btn.clicked.connect(self.show_calendar)
        ##
        self.pdf_btn.setMaximumSize(110,40)
        self.pdf_btn.setMinimumSize(90,20)
        self.pdf_btn.clicked.connect(self.export_sale_table_pdf_fpdf)
        self.pdf_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Maximum)
        pdf_icon= QIcon(self.get_asset_path("pdf_9496432.png"))
        self.pdf_btn.setIcon(pdf_icon)
        self.pdf_btn.setIconSize(QtCore.QSize(25,25))
        self.pdf_btn.setText("ساخت")
        self.pdf_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                color: black;
                font-family: Mirza;
                font-size: 15px;
                font-weight: bold;
                border-radius: 15px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: white;  /* خاکستری ملایم هنگام کلیک */
            }
            ''')
        shadow= QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1,4)
        shadow.setColor(QColor(0,0,0,70))
        self.pdf_btn.setGraphicsEffect(shadow)
        ##
        self.pdf_btns.setMaximumSize(110,40)
        self.pdf_btns.setMinimumSize(90,20)
        self.pdf_btns.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Maximum)
        self.pdf_btns.setIcon(pdf_icon)
        self.pdf_btns.setIconSize(QtCore.QSize(25,25))
        self.pdf_btns.setText("ساخت")
        self.pdf_btns.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                color: black;
                font-family: Mirza;
                font-size: 15px;
                font-weight: bold;
                border-radius: 15px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: white;  /* خاکستری ملایم هنگام کلیک */
            }
            ''')
        shadows= QGraphicsDropShadowEffect()
        shadows.setBlurRadius(15)
        shadows.setOffset(1,4)
        shadows.setColor(QColor(0,0,0,70))
        self.pdf_btns.setGraphicsEffect(shadows)
        
    ##
    def table_UI(self):
        self.sale_table.setColumnCount(4)
        self.sale_table.setHorizontalHeaderLabels(["نام محصول","تعداد محصول","واحد","قیمت کل"])
        self.sale_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.sale_table.verticalHeader().setVisible(False)
        #self.sale_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.sale_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sale_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.sale_table.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        #header:
        header= self.sale_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        ##reszie mode:
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        #style:
        self.sale_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
                gridline-color: black;
            }
            QHeaderView::section {
                background-color: transparent;
                border: 1px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;
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
        ##color class:
        self.sale_table.setItemDelegate(BlackTextDelegate())
        
        ### buy table
        self.buy_table.setColumnCount(4)
        self.buy_table.setHorizontalHeaderLabels(["نام محصول","تعداد محصول","واحد","قیمت کل"])
        self.buy_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.buy_table.verticalHeader().setVisible(False)
        self.buy_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.buy_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.buy_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.buy_table.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        #header:
        header= self.buy_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        ##reszie mode:
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        #style:
        self.buy_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
                gridline-color: black;
            }
            QHeaderView::section {
                background-color: transparent;
                border: 1px solid black;
                color: black;
                font-family: B Nazanin;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;
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
        ##color class:
        self.buy_table.setItemDelegate(BlackTextDelegate())

    ##
    def open_reports(self):
            from finance import Money
            self.finace= Money()
            self.item_stack.addWidget(self.finace)
            self.item_stack.setCurrentWidget(self.finace)
            self.finace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            
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
    ####all back_end fucntions:
    def handle_tab_buttons(self,clicked_btn):
        for btn in self.tab_buttons:
            btn.setStyleSheet('''
                QPushButton {
                    padding: 6px 18px;
                    font-size: 16px;
                    background-color: transparent;
                    color: black;
                    font-family: B Nazanin, "Mirza";
                }
                QPushButton:hover {
                    background-color: #d0d6d5;
                }
            ''')
        clicked_btn.setStyleSheet('''
            QPushButton {
                padding: 6px 18px;
                font-size: 16px;
                background-color: white;
                color: black;
                font-family: B Nazanin, "Mirza";
                font-weight: bold;
            }
        ''')

        ##btn frames:
        for btn,frame in self.tab_frames.items():
            frame.setVisible(btn== clicked_btn)
    ##
    def show_calendar(self):
        self.calendar_popup = JalaliCalendar(self)
        self.calendar_popup.adjustSize()  # تا عرض تقویم درست تنظیم شود
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomLeft())
        pos.setX(pos.x() - self.calendar_popup.width())  # انتقال به چپ
        self.calendar_popup.date_selected.connect(self.handle_selected_date)
        self.calendar_popup.show_with_animation(pos)

    ###thread:
    def show_first_spinner(self):
        self.hide_run_layout_widgets()  # ← اول مخفی کن
        self.show_spinner_and_load_data()
    ##
    def show_spinner_and_load_data(self):
        if not hasattr(self, "run_layout_widget"):
            # فقط یک‌بار ایجاد شود
            self.run_layout_widget = QWidget()
            self.main_layout.addWidget(self.run_layout_widget)

            # لایه اصلی کاور
            self.wrapper_layout = QVBoxLayout(self.run_layout_widget)

            # ویجت spinner
            self.spinner_wrapper = QWidget()
            spinner_layout = QVBoxLayout(self.spinner_wrapper)
            spinner_layout.setContentsMargins(0, 100, 0, 100)
            spinner_layout.addStretch()

            self.spinner = CircularSpinner(self)
            spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
            spinner_layout.addStretch()

            self.wrapper_layout.addWidget(self.spinner_wrapper)

            # محتوای اصلی برنامه (ابتدا پنهان)
            self.run_layout_holder = QWidget()
            self.run_layout_holder.setVisible(False)
            self.run_layout_holder.setLayout(self.info_layout)
            self.wrapper_layout.addWidget(self.run_layout_holder)
        else:
            # اگر spinner حذف شده بود (بعد از بارگذاری)، دوباره بساز
            if self.spinner_wrapper is None or self.spinner_wrapper.isHidden():
                self.spinner_wrapper = QWidget()
                spinner_layout = QVBoxLayout(self.spinner_wrapper)
                spinner_layout.setContentsMargins(0, 100, 0, 100)
                spinner_layout.addStretch()

                self.spinner = CircularSpinner(self)
                spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
                spinner_layout.addStretch()

                self.wrapper_layout.insertWidget(0, self.spinner_wrapper)

            self.spinner_wrapper.setVisible(True)
            self.run_layout_holder.setVisible(False)

        QTimer.singleShot(0, self.defer_start_thread)
    ##
    def defer_start_thread(self):
        self.start_thread(year_month=self.selected_month, full_date=self.selected_date)

    ##
    def start_thread(self, year_month: str = None, full_date: str = None):
        if full_date:
            # فقط اطلاعات روزانه را بارگذاری کن
            self.item_thread = ItemThread(selected_month=None, selected_date=full_date)
        elif year_month:
            # فقط اطلاعات ماهانه را بارگذاری کن
            self.item_thread = ItemThread(selected_month=year_month, selected_date=None)
        else:
            # پیش‌فرض: بارگذاری ماه جاری
            jdate = jdatetime.date.today()
            year_month = f"{jdate.year}/{jdate.month:02d}"
            self.item_thread = ItemThread(selected_month=year_month, selected_date=None)
        ##boxes
        self.item_thread.sale_box_signal.connect(self.sale_box)
        self.item_thread.buy_box_signal.connect(self.buy_boxes)
        ##day
        self.item_thread.day_sale_signal.connect(self.sale_box)
        self.item_thread.day_buy_signal.connect(self.buy_boxes)
        ##tables_m
        self.item_thread.sale_table_data.connect(self.sale_table_info)
        self.item_thread.buy_table_data.connect(self.buy_table_info)
        ##day
        self.item_thread.sale_table_data_day.connect(self.sale_table_info)
        self.item_thread.buy_table_data_day.connect(self.buy_table_info)
        
        self.item_thread.finished.connect(self.on_data_loaded)
        self.item_thread.start()
    ##
    def on_data_loaded(self):
        if self.spinner_wrapper:
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None  # ← برای بررسی بعدی
        self.run_layout_holder.setVisible(True)
    ##
    def hide_run_layout_widgets(self):
        for i in range(self.info_layout.count()):
            item = self.info_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setVisible(False)
    ##
    def sale_box(self, sale_stats: dict):
        for key,value in sale_stats.items():
            if key in self.val_sale:
                self.val_sale[key].setText(f'{value}')
    ##
    def buy_boxes(self,buy_satic: dict):
        for key, value in buy_satic.items():
            if key in self.val_buy:
                self.val_buy[key].setText(f"{value}")
    ##month select
    def set_selected_month(self, year_month: str):
        if self.selected_month != year_month:
            self.selected_month = year_month
            self.selected_date = None  # 🟢 پاک کردن تاریخ قبلی برای جلوگیری از اجرای گزارش روز
            print(f"📌 ماه انتخاب‌شده جدید: {self.selected_month}")
            self.show_first_spinner()
    ##
    def handle_selected_date(self, date_str: str):
        print(f"📅 تاریخ انتخاب‌شده: {date_str}")
        self.selected_date = date_str
        #self.selected_month = None  # مهم! ماه را پاک کن تا فقط اطلاعات روزانه اجرا شود
        self.show_first_spinner()   # نمایش spinner و اجرای thread

    def handle_month_change(self, index):
        today = jdatetime.date.today()
        current_year = today.year
        selected_text = self.month_combo.itemText(index)

        if self.sale_button.styleSheet().find("background-color: white") != -1:
            month_number = index + 1
            formatted_month = f"{current_year}/{month_number:02d}"
            print(f"📆 انتخاب کاربر از کمبو: {formatted_month}")
            self.set_selected_month(formatted_month)
        elif self.buy_button.styleSheet().find("background-color: white") != -1:
            month_number = index + 1
            formatted_month = f"{current_year}/{month_number:02d}"
            print(f"📆 انتخاب کاربر از کمبو: {formatted_month}")
            self.set_selected_month(formatted_month)
    ##
    def sale_table_info(self, data : dict):
        self.sale_table.setRowCount(0)
        for row_index,values in data.items():
            self.sale_table.insertRow(row_index)
            for col_index,value in enumerate(values):
                item= QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.sale_table.setItem(row_index,col_index,item)   
    ##
    def buy_table_info(self, info: dict):
        self.buy_table.setRowCount(0)
        for row_index, values in info.items():
            self.buy_table.insertRow(row_index)
            for column_index, value in enumerate(values):
                items= QTableWidgetItem(str(value))
                items.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.buy_table.setItem(row_index,column_index,items)
    ##
    def export_sale_table_pdf_fpdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ذخیره گزارش فروش به صورت PDF",
            "گزارش_فروش.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            print("❌ ذخیره لغو شد.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # 📁 فونت پیشنهادی: Shabnam یا نسخه سالم BNazanin
        font_file = "BNazanin.ttf"  # یا "Shabnam.ttf"
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", font_file)

        use_farsi_font = False
        if os.path.exists(font_path):
            try:
                pdf.add_font("Persian", "", font_path, uni=True)
                pdf.set_font("Persian", size=16)
                use_farsi_font = True
            except Exception as e:
                print(f"⚠️ خطا در افزودن فونت: {e}")
                pdf.set_font("Arial", size=16)
        else:
            print("⚠️ فونت پیدا نشد، استفاده از Arial")
            pdf.set_font("Arial", size=16)

        today = jdatetime.date.today().strftime("%Y/%m/%d")
        pdf.cell(200, 10, txt="📄 گزارش فروش", ln=True, align='C')
        pdf.set_font("Persian" if use_farsi_font else "Arial", size=12)
        pdf.cell(200, 10, txt=f"تاریخ: {today}", ln=True, align='R')
        pdf.ln(10)

        headers = []
        for col in range(self.sale_table.columnCount()):
            header_item = self.sale_table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else "")

        col_width = 40
        row_height = 10

        pdf.set_font("Persian" if use_farsi_font else "Arial", size=13)
        for header in headers:
            pdf.cell(col_width, row_height, txt=header, border=1, align='C')
        pdf.ln(row_height)

        pdf.set_font("Persian" if use_farsi_font else "Arial", size=14)
        for row in range(self.sale_table.rowCount()):
            for col in range(self.sale_table.columnCount()):
                item = self.sale_table.item(row, col)
                text = item.text() if item else ''
                pdf.cell(col_width, row_height, txt=text, border=1, align='C')
            pdf.ln(row_height)

        pdf.output(file_path)
        print(f"✅ فایل PDF ذخیره شد در: {file_path}")

    ##
    def create_buy_report_pdf(self):
        pass     

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
    