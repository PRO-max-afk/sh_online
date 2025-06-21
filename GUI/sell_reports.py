from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtGui import QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QDate,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os
import jdatetime


class SalesDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #D9D9D9;")
        
        self.tab_buttons = []  # لیستی برای نگهداری دکمه‌ها
        self.in_UI()
        self.label_UI()
        self.button_UI()
        self.set_today_date()
        self.set_today_time()
    
    
    def in_UI(self):
        self.stack_widget= QStackedWidget()
        self.setCentralWidget(self.stack_widget)
        ##
        self.sell_r_page= QWidget()

        main_layout = QVBoxLayout(self.sell_r_page)
        
        # لایه بالا
        top_layout = QHBoxLayout()
        self.labels = QLabel("گزارشات فروش", self)
        title_label= QHBoxLayout()
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        title_label.addWidget(self.labels)


        ##
        self.labels.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        ##
        datetime_layout = QVBoxLayout()
        self.date_label = QLabel()
        self.time_label = QLabel()
        self.back_btn= QPushButton()

        #datetime_layout.addWidget(self.date_label)
        #datetime_layout.addWidget(self.time_label)
        datetime_layout.addWidget(self.back_btn)
        datetime_layout.setAlignment( Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(title_label) 
        top_layout.addStretch(1)
        top_layout.addLayout(datetime_layout)
        
        

        # --- تب‌ها: روزی، هفته، ماهانه
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #c7c9c8; border-radius: 10px;")
        tabs_layout = QHBoxLayout(tab_frame)
        tab_frame.setFixedSize(500, 50)
         # --- باکس‌های آماری
        stats_layout = QHBoxLayout()
        stats = [
            ("فروشات حضوری", "300"),
            ("فروشات آنلاین", "90,000,000 IRR"),
            ("فروشات مبایل", "8,000,000 IRR"),
            ("مجموعه فروشات", "81,000,000 IRR"),
            ("فایده کلی", "22,000,000 IRR"),
        ]
        for title, value in stats:
            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 10px;
                    color:black;
                    font-family: B Nazanin;
                    font-weight: bold;
                    padding: 5px;
                }
                QLabel {
                    font-size: 14px;
                    margin: 4px;
                }
            """)
            box_layout = QVBoxLayout(box)
            top_title= QLabel(title)
            top_title.setStyleSheet('''
                color: black;
                font-family: Mirza,"B Nazanin";
                font-size: 15px;
                font-weight: bold;
            ''')
            top_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            box_layout.addWidget(top_title)
            val_label = QLabel(value)
            val_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_label.setStyleSheet("font-weight: bold; font-size: 14px; font-family: arial;")
            box_layout.addWidget(val_label)
            stats_layout.addWidget(box)
            ###shadow
            shadow= QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 70))
            box.setGraphicsEffect(shadow)

            
        
        ###
        self.day_btn= QPushButton()
        self.month_btn= QPushButton()
        self.week_btn= QPushButton()
       # --- تعریف فریم‌ها و لایه‌ها
        self.day_frame = QFrame()
        self.day_layout = QVBoxLayout(self.day_frame)
        #self.day_layout.addWidget(self.create_bar_chart())

        self.week_frame = QFrame()
        self.week_layout = QVBoxLayout(self.week_frame)
        #self.week_layout.addWidget(self.create_bar_chart())

        self.month_frame = QFrame()
        self.month_layout = QVBoxLayout(self.month_frame)

        # --- نگاشت دکمه‌ها به فریم‌ها
        self.tab_buttons = []
        self.tab_frames = {
            self.day_btn: self.day_frame,
            self.week_btn: self.week_frame,
            self.month_btn: self.month_frame
        }

        # --- دکمه‌ها
        for btn in (self.day_btn, self.week_btn, self.month_btn):
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
            btn.clicked.connect(lambda checked, b=btn: self.handle_tab_click(b))
            self.tab_buttons.append(btn)
            tabs_layout.addWidget(btn)

        # نمایش پیش‌فرض
        self.handle_tab_click(self.month_btn)
       
        # --- لایه برای فریم فعال (فقط یکی در لحظه داخل آن خواهد بود)
        self.chart_container = QVBoxLayout()
        self.chart_container.addWidget(self.month_frame)  # فقط فریم پیش‌فرض
        # --- لایه برای فریم فعال (فقط یکی در لحظه داخل آن خواهد بود)
        self.chart_containers = QVBoxLayout()
        self.chart_container.addWidget(self.week_frame)  # فقط فریم پیش‌فرض# --- لایه بر

        self.chart_containeres = QVBoxLayout()
        self.chart_container.addWidget(self.day_frame)  # فقط فریم پیش‌فرض

        # --- افزودن به لایه اصلی
        main_layout.addLayout(top_layout)
        main_layout.addWidget(tab_frame, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addLayout(stats_layout)
        main_layout.addLayout(self.chart_container)  # اینجا فقط یک فریم داخل آن هست
        main_layout.addLayout(self.chart_containers)
        main_layout.addLayout(self.chart_containeres)

        self.stack_widget.addWidget(self.sell_r_page)


        # --- نمودار QChartView
        chart_view = self.create_bar_chart_month()
        chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        week_chart= self.create_bar_chart_week()
        week_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        day_chart= self.create_bar_chart_day()
        day_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ###
        self.month_layout.addWidget(chart_view)
        self.week_layout.addWidget(week_chart)
        self.day_layout.addWidget(day_chart)
        ###
        self.stack_widget.addWidget(self.sell_r_page)

    ##
    def label_UI(self):
        self.labels.setMinimumSize(200, 40)
        self.labels.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;
        ''')
    ##
    def create_bar_chart_month(self):
        from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
        from PyQt6.QtGui import QColor, QPainter, QFont
        from PyQt6.QtCore import Qt

        months = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]
        values = [8000000, 10000000, 14000000, 20000000, 35000000,
                50000000, 42000000, 25000000, 1200000, 3000000, 55000000, 6000000]

        # فقط یک BarSet می‌سازیم
        bar_set = QBarSet("فروش ماهانه")
        bar_set.append(values)

        # 🔸 رنگ اصلی را تعیین می‌کنیم (مثلاً خاکستری)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)  # 🔸 تراز و عرض مناسب

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("گزارش فروش ماهانه")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) + 5000000)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

    ##
    def create_bar_chart_week(self):
        from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
        from PyQt6.QtGui import QColor, QPainter, QFont
        from PyQt6.QtCore import Qt

        months = ["شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهارشنبه", "جمعه"]
        values = [8000000, 10000000, 14000000, 20000000, 35000000,
                50000000, 42000000]

        # فقط یک BarSet می‌سازیم
        bar_set = QBarSet("فروش هفته وار")
        bar_set.append(values)

        # 🔸 رنگ اصلی را تعیین می‌کنیم (مثلاً خاکستری)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)  # 🔸 تراز و عرض مناسب

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("گزارش فروش هفته وار")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) + 5000000)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

    ##
    def create_bar_chart_day(self):
        from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
        from PyQt6.QtGui import QColor, QPainter, QFont
        from PyQt6.QtCore import Qt

        months = ["فروشات حضوری", "فروشات آنلاین", "فروشات مبایل"]
        values = [8000000, 10000000, 14000000]

        # فقط یک BarSet می‌سازیم
        bar_set = QBarSet("فروش روزانه")
        bar_set.append(values)

        # 🔸 رنگ اصلی را تعیین می‌کنیم (مثلاً خاکستری)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)  # 🔸 تراز و عرض مناسب

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("گزارشات فروش روزانه")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) + 5000000)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

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
    def button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.back_settings)
        self.back_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.back_btn.setStyleSheet('''
        QPushButton{
            background-color: transparent;
            border-radius: 27px;
            padding: 5px;
                                    }
   
        ''')
        ##
        self.day_btn.setText("روز")
        self.month_btn.setText("ماه")
        self.week_btn.setText("هفته")
    ##
    def handle_tab_click(self, clicked_btn):
        # استایل دکمه‌ها
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

        # نمایش فقط فریم مربوطه
        for btn, frame in self.tab_frames.items():
            frame.setVisible(btn == clicked_btn)

    ##
    def back_settings(self):
        from finance import Money

        self.settings= Money()
        self.stack_widget.addWidget(self.settings)

        
        self.stack_widget.setCurrentWidget(self.settings)
        ##
        start_pos = QPoint(-self.width(), 0)
        end_pos = QPoint(0, 0)
        self.settings.move(start_pos)
        ##
        self.animate= QPropertyAnimation(self.settings, b"pos",self)
        self.animate.setDuration(700)
        self.animate.setStartValue(start_pos)
        self.animate.setEndValue(end_pos)
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()
    ##
    
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
    

