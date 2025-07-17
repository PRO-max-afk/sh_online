import os
from datetime import datetime, timezone, date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QSpinBox
)
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ntp_miladi import  GregorianNTPThread  

class Calendar(QDialog):
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

        self.font = QFont("Roboto", 12)
        self.setFont(self.font)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.header_layout = QHBoxLayout()

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(1900, 2100)
        self.year_spinbox.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        self.year_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.year_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: transparent;
                border: none;
                color: black;
            }
        """)
        self.year_spinbox.valueChanged.connect(self.on_year_changed)

        self.month_combo = QComboBox()
        self.month_names = ["", "January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(self.month_names[1:])
        self.month_combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.month_combo.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "Roboto";
                font-size: 12px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: left;
                padding: 6px 10px 6px 30px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left;
                width: 30px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                font-family: "Roboto";
                font-size: 12px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #e6f0ff;
                padding: 5px;
                outline: 0;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 2px 0 2px 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #a8a8a8;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7a7a7a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        ''')
        self.month_combo.currentIndexChanged.connect(self.on_month_changed)

        self.header_layout.addWidget(self.month_combo)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.year_spinbox)
        self.layout.addLayout(self.header_layout)

        self.days_layout = QGridLayout()
        self.days_layout.setHorizontalSpacing(12)
        self.days_layout.setVerticalSpacing(10)
        self.layout.addLayout(self.days_layout)

        self.load_all_fonts()

        # 🚀 اجرای ترد برای گرفتن تاریخ از NTP
        self.ntp_thread = GregorianNTPThread()
        self.ntp_thread.finished.connect(self.on_date_ready)
        self.ntp_thread.start()

    def on_date_ready(self, dt):
        self.current_date = dt
        self.current_year = dt.year
        self.current_month = dt.month
        self.year_spinbox.setValue(self.current_year)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.update_calendar()

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

    def on_year_changed(self, year):
        self.current_year = year
        self.update_calendar()

    def update_calendar(self):
        self.year_spinbox.setValue(self.current_year)

        for i in reversed(range(self.days_layout.count())):
            widget = self.days_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            first_day = date(self.current_year, self.current_month, 1)
        except ValueError:
            return

        start_col = (first_day.weekday() + 1) % 7
        day = 1
        row = 0

        for i in range(start_col, 42):
            try:
                date(self.current_year, self.current_month, day)
            except:
                break

            btn = QPushButton(str(day))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    font-family: Roboto;
                    font-size: 11;
                    font-weight: black;
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
        selected = date(self.current_year, self.current_month, day)
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
