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
    def __init__(self, message, parent_frame):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        self.timestamp = datetime.now()
        self.setFixedHeight(70)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()

        # محاسبه موقعیت و اندازه اعلان
        parent_width = parent_frame.width()
        notif_width = min(400, parent_width - 40)
        x_pos = (parent_width - notif_width) // 2
        self.setGeometry(x_pos, -80, notif_width, 70)

        # فریم اصلی داخل اعلان برای پس‌زمینه سفید
        inner_frame = QFrame(self)
        inner_frame.setGeometry(0, 0, notif_width, 70)
        inner_frame.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
        """)

        # آیکون سمت راست
        icon_label = QLabel()
        pixmap = QPixmap(self.get_asset_path("time_16601996.png")).scaled(30, 30, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(35,35)

        # پیام و زمان در layout عمودی
        text_label = QLabel(message)
        text_label.setStyleSheet('''
        color: black;
        font-family: Vazir;
        font-weight: bold;
        font-size: 13px;
        ''')
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.time_label = QLabel(relative_time_string(self.timestamp))
        #self.time_label.setFont(QFont("", 9))
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
        message_layout.addWidget(text_label)
        message_layout.addWidget(self.time_label)

        # چیدمان افقی نهایی
        layout = QHBoxLayout(inner_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        layout.addLayout(message_layout)
        layout.addWidget(icon_label)

        # انیمیشن ظاهر شدن
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(x_pos, -80, notif_width, 70))
        self.animation.setEndValue(QRect(x_pos, 20, notif_width, 70))
        self.animation.start()

        # بروزرسانی زمان هر 30 ثانیه
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(30000)  # 30 ثانیه

        # ناپدید شدن بعد از چند ثانیه
        QTimer.singleShot(2000, self.hide_notification)

    def update_time_label(self):
        self.time_label.setText(relative_time_string(self.timestamp))

    def hide_notification(self):
        x_pos = self.x()
        self.animation.setStartValue(QRect(x_pos, 20, self.width(), 70))
        self.animation.setEndValue(QRect(x_pos, -80, self.width(), 70))
        self.animation.start()
        QTimer.singleShot(500, self.close)
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ###
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
    ##


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("برنامه فروشگاه")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        button = QPushButton("نمایش اعلان")
        button.clicked.connect(self.show_notification)
        layout.addWidget(button)

        # فریم ویژه اعلان‌ها
        self.notification_frame = QFrame(self)
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.raise_()

    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)

    def show_notification(self):
        notif = Notification("محصول جدید به فروشگاه اضافه شد!", self.notification_frame)
        notif.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
