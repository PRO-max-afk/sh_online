import ntplib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
import jdatetime
from datetime import datetime, timezone
import os

class JalaliCalendar(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setWindowOpacity(0)
        self.setFixedSize(300, 230)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
        """)

        self.font = QFont("B Nazanin", 12)
        self.setFont(self.font)

        # گرفتن تاریخ شمسی از سرور NTP
        self.current_date = self.get_jalali_from_ntp()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.header_layout = QHBoxLayout()

        self.year_label = QLabel(str(self.current_year))
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_label.setStyleSheet("background-color:transparent;color: black;")
        self.year_label.setFont(QFont("B Nazanin", 14, QFont.Weight.Bold))

        self.month_combo = QComboBox()
        self.month_names = [
            "", "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
        ]
        self.month_combo.addItems(self.month_names[1:])
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.month_combo.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 12px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left;
                width: 30px;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                text-align: left;
                font-family: "B Nazanin";
                font-size: 12px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;
            }
            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }
        ''')
        self.month_combo.currentIndexChanged.connect(self.on_month_changed)

        self.header_layout.addWidget(self.month_combo)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.year_label)
        self.layout.addLayout(self.header_layout)

        self.days_layout = QGridLayout()
        self.days_layout.setHorizontalSpacing(12)
        self.days_layout.setVerticalSpacing(10)
        self.layout.addLayout(self.days_layout)

        self.update_calendar()

    def get_jalali_from_ntp(self):
        try:
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3, timeout=3)
            utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            return jdatetime.datetime.fromgregorian(datetime=utc_time).date()
        except Exception as e:
            print("⚠ خطا در دریافت تاریخ از NTP:", e)
            # گرفتن زمان سیستم کامپیوتر
            local_time = datetime.now()
            return jdatetime.datetime.fromgregorian(datetime=local_time).date()

    def show_with_animation(self, pos):
        self.move(pos)
        self.setWindowOpacity(0)
        self.show()
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

    def hide_with_animation(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.start()

    def on_month_changed(self, index):
        self.current_month = index + 1
        self.update_calendar()

    def update_calendar(self):
        self.year_label.setText(str(self.current_year))

        for i in reversed(range(self.days_layout.count())):
            widget = self.days_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        first_day = jdatetime.date(self.current_year, self.current_month, 1)
        start_col = (first_day.togregorian().weekday() + 1) % 7

        day = 1
        row = 0
        for i in range(start_col, 42):
            try:
                jdatetime.date(self.current_year, self.current_month, day)
            except:
                break

            btn = QPushButton(str(day))
            btn.setFont(QFont("B Nazanin", 11))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    border: 1px solid transparent;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QPushButton:pressed {
                    background-color: #498bf5;
                }
            """)
            btn.clicked.connect(lambda checked, d=day: self.select_day(d))
            self.days_layout.addWidget(btn, row, i % 7)
            day += 1
            if (i + 1) % 7 == 0:
                row += 1

    def select_day(self, day):
        selected = jdatetime.date(self.current_year, self.current_month, day)
        formatted = selected.strftime("%Y/%m/%d")
        self.main_window.set_selected_date(formatted)
        self.hide_with_animation()

    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")

        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return

        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
