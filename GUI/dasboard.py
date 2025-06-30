from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QWidget,QGridLayout,QComboBox)
from PyQt6.QtGui import QPainter,QFont,QColor,QFontDatabase,QIcon
from PyQt6.QtCore import Qt, QDate,QPoint,QPropertyAnimation,QEasingCurve,QTimer
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6 import QtCore
import os
import jdatetime
from year_thread import YearThread
from circle import CircularSpinner



class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #D9D9D9;")
    
        self.selected_year= None
        self.val_labels= {}
        self.year_thread =  None
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
        self.labels = QLabel("داشبورد", self)
        title_label= QHBoxLayout()
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        title_label.addWidget(self.labels)


        ##
        self.labels.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        ##
        datetime_layout = QVBoxLayout()
        self.date_label = QLabel()
        self.time_label = QLabel()

        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment( Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(title_label) 
        top_layout.addStretch(1)
        top_layout.addLayout(datetime_layout)
        
        

        # --- تب‌ها: روزی، هفته، ماهانه
        middle_layout= QHBoxLayout()
        ##
        self.year_combo = QComboBox()
        middle_layout.addWidget(self.year_combo,alignment=Qt.AlignmentFlag.AlignRight)
        middle_layout.addStretch(1)
        
        # --- باکس‌های آماری
        stats_layout = QHBoxLayout()
        stats = [
            ("کل خریداری", "total_buy"),
            ("کل فروشات", "total_sale"),
            ("مفاد خالص", "profit"),
            ("مجموعه برداشت ها","harvest"),
            ("مجموعه قرض ها","total_barrow"),
            ("سرمایه فعلی", "current_capital"), 
            ("پول نقد", "total_cush")
              ]
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

        # --- افزودن به لایه اصلی
        self.run_layout= QVBoxLayout()
        self.run_layout.addLayout(stats_layout)
        ##
        self.chart_veiw= self.create_bar_chart_year()
        self.chart_veiw.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.run_layout.addWidget(self.chart_veiw)
        ###main layout
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(middle_layout)
        #self.main_layout.addLayout(self.run_layout)

    
        ###
        self.stack_widget.addWidget(self.sell_r_page)


       
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
        ##
        self.year_combo.setFixedWidth(150)
        self.year_combo.setStyleSheet('''
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
                padding-left: 45px;
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
        QTimer.singleShot(100, lambda: self.box_thread())

    
    def box_thread(self, selected_year: str = None):
        if selected_year is None:
            selected_year = getattr(self, "selected_year", None)

        if self.year_thread and self.year_thread.isRunning():
            self.year_thread.quit()
            self.year_thread.wait()

        self.year_thread = YearThread(selected_year=selected_year)
        self.year_thread.full_info.connect(self.update_boxes_thread)
        self.year_thread.chart_data.connect(self.update_bar_chart)
        self.year_thread.year_info.connect(self.update_boxes_thread)
        self.year_thread.year_chart.connect(self.update_bar_chart)
        self.year_thread.year_data.connect(self.this_year)
        self.year_thread.finished.connect(self.on_data_loaded)
        self.year_thread.finished.connect(self.on_data_loaded)
        self.year_thread.start()
        


    ##
    def on_data_loaded(self):
        if self.spinner_wrapper:
            self.spinner_wrapper.deleteLater()
            self.spinner_wrapper = None  # ← برای بررسی بعدی
        self.run_layout_holder.setVisible(True)
   

    ##
    def update_bar_chart(self, total):
        if not isinstance(total, list):
            print("❌ خطا: مقدار ورودی برای چارت باید لیست باشد")
            return

        # حذف چارت قبلی اگر وجود داشته باشد و معتبر باشد
        try:
            if hasattr(self, "chart_veiw") and self.chart_veiw is not None:
                self.run_layout.removeWidget(self.chart_veiw)
                self.chart_veiw.deleteLater()
                self.chart_veiw = None  # بعد از حذف، مقداردهی به None
        except RuntimeError:
            print("⛔ چارت قبلی قبلاً حذف شده است")

        # ساخت چارت جدید
        self.chart_veiw = self.create_bar_chart_year(total)
        self.chart_veiw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.run_layout.addWidget(self.chart_veiw)


    ##
    def create_bar_chart_year(self, total: list[float]= None):
        if total is None:
            total = [0, 0, 0, 0, 0, 0, 0]  # یا هر مقدار پیش‌فرض دلخواه
        name_labels = ["کل خریداری", "کل فروشات", "مفاد خالص", "مجموعه برداشت", "مجموعه قرض ها", "سرمایه فعلی", "پول نقد"]
        colors = ["#ff5733", "#33c1ff", "#9b59b6", "#f1c40f", "#e67e22", "#2ecc71", "#e84393"]

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
        chart.setTitle("گزارش سالانه فروشگاه")
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
    def update_bar_chart_year(self, total):
        if not isinstance(total, list):
            print("❌ خطا: مقدار ورودی برای چارت سال باید لیست باشد")
            return

        if self.chart_veiw:
            self.run_layout.removeWidget(self.chart_veiw)
            self.chart_veiw.deleteLater()

        # عنوان سال در چارت اضافه شود
        year_label = f"سال {self.selected_year}" if hasattr(self, "selected_year") else "سال مشخص نیست"
        self.bar_chart_view = self.create_bar_chart_year(total, title=f"گزارش سالانه فروشگاه ({year_label})")
        self.bar_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.run_layout.addWidget(self.bar_chart_view)
    ##
    def create_bar_chart_year(self, total: list[float] = None, title: str = "گزارش سالانه فروشگاه"):
        if total is None:
            total = [0, 0, 0, 0, 0, 0, 0]

        name_labels = ["کل خریداری", "کل فروشات", "مفاد خالص", "مجموعه برداشت", "مجموعه قرض ها", "سرمایه فعلی", "پول نقد"]
        colors = ["#ff5733", "#33c1ff", "#9b59b6", "#f1c40f", "#e67e22", "#2ecc71", "#e84393"]

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
        chart.setTitle(title)
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
    def on_year_selected(self, selected_year):
        if selected_year:
            print(f"📅 سال انتخاب‌شده: {selected_year}")
            self.selected_year = selected_year  # ذخیره سال انتخاب‌شده
            self.show_first_spinner()

  ##

    def hide_run_layout_widgets(self):
        for i in range(self.run_layout.count()):
            item = self.run_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setVisible(False)
    ##
    def update_boxes_thread(self, stats: dict):
        for key, value in stats.items():
            if key in self.val_labels:
                self.val_labels[key].setText(f"{value:,.0f}")
   
    ##
    def update_boxes_year(self, stats: dict):
        for key, value in stats.items():
            if key in self.val_labels:
                self.val_labels[key].setText(f"{value:,.0f} (سالیانه)")

    ##
    def this_year(self, year_selected: str | list):
        self.year_combo.blockSignals(True)  # جلوگیری از سیگنال‌دهی هنگام پر کردن
        self.year_combo.clear()

        # گزینه پیش‌فرض برای انتخاب سال
        self.year_combo.addItem("انتخاب سال")

        # گزینه "همه گزارشات" برای بارگذاری داده کامل
        self.year_combo.addItem("همه گزارشات")

        if isinstance(year_selected, list):
            for y in sorted(year_selected):
                self.year_combo.addItem(y)
            self.selected_year = None
            self.year_combo.setCurrentIndex(0)  # حالت پیش‌فرض "انتخاب سال"
        else:
            self.year_combo.addItem(year_selected)
            self.selected_year = None
            self.year_combo.setCurrentIndex(0)  # هنوز انتخاب نشده، "انتخاب سال"

        self.year_combo.blockSignals(False)
        print(f"سال(ها) {year_selected} به year_combo افزوده شد.")

        # اتصال سیگنال تغییر انتخاب (اگر قبلاً متصل نیست)
        if not self.year_combo.signalsBlocked():
            self.year_combo.currentIndexChanged.connect(self.on_year_changed)

    def on_year_changed(self, index):
        text = self.year_combo.currentText()

        # جلوگیری از اجرا همزمان
        if self.year_thread and self.year_thread.isRunning():
            self.year_thread.quit()
            self.year_thread.wait()

        if text == "همه گزارشات":
            self.selected_year = None
            print("🔄 بارگذاری همه گزارشات (full_data)")
        else:
            self.selected_year = text
            print(f"📅 بارگذاری اطلاعات سال {self.selected_year}")

        QTimer.singleShot(50, self.show_first_spinner)  # نمایش spinner پیش از بارگذاری


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
    

