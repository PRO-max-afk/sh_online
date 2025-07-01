from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
import os
import sqlite3
from message_b import MessageBox
from app_signals import global_signals  # ✅ نمونه‌ی درست

class ProfileImage(QLabel):
    def __init__(self, size=80, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background-color: transparent;")

        self.load_image_from_db()

        # ✅ اتصال به سیگنال مشترک
        global_signals.logo_updated.connect(self.load_image_from_db)

    def load_image_from_db(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT image FROM logo LIMIT 1")
            result = cursor.fetchone()
            conn.close()

            if result:
                image_data = result[0]
                image_path = "temp_profile_logo.png"
                with open(image_path, "wb") as f:
                    f.write(image_data)
                self.update_image(image_path)

        except Exception as e:
            print("❌ خطا در بارگذاری عکس پروفایل:", e)

    def update_image(self, image_path):
        if not image_path or not os.path.exists(image_path):
            print("📛 تصویر یافت نشد:", image_path)
            return
        pixmap = QPixmap(image_path).scaled(self.size, self.size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        rounded = QPixmap(self.size, self.size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self.size, self.size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.setPixmap(rounded)
