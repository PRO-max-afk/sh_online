from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtGui import QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QDate,QPoint,QPropertyAnimation,QEasingCurve,QTimer
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os
import jdatetime
from month_ca import MonthSelectorDialog
from sale_thread import SaleThread
from circle import CircularSpinner



class SalesDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #D9D9D9;")
        
        self.tab_buttons = []  # لیستی برای نگهداری دکمه‌هاپ
        self.val_labels= {} 
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
        middle_layout= QHBoxLayout()
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #c7c9c8; border-radius: 10px;")
        tabs_layout = QHBoxLayout(tab_frame)
        tab_frame.setFixedSize(500, 50)
        ##
        self.calendar_btn= QPushButton()
        middle_layout.addWidget(self.calendar_btn,alignment=Qt.AlignmentFlag.AlignRight)
        middle_layout.addStretch(1)
        middle_layout.addWidget(tab_frame,alignment=Qt.AlignmentFlag.AlignHCenter)
        middle_layout.addStretch(1)
        
        # --- باکس‌های آماری
        stats_layout = QHBoxLayout()
        stats = [
            ("فروشات حضوری", "offline"),
            ("فروشات آنلاین", "online"),
            ("فروشات مبایل", "mobile"),
            ("مجموعه فروشات", "total"), 
            ("فایده کلی", "profit") ]
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
        self.run_layout= QVBoxLayout()
        self.run_layout.addLayout(stats_layout)
        self.run_layout.addLayout(self.chart_container)  # اینجا فقط یک فریم داخل آن هست
        self.run_layout.addLayout(self.chart_containers)
        self.run_layout.addLayout(self.chart_containeres)
        
        ###main layout
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(middle_layout)
        #self.main_layout.addLayout(self.run_layout)

    
        ###
        self.stack_widget.addWidget(self.sell_r_page)


        # --- نمودار QChartView
        self.month_chart_view = self.create_bar_chart_month()
        self.month_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        week_chart= self.create_bar_chart_week()
        week_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ##
        day_chart= self.create_bar_chart_day()
        day_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ###
        self.month_layout.addWidget(self.month_chart_view)
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
    def show_calendar(self):
        self.calendar_popup = MonthSelectorDialog(self)
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomLeft())
        self.calendar_popup.show_with_animation(pos)
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
        bar_set = QBarSet("فروش ماهانه")
        bar_set.append(monthly_totals)
        bar_set.setColor(QColor("#11f55d"))
        bar_set.setLabelFont(QFont("B Nazanin", 11))
        bar_set.setLabelBrush(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)

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
        axis_y.setRange(0, total_sale_value if total_sale_value else 0)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view


    ##
    def create_bar_chart_week(self):
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
        self.cale_icon= QIcon(self.get_asset_path("calendar_8265298.png"))
        self.calendar_btn.setIcon(self.cale_icon)
        self.calendar_btn.setIconSize(QtCore.QSize(35,35))
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                padding: 5px;
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
    ## new thread
    def show_first_spinner(self):
        self.hide_run_layout_widgets()  # ← اول مخفی کن
        self.show_spinner_and_load_data()
    ##
    def show_spinner_and_load_data(self):
        # ویجت کاور شامل همه چیز
        self.run_layout_widget = QWidget()
        self.main_layout.addWidget(self.run_layout_widget)

        # لایه اصلی کاور
        wrapper_layout = QVBoxLayout(self.run_layout_widget)

        # فقط spinner ابتدا نمایش داده شود
        self.spinner_wrapper = QWidget()
        spinner_layout = QVBoxLayout(self.spinner_wrapper)
        spinner_layout.setContentsMargins(0, 100, 0, 100)
        spinner_layout.addStretch()

        self.spinner = CircularSpinner(self)
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        spinner_layout.addStretch()

        wrapper_layout.addWidget(self.spinner_wrapper)

        # ایجاد run_layout اما فعلاً اضافه نمی‌شود
        self.run_layout_holder = QWidget()
        self.run_layout_holder.setVisible(False)
        self.run_layout_holder.setLayout(self.run_layout)

        wrapper_layout.addWidget(self.run_layout_holder)

        # شروع بارگذاری
        QTimer.singleShot(100, self.start_thread)


    def start_thread(self):
        self.sale_thread = SaleThread()
        self.sale_thread.ofline_sale.connect(self.ofline_sale)
        self.sale_thread.monthly_sale.connect(self.update_month_chart)  # ← اتصال جدید
        self.sale_thread.total_sale.connect(self.total_value)
        self.sale_thread.online_sale.connect(self.online_sale)
        self.sale_thread.finished.connect(self.on_data_loaded)  # ← اتصال جدید
        self.sale_thread.start()

    ##
    def on_data_loaded(self):
        self.spinner_wrapper.deleteLater()
        self.run_layout_holder.setVisible(True)


    ##
    def ofline_sale(self,value):
        self.val_labels["offline"].setText(f"{value} افغانی")
    ##
    def online_sale(self,value):
        self.val_labels["online"].setText(f'{value} افغانی')
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
    

