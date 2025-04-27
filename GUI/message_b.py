from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QTimer
import os

class MessageBox:
    def __init__(self, text, title="پیام", type="info", buttons=QMessageBox.StandardButton.Ok):
        self.msg = QMessageBox()
        self.type = type  # اینو ذخیره کنیم که بعداً چک کنیم
        self.msg.setWindowTitle(title)
        self.msg.setText(text)
        self.msg.setStandardButtons(buttons)

        if type == "info":
            self.msg.setIcon(QMessageBox.Icon.Information)
            self.msg.button(QMessageBox.StandardButton.Ok).setText('باشه')
        elif type == "warning":
            self.msg.setIcon(QMessageBox.Icon.Warning)
            self.msg.button(QMessageBox.StandardButton.Ok).setText('لغو')
        elif type == "error":
            self.msg.setIcon(QMessageBox.Icon.Critical)
        elif type == "question":
            self.msg.setIcon(QMessageBox.Icon.Question)
        else:
            self.msg.setIcon(QMessageBox.Icon.NoIcon)

        self.message_UI()
        self.load_all_fonts()

    def show(self):
        if self.type == "info":
            # اگر تایپ اینفو بود، تایمر ۵۰۰ میلی ثانیه‌ای ست کن
            QTimer.singleShot(500, self.msg.accept)  # بعد از ۵۰۰ میلی ثانیه پیام رو ببند
        return self.msg.exec()

    def message_UI(self):
        self.msg.setStyleSheet('''
            QMessageBox {
                background-color: #d9d9d9;
                font-family: "B Nazanin";
                font-size: 18px;
                font-weight: bold;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-family: "Vazir";
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')

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
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        pass
