from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect,QTextEdit,QStyledItemDelegate, QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush,QPalette,QPainter
from PyQt6 import QtCore
from circle import CircularSpinner
import sqlite3
import pymysql
import requests
from notifi_box import Notification
from calendars import JalaliCalendar
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import threading
from switch import ToggleSwitch
from message_b import MessageBox
from switch import ToggleSwitch
import os
import sys

class BlackTextDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor("black"))
        editor.setPalette(palette)
        return editor
class Barrow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.in_UI()
        self.label_UI()
        self.input_UI()
        self.Button_UI()
        self.table_UI()
        self.load_all_fonts()
    
    def in_UI(self):
        self.stack_barrow= QStackedWidget()
        self.setCentralWidget(self.stack_barrow)
        self.barrow_page= QWidget()

        main_layout= QVBoxLayout(self.barrow_page)
        
        top_layout= QHBoxLayout()

        self.top_label= QLabel("گزارشات قرض")
        
        back_layout= QHBoxLayout()
        self.back_btn= QPushButton()
        back_layout.addWidget(self.back_btn)
        ###
        top_layout.addLayout(back_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.top_label)
        ###
        middle_layout= QHBoxLayout()
        table_frame= QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        table_layout= QVBoxLayout(table_frame)
        self.top_table_ly= QHBoxLayout()
        
        ### widgets for table_frame
        self.title_lb= QLabel("آخرین اطلاعات قرض")
        self.har_table= QTableWidget()
        self.top_table_ly.addWidget(self.title_lb)
        ### adding to the frame
        table_layout.addLayout(self.top_table_ly)
        table_layout.addWidget(self.har_table)
        
        ###form frame
        feild_frame= QFrame()
        feild_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        self.form= QVBoxLayout(feild_frame)
        
        title_from_ly= QHBoxLayout()
        ##
        self.title_from= QLabel("ثبت قرض")
        title_from_ly.addWidget(self.title_from)
        ###forms
        self.form_layout= QVBoxLayout()
        ##name
        self.name_line= QLineEdit()
        self.name_line.setPlaceholderText("نام شخص")
        ##amount
        self.money_line= QLineEdit()
        self.money_line.setPlaceholderText("مقدار قرض")
        ##date
        self.date_line= QLineEdit()
        self.date_line.setPlaceholderText("تاریخ قرض")
        self.date_line.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.date_line.setReadOnly(True)
        ##
        self.descprit_text= QTextEdit()
        self.descprit_text.setPlaceholderText("....توضیحات بیشتر")
        ##
        self.save_btn= QPushButton()
        ##
        self.form.addLayout(title_from_ly)
        self.form.addLayout(self.form_layout)
        self.form.addWidget(self.save_btn)
        self.form_layout.setSpacing(7)
        ###
        chart_frame= QFrame()
        chart_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        chart_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)      
        chart_frame.setMaximumHeight(400)  
        chart_layout= QVBoxLayout(chart_frame)
        ##
        self.chart_view= self.create_bar_chart()
        self.chart_view.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        chart_layout.addWidget(self.chart_view)
        
        ###
        middle_layout.addWidget(chart_frame,2)
        middle_layout.addWidget(feild_frame,1)

        #####adding to the main layout
        main_layout.setSpacing(5)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout, 3)
        main_layout.addWidget(table_frame,2)
        self.stack_barrow.addWidget(self.barrow_page)
        
    ###  
    def label_UI(self):
        self.top_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
    ''')
        for label in (self.title_lb,self.title_from):
            label.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Fixed)
            label.setMaximumHeight(20)
            label.setMinimumHeight(5)
            label.setStyleSheet('''
                font-size: 18px;
                font-weight: bold; 
                color: black;
                font-family: B Nazanin;
            ''')
    ##
    def input_UI(self):
        for feild in (self.name_line,self.money_line,self.date_line):
            self.form_layout.addWidget(feild)
            feild.setMaximumHeight(40)
            feild.setMinimumHeight(20)
            feild.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
            if feild == self.money_line and self.date_line:
                font_family= 'Arial'
            else:
                font_family= ' "B Nazanin", Mirza'
            
            feild.setStyleSheet(f'''
                QLineEdit{{
                    color: black;
                    font-size: 16px;
                    font-family: {font_family};
                    font-weight: bold;
                    border: 1px solid gray;
                    padding: 5px;
                    border-radius: 5px;}}
        
            ''')
        self.form_layout.addWidget(self.descprit_text)
        ##
        self.descprit_text.setMaximumHeight(150)
        #self.descprit_text.setMaximumHeight(20)
        self.descprit_text.setStyleSheet('''
                    color: black;
                    font-size: 16px;
                    font-family: B Nazanin;
                    font-weight: bold;
                    border: 1px solid gray;
                    padding: 5px;
                    border-radius: 5px;

        ''')
        self.descprit_text.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    ###
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
        self.calendar_btn= QPushButton(self.date_line)
        self.calendar_btn.move(5,2)
        self.cale_icon= QIcon(self.get_asset_path("calendar_8265298.png"))
        self.calendar_btn.setIcon(self.cale_icon)
        self.calendar_btn.setIconSize(QtCore.QSize(25,25))

        self.calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 7px; /* گردی برای همه حالت‌ها */
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
        self.save_btn.setText("ثبت قرض")
        self.save_btn.setStyleSheet('''
            QPushButton {
                    background-color: #1be314;
                    color: white;
                    font-family: "B Nazanin";
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    text-align: center;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #5bfa55;  
                }
                QPushButton:pressed {
                    background-color: #1be314;
                }
    ''')
    ###
    def table_UI(self):
        self.har_table.setColumnCount(5)
        self.har_table.setHorizontalHeaderLabels(["نام شخص", "مقدار قرض","نوعیت قرض","تاریخ","توضیحات"])
        self.har_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.har_table.verticalHeader().setVisible(False)
        self.har_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.har_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # تنظیمات Head Section (ریسپانسیو ستون‌ها)
        header = self.har_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignHCenter)
        header.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # حالت ریسپانسیو برای ستون‌ها:
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # نام شخص
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # مقدار برداشت
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # نوعیت قرض
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # توضیحات → کشیده‌تر

        # اعمال استایل
        self.har_table.setStyleSheet("""
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

        # اگر نماینده‌ای برای رنگ یا ظاهر سفارشی داری:
        self.har_table.setItemDelegate(BlackTextDelegate())  # اگر کلاس تعریف شده است

    def show_calendar(self):
        self.calendar_popup = JalaliCalendar(self)
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomRight())
        self.calendar_popup.show_with_animation(pos)
    ##
    def set_selected_date(self, date_str):
        self.date_line.setText(date_str)
        self.date_line.setAlignment(Qt.AlignmentFlag.AlignRight)  
    ###
    def open_reports(self):
        from finance import Money
        self.finace= Money()
        self.stack_barrow.addWidget(self.finace)
        self.stack_barrow.setCurrentWidget(self.finace)
        
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
    def create_bar_chart(self):
        total = [5000, 2000, 500004, 2334243, 321000]  # یا هر مقدار پیش‌فرض دلخواه
        name_labels = ["مقدار طلب", "", "مقدار برده گی", "مقدار رسیده گی", "پول نقد"]
        colors = ["#ff5733", "#33c1ff", "#9b59b6", "#f1c40f", "#e67e22"]

        series = QBarSeries()

        for i in range(len(total)):
            bar_set = QBarSet(name_labels[i])
            bar_set << total[i]
            bar_set.setColor(QColor(colors[i]))
            bar_set.setLabelFont(QFont("B Nazanin", 11))
            bar_set.setLabelBrush(QColor("black"))
            series.append(bar_set)

        series.setBarWidth(0.6)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("نمودار اطلاعات قرض")
        chart.setTitleFont(QFont("B Nazanin", 15, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append([""])
        axis_x.setLabelsFont(QFont("B Nazanin", 12))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(total))
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setFont(QFont("B Nazanin", 11))

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        return chart_view

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
    