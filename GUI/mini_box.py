from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFont, QColor,QFontDatabase
from PyQt6.QtCore import Qt
import os

class MniniBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(270, 100)
        self.setMaximumSize(270, 100)
        self.setStyleSheet("background-color: transparent;")
        self.load_all_fonts()

        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, 270, 100)
        self.frame.setStyleSheet("background-color: white; border-radius: 20px;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.frame.setGraphicsEffect(shadow)

        # آیکون محصول (چپ)
        self.icon_label = QLabel(self.frame)
        self.icon_label.setGeometry(10, 20, 60, 60)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # عدد (بالا)
        self.number_label = QLabel("0", self.frame)
        self.number_label.setGeometry(80, 15, 180, 35)
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.number_label.setStyleSheet("color: black; font-family: PoetsenOne; font-size: 14px;")


        # متن توضیحی (پایین)
        self.text_label = QLabel("محصولات تمام شده", self.frame)
        self.text_label.setGeometry(80, 50, 180, 35)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.text_label.setStyleSheet("color: gray; font-family: B Nazanin; font-size: 12px;")

        # آیکون پیش‌فرض
        default_icon_path = "default.png"
        if os.path.exists(default_icon_path):
            self.set_icon(default_icon_path)

    def set_product_info(self, number: int):
        self.number_label.setText(str(number))

    def set_icon(self, image_path: str):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
     ##fonts
    ##
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
