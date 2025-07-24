from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout,QComboBox)
from PyQt6.QtGui import QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QDate,QPoint,QPropertyAnimation,QEasingCurve,QTimer
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os
import jdatetime
from buy_thread import BuyThread
from circle import CircularSpinner



class BuyDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #D9D9D9;")
        
        self.tab_buttons = []  # لیستی برای نگهداری دکمه‌هاپ
        self.val_labels= {} 
        self.val_labelse= {}
        self.val_labelses= {}
        self.selected_month= None
        self.selected_week=None
        self.selected_day=None
        self.in_UI()
        self.label_UI()
        self.button_UI()
        self.set_today_date()
        self.set_today_time()
        self.show_first_spinner()
        self.load_all_fonts()
    
    
    def in_UI(self):
        self.stack_widget= QStackedWidget()
        self.setCentralWidget(self.stack_widget)
        ##
        self.sell_r_page= QWidget()

        self.main_layout = QVBoxLayout(self.sell_r_page)
        
        # لایه بالا
        top_layout = QHBoxLayout()
        self.labels = QLabel("گزارشات خرید", self)
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
        datetime_layout.setAlignment( Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(title_label) 
        top_layout.addStretch(1)
        top_layout.addLayout(datetime_layout)
        
        

        # --- تب‌ها: روزی، هفته، ماهانه
        middle_layout= QHBoxLayout()
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #c7c9c8; border-radius: 10px;")
        tabs_layout = QHBoxLayout(tab_frame)
        tab_frame.setFixedSize(500, 50)
        ##
        self.month_combo = QComboBox()
        middle_layout.addWidget(self.month_combo,alignment=Qt.AlignmentFlag.AlignRight)
        middle_layout.addStretch(1)
        middle_layout.addWidget(tab_frame,alignment=Qt.AlignmentFlag.AlignHCenter)
        middle_layout.addStretch(1)
        
        # --- تعریف فریم‌ها و لایه‌ها
        self.day_frame = QFrame()
        self.day_layout = QVBoxLayout(self.day_frame)
        #self.day_layout.addWidget(self.create_bar_chart())

        self.week_frame = QFrame()
        self.week_layout = QVBoxLayout(self.week_frame)
        #self.week_layout.addWidget(self.create_bar_chart())

        self.month_frame = QFrame()
        self.month_layout = QVBoxLayout(self.month_frame)
        
        # --- باکس‌های آماری
        stats_layout = QHBoxLayout(self.month_frame)
        stats = [
            ("خرید ماه جاری", "current_month"),
            ("خرید ماه گذشته", "past_month"),
            ("فیصدی تغییری (%)", "percent"),
            ("مجموعه خرید ماهانه", "total")]
        for title, key in stats:
            box = QFrame()
            box.setStyleSheet("""
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
            """)

            box_layout = QVBoxLayout(box)
            shadow= QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0,0,0,70))
            box.setGraphicsEffect(shadow)

            # عنوان
            top_title = QLabel(title)
            top_title.setStyleSheet("""
                color: black;
                font-family: Mirza, 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
            """)
            top_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            box_layout.addWidget(top_title)

            # مقدار
            val_label = QLabel("")
            val_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_label.setStyleSheet("""
                font-weight: bold;
                font-size: 14px;
                font-family: Arial;
            """)
            box_layout.addWidget(val_label)

            # ذخیره label با کلید مشخص
            self.val_labels[key] = val_label
            stats_layout.addWidget(box)
        ###
        # --- باکس‌های آماری
        stats_layout_w = QHBoxLayout(self.month_frame)
        statse = [
            ("هفته اول", "first"),
            ("هفته دوم", "second"),
            ("هفته سوم", "third"),
            ("هفته چهارم", "fourth"), 
            ("مجموعه چهار هفته", "total_week") ]
        for title, key in statse:
            box = QFrame()
            box.setStyleSheet("""
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
            """)

            box_layout = QVBoxLayout(box)
            shadow= QGraphicsDropShadowEffect(self)
            
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0,0,0,70))
            box.setGraphicsEffect(shadow)

            # عنوان
            top_title = QLabel(title)
            top_title.setStyleSheet("""
                color: black;
                font-family: Mirza, 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
            """)
            top_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            box_layout.addWidget(top_title)

            # مقدار
            val_labels = QLabel("")
            val_labels.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_labels.setStyleSheet("""
                font-weight: bold;
                font-size: 14px;
                font-family: Arial;
            """)
            box_layout.addWidget(val_labels)

            # ذخیره label با کلید مشخص
            self.val_labelse[key] = val_labels
            stats_layout_w.addWidget(box)
        ###
         # --- باکس‌های آماری
        stats_layout_d = QHBoxLayout(self.month_frame)
        statses = [
            ("شنبه", "saturday"),
            ("یکشنبه", "sunday"),
            ("دوشنبه", "monday"),
            ("سه شنبه", "tuesday"), 
            ("چهارشبنه", "wednesday"),
            ("پنجشنبه","thursday"),
            ("جمعه","friday")]
        for title, key in statses:
            box = QFrame()
            box.setStyleSheet("""
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
            """)

            box_layout = QVBoxLayout(box)
            shadow= QGraphicsDropShadowEffect(self)
            
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0,0,0,70))
            box.setGraphicsEffect(shadow)

            # عنوان
            top_title = QLabel(title)
            top_title.setStyleSheet("""
                color: black;
                font-family: Mirza, 'B Nazanin';
                font-size: 15px;
                font-weight: bold;
            """)
            top_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            box_layout.addWidget(top_title)

            # مقدار
            val_labelss = QLabel("")
            val_labelss.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_labelss.setStyleSheet("""
                font-weight: bold;
                font-size: 14px;
                font-family: Arial;
            """)
            box_layout.addWidget(val_labelss)

            # ذخیره label با کلید مشخص
            self.val_labelses[key] = val_labelss
            stats_layout_d.addWidget(box)
        ###
        self.day_btn= QPushButton()
        self.month_btn= QPushButton()
        self.week_btn= QPushButton()
       

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
        self.month_layout.addLayout(stats_layout)  # فقط به ماه اضافه شود
        self.chart_container.addWidget(self.month_frame)
        
        # --- لایه برای فریم فعال (فقط یکی در لحظه داخل آن خواهد بود)
        self.chart_containers = QVBoxLayout()
        self.week_layout.addLayout(stats_layout_w)
        self.chart_containers.addWidget(self.week_frame)  # فقط فریم پیش‌فرض# --- لایه بر

        self.chart_containeres = QVBoxLayout()
        self.day_layout.addLayout(stats_layout_d)
        self.chart_containeres.addWidget(self.day_frame)  # فقط فریم پیش‌فرض

        # --- افزودن به لایه اصلی
        self.run_layout= QVBoxLayout()
        #self.run_layout.addLayout(stats_layout)
        self.run_layout.addLayout(self.chart_container)  # اینجا فقط یک فریم داخل آن هست
        self.run_layout.addLayout(self.chart_containers)
        self.run_layout.addLayout(self.chart_containeres)
        
        ###main layout
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(middle_layout)
        #self.main_layout.addLayout(self.run_layout


        # --- نمودار QChartView
        self.month_chart_view = self.create_bar_chart_month()
        self.month_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        self.week_chart_view= self.create_bar_chart_week()
        self.week_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        self.day_chart= self.create_bar_chart_day()
        self.day_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ###
        self.month_layout.addWidget(self.month_chart_view)
        self.week_layout.addWidget(self.week_chart_view)
        self.day_layout.addWidget(self.day_chart)
        ###
        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
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
    def update_month_chart(self, monthly_totals,total_sale_value: float):
        # اطمینان از اینکه ورودی یک لیست است
        if not isinstance(monthly_totals, list):
            print("❌ خطا: مقدار ورودی برای چارت باید لیست باشد")
            return

        # حذف چارت قبلی
        if self.month_chart_view:
            self.month_layout.removeWidget(self.month_chart_view)
            self.month_chart_view.deleteLater()

        # ساخت چارت جدید
        self.month_chart_view = self.create_bar_chart_month(monthly_totals,total_sale_value)
        self.month_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.month_layout.addWidget(self.month_chart_view)

    ##
    def create_bar_chart_month(self, monthly_totals: list[float] = None,total_sale_value: float=0):

        months = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
                "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]

        # اگر آرگومان داده نشد، با صفر پر شود
        if monthly_totals is None:
            monthly_totals = [0] * 12
        elif len(monthly_totals) < 12:
            monthly_totals += [0] * (12 - len(monthly_totals))

        # 🔸 ساخت مجموعه داده‌ها
        bar_set = QBarSet("خرید ماهانه")
        bar_set.append(monthly_totals)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("گزارش خرید ماهانه")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, total_sale_value if total_sale_value else 0)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view


    ##
    def update_week_chart(self, week_sale,total_sale_week: float):
        # اطمینان از اینکه ورودی یک لیست است
        if not isinstance(week_sale, list):
            print("❌ خطا: مقدار ورودی برای چارت باید لیست باشد")
            return

        # حذف چارت قبلی
        if self.week_chart_view:
            self.week_layout.removeWidget(self.week_chart_view)
            self.week_chart_view.deleteLater()

        # ساخت چارت جدید
        self.week_chart_view = self.create_bar_chart_week(week_sale,total_sale_week)
        self.week_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.week_layout.addWidget(self.week_chart_view)

    ##
    def create_bar_chart_week(self, weekly_sales: list[float] = None, total_week_value: float = 0):
        # اگر هیچ داده‌ای داده نشده، مقدار پیش‌فرض
        if weekly_sales is None:
            weekly_sales = [0] * 4  # فرض: حداکثر 4 هفته اخیر

        # ساخت لیبل‌های هفته‌ها (هفته ۱، هفته ۲، ...)
        week_labels = [f"هفته {i + 1}" for i in range(len(weekly_sales))]

        # 🔹 ساخت BarSet
        bar_set = QBarSet("خرید هفته وار")
        bar_set.append(weekly_sales)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        # 🔹 سری داده‌ها
        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)

        # 🔹 چارت اصلی
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("گزارش خرید هفته وار")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # 🔹 محور X (لیبل هفته‌ها)
        axis_x = QBarCategoryAxis()
        axis_x.append(week_labels)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # 🔹 محور Y (مقدار فروش)
        axis_y = QValueAxis()
        axis_y.setRange(0, total_week_value if total_week_value else max(weekly_sales + [0]))
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # 🔹 نهایی: QChartView
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

    ##
    def update_day_chart(self, day_sale, total_sale_day: float):
        if not isinstance(day_sale, list):
            print("❌ خطا: مقدار ورودی برای چارت باید لیست باشد")
            return

        if self.day_chart:
            self.day_layout.removeWidget(self.day_chart)
            self.day_chart.deleteLater()

        # استفاده از selected_day
        selected_day_name = self.selected_day or "روز نامشخص"
        self.day_chart = self.create_bar_chart_day(day_sale, total_sale_day, selected_day_name)
        self.day_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.day_layout.addWidget(self.day_chart)


    ##
    def create_bar_chart_day(self, daily_sales: list[float] = None, total_day_value: float = 0, selected_day_label: str = ""):
        # اگر هیچ داده‌ای داده نشده، مقدار پیش‌فرض ۷ روز هفته
        if daily_sales is None:
            daily_sales = [0] * 7

        # لیبل‌های روزهای هفته شمسی
        day_labels = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]

        # 🔹 ساخت BarSet
        bar_set = QBarSet("خرید روزانه")
        bar_set.append(daily_sales)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        # 🔹 سری داده‌ها
        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)

        # 🔹 چارت اصلی
        chart = QChart()
        chart.addSeries(series)

        # استفاده از selected_day_label برای عنوان چارت
        title_text = "گزارش خرید روزانه"
        if selected_day_label:
            title_text += f" ({selected_day_label})"

        chart.setTitle(title_text)
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # 🔹 محور X (روزهای هفته)
        axis_x = QBarCategoryAxis()
        axis_x.append(day_labels)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # 🔹 محور Y (مقدار فروش)
        axis_y = QValueAxis()
        axis_y.setRange(0, total_day_value if total_day_value else max(daily_sales + [0]))
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # 🔹 نهایی: QChartView
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
        self.back_btn.clicked.connect(self.open_reports)
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
        self.month_combo.setFixedWidth(150)
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

        # اضافه کردن ماه‌های شمسی
        self.months_jalali = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
                            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]
        self.month_combo.addItems(self.months_jalali)
       ##
       # تنظیم مقدار پیش‌فرض به ماه جاری
        today = jdatetime.date.today()
        self.month_combo.setCurrentIndex(today.month - 1)
        self.month_combo.currentIndexChanged.connect(self.handle_month_change)
       
    ###
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
        
        ## setting month,week names
        self.month_combo.clear()
        if clicked_btn== self.month_btn:
            # ماه‌های شمسی
            months = [
                "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
                "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
            ]
            self.month_combo.addItems(months)
        elif clicked_btn== self.week_btn:
            week= ["هفته اول","هفته دوم","هفته سوم"," هفته چهارم"]
            self.month_combo.addItems(week)
        elif clicked_btn == self.day_btn:
            day= ["شنبه","یکشنبه","دوشنبه","سه شنبه","چهارشنبه","پنجشنبه","جمعه"]
            self.month_combo.addItems(day)

    ##
    def open_reports(self):
        from finance import Money
        self.finace= Money()
        self.stack_widget.addWidget(self.finace)
        self.stack_widget.setCurrentWidget(self.finace)
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
    ## new thread
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
            self.run_layout_holder.setLayout(self.run_layout)
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

        # 👇 مقدار انتخاب‌شده را بده به ترد
        QTimer.singleShot(100, lambda: self.start_thread(self.selected_month))

    ##
    def start_thread(self, year_month: str = None, week_label: str = None,selected_day: str= None):
        if year_month is None:
            jdate = jdatetime.date.today()
            year_month = f"{jdate.year}/{jdate.month:02d}"

        # جلوگیری از راه‌اندازی مجدد ترد اگر همان ماه انتخاب شده است
        if hasattr(self, 'sale_thread') and self.sale_thread.isRunning():
            if self.selected_month == year_month:
                print("ℹ️ Thread already running for this month")
                return
            else:
                print("🔄 Stopping previous thread")
                self.sale_thread.quit()
                self.sale_thread.wait()

        self.selected_month = year_month  # مقداردهی به متغیر
        print(f"▶ Starting thread for: {year_month}")

        self.sale_thread = BuyThread(selected_month=year_month, selected_week=week_label,selected_day=selected_day)
        self.sale_thread.ofline_sale.connect(self.ofline_sale)
        self.sale_thread.monthly_sale.connect(self.update_month_chart)
        self.sale_thread.total_sale.connect(self.total_value)
        self.sale_thread.online_sale.connect(self.online_sale)
        self.sale_thread.monthly_sa.connect(self.update_monthly_boxes)
        ##week
        self.sale_thread.weekly_sale.connect(self.update_week_chart)
        self.sale_thread.weekly_sa.connect(self.weekly_boxes)
        ##day
        self.sale_thread.daily_sale.connect(self.update_day_chart)
        self.sale_thread.daily_sa.connect(self.daily_boxes)

        self.sale_thread.finished.connect(self.on_data_loaded)
        self.sale_thread.start()

    ##
    def on_data_loaded(self):
        if self.spinner_wrapper:
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None  # ← برای بررسی بعدی
        self.run_layout_holder.setVisible(True)


    ##
    def ofline_sale(self,value):
        self.val_labels["current_month"].setText(f"{value} افغانی")
    ##
    def online_sale(self,value):
        self.val_labels["past_month"].setText(f'{value} افغانی')
    ##
    def total_value(self,total_sale_value):
        self.val_labels["total"].setText(f'{total_sale_value} افغانی')

    ##
    def hide_run_layout_widgets(self):
        for i in range(self.run_layout.count()):
            item = self.run_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setVisible(False)
    ##
    def update_monthly_boxes(self, stats: dict):
        for key, value in stats.items():
            if key in self.val_labels:
                self.val_labels[key].setText(f"{value:,.0f}")
    ##
    def weekly_boxes(self, states: dict):
        for key , value in states.items():
            if key in self.val_labelse:
                self.val_labelse[key].setText(f"{value:,.0f}")
    ##
    def daily_boxes(self, statess: dict):
        for key , value in statess.items():
            if key in self.val_labelses:
                self.val_labelses[key].setText(f"{value:,.0f}")

    ##
    def set_selected_month_data(self, year_month: str):
        if self.selected_month != year_month:
            self.selected_month = year_month
            self.start_thread(year_month)
            self.show_first_spinner()
        else:
            # ماه تکراری، ولی دوباره لود شود → قبل از اجرای thread بررسی شود
            if not hasattr(self, 'sale_thread') or not self.sale_thread.isRunning():
                self.start_thread(year_month)
                self.show_first_spinner()

    ##
    def set_selected_week_data(self, year_month: str, week_label: str):
        # week_label مثلاً "هفته 2"
        if self.selected_month != year_month or self.selected_week != week_label:
            self.selected_month = year_month
            self.selected_week = week_label
            self.start_thread(year_month, week_label)
            self.show_first_spinner()
        else:
            if not hasattr(self, 'sale_thread') or not self.sale_thread.isRunning():
                self.start_thread(year_month, week_label)
                self.show_first_spinner()
    ##
    def set_selected_day_data(self, year_month: str, day_label: str):
        # day_label مثال: "شنبه" یا "دوشنبه"
        if self.selected_month != year_month or self.selected_day != day_label:
            self.selected_month = year_month
            self.selected_day = day_label
            self.start_thread(year_month, selected_day=day_label)
            self.show_first_spinner()
        else:
            if not hasattr(self, 'sale_thread') or not self.sale_thread.isRunning():
                self.start_thread(year_month, selected_day=day_label)
                self.show_first_spinner()

    ##
    def handle_month_change(self, index):
        today = jdatetime.date.today()
        current_year = today.year
        current_month = today.month
        current_day = today.day
        selected_text = self.month_combo.itemText(index)

        if self.month_btn.styleSheet().find("background-color: white") != -1:
            # 🔹 انتخاب ماهانه
            month_number = index + 1
            formatted_month = f"{current_year}/{month_number:02d}"
            print(f"📆 انتخاب ماهانه: {formatted_month}")
            self.set_selected_month_data(formatted_month)

        elif self.week_btn.styleSheet().find("background-color: white") != -1:
            # 🔹 انتخاب هفته‌ای
            formatted_month = f"{current_year}/{current_month:02d}"
            week_number = index + 1
            week_label = f"هفته {week_number}"
            print(f"📅 انتخاب هفته‌ای: {formatted_month} - {week_label}")
            self.set_selected_week_data(formatted_month, week_label)

        elif self.day_btn.styleSheet().find("background-color: white") != -1:
            # 🔹 انتخاب روزانه
            formatted_month = f"{current_year}/{current_month:02d}"
            day_label = selected_text.strip()
            print(f"📅 انتخاب روزانه: {formatted_month} - {day_label}")
            self.set_selected_day_data(formatted_month, day_label)

    
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
    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)

