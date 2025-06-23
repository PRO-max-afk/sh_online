from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
import jdatetime  # اضافه‌شده برای استفاده در کل کلاس


class MonthSelectorDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedSize(130, 70)
        self.setWindowOpacity(0)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.month_combo = QComboBox()
        self.month_combo.setFont(QFont("B Nazanin", 12))
        self.month_names = [
            "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
        ]
        self.month_combo.addItems(self.month_names)

        # 🔸 تنظیم ماه فعلی شمسی به عنوان پیش‌فرض
        current_jdate = jdatetime.date.today()
        self.current_month = current_jdate.month
        self.current_year = current_jdate.year
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.month_combo.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 14px;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
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
                font-family: "B Nazanin";
                font-size: 12px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #e6f0ff;
                padding: 5px;
                outline: 0;
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

        self.month_combo.currentIndexChanged.connect(self.month_selected)
        layout.addWidget(self.month_combo)

    def show_with_animation(self, pos):
        self.move(pos)
        self.setWindowOpacity(0)
        self.show()
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

    def hide_with_animation(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.start()

    def month_selected(self, index):
        selected_month = index + 1
        formatted = f"{self.current_year}/{selected_month:02d}"
        #self.main_window.set_selected_date(formatted)
        self.hide_with_animation()
