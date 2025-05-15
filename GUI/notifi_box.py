from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel,
    QHBoxLayout, QFrame, QPushButton
)
from PyQt6.QtCore import QTimer, QRect, QPropertyAnimation, Qt
from PyQt6.QtGui import QFont, QPixmap,QColor,QFontDatabase
from datetime import datetime
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
import sys
import os


def relative_time_string(past_time):
    now = datetime.now()
    diff = now - past_time

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "لحظاتی پیش"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقیقه پیش"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ساعت پیش"
    else:
        days = seconds // 86400
        return f"{days} روز پیش"


class Notification(QWidget):
    def __init__(self, pro_name,message, parent_frame, icon_path=None):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        self.timestamp = datetime.now()
        self.setFixedHeight(70)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()

        parent_width = parent_frame.width()
        notif_width = min(400, parent_width - 40)
        x_pos = (parent_width - notif_width) // 2
        self.setGeometry(x_pos, -80, notif_width, 70)

        inner_frame = QFrame(self)
        inner_frame.setGeometry(0, 0, notif_width, 70)
        inner_frame.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
        """)

        # پیام و زمان و نام محصول
        name_lb= QLabel(pro_name)
        name_lb.setStyleSheet('''
        color: black;
        font-family: B Nazanin;
        font-weight: bold;
        font-size: 14px;
        font-weight: bold;
        ''')
        name_lb.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        ##
        text_label = QLabel(message)
        text_label.setStyleSheet('''
        color: black;
        font-family: Vazir;
        font-weight: bold;
        font-size: 13px;
        ''')
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.time_label = QLabel(relative_time_string(self.timestamp))
        self.time_label.setStyleSheet('''
            color: gray;
            font-family: B Nazanin;
            font-weight: bold;
            font-size: 11px;
        ''')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        message_layout = QVBoxLayout()
        message_layout.setSpacing(1)
        message_layout.setContentsMargins(0, 8, 0, 8)
        message_layout.addWidget(name_lb)
        message_layout.addWidget(text_label)
        message_layout.addWidget(self.time_label)

        # چیدمان افقی نهایی
        layout = QHBoxLayout(inner_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        layout.addLayout(message_layout)

        # فقط اگر آیکون داده شده باشد
        if icon_path:
            pixmap = QPixmap(icon_path).scaled(30, 30, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(35, 35)
            layout.addWidget(icon_label)

        # انیمیشن
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(x_pos, -80, notif_width, 70))
        self.animation.setEndValue(QRect(x_pos, 20, notif_width, 70))
        self.animation.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(30000)

        QTimer.singleShot(4000, self.hide_notification)

    def update_time_label(self):
        self.time_label.setText(relative_time_string(self.timestamp))

    def hide_notification(self):
        x_pos = self.x()
        self.animation.setStartValue(QRect(x_pos, 20, self.width(), 70))
        self.animation.setEndValue(QRect(x_pos, -80, self.width(), 70))
        self.animation.start()
        QTimer.singleShot(500, self.close)

    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None

    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")
        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return
        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf", ".TTF")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")

