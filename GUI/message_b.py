from PyQt6.QtWidgets import QMessageBox,QLabel
from PyQt6.QtGui import QFontDatabase,QPixmap
from PyQt6.QtCore import QTimer,QUrl,Qt
from PyQt6.QtMultimedia import QSoundEffect
import os,sys

class MessageBox:
    def __init__(self, text, title="پیام", type="info", buttons=QMessageBox.StandardButton.Ok):
        self.msg = QMessageBox()
        self.type = type  # اینو ذخیره کنیم که بعداً چک کنیم
        self.msg.setWindowTitle(title)
        self.msg.setText(text)
        self.msg.setStandardButtons(buttons)
        self.msg.setWindowFlag(Qt.WindowType.Tool)

        self.msg.setIcon(QMessageBox.Icon.NoIcon)

        self.message_UI()
        self.load_all_fonts()
        self.play_notification()
        self.custo_icons()

    def show(self):
        if self.type == "info":
            # اگر تایپ اینفو بود، تایمر ۵۰۰ میلی ثانیه‌ای ست کن
            QTimer.singleShot(1000, self.msg.accept)  # بعد از ۵۰۰ میلی ثانیه پیام رو ببند
        return self.msg.exec()
    def custo_icons(self):
        try:
            icon_files= {
                "info" : "information_10015217.png",
                "warning" : "warning (1).png",
                "error" : "remove_1828847.png"
            }
            icon_path= self.get_asset_path(icon_files.get(self.type, "information_10015217.png"))
            if icon_path:
                pixmap= QPixmap(icon_path)
                label= QLabel()
                label.setPixmap(pixmap)
                label.setFixedSize(40,40)
                label.setScaledContents(True)
                layout= self.msg.layout()
                layout.addWidget(label,0,0)
            
        except Exception as e:
            print(f"{e}: some problem ocurs")
    
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
        ##images
    
    def play_notification(self):
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # یک فولدر بالاتر از GUI
            sounds_folder = os.path.join(base_path, 'assets', 'sounds')
            print("📂 مسیر صداها:", sounds_folder)

            sound_files = {
                "info": os.path.join(sounds_folder, "info.wav"),
                "warning": os.path.join(sounds_folder, "warning.wav"),
                "error": os.path.join(sounds_folder, "error.wav"),
                "question": os.path.join(sounds_folder, "question.wav"),
            }

            sound_path = sound_files.get(self.type)
            if sound_path and os.path.exists(sound_path):
                # نگه داشتن به صورت attribute تا GC حذفش نکند
                self.sound = QSoundEffect()
                self.sound.setSource(QUrl.fromLocalFile(sound_path))
                self.sound.setVolume(0.9)
                self.sound.play()
            else:
                print(f"⚠ فایل صوتی برای نوع {self.type} یافت نشد: {sound_path}")
        except Exception as e:
            print(f'❌ خطا در پخش صدا: {e}')
    ##images
    def get_asset_path(self, filename):
        try:
            # حالت build شده با PyInstaller
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                # حالت اجرای عادی (Debug/Run)
                base_path = os.path.dirname(self.resource_path(os.path.dirname(os.path.abspath(__file__))))

            image_path = os.path.join(base_path, "assets", filename)

            if os.path.exists(image_path):
                return image_path
            else:
                print(f"⚠ فایل یافت نشد: {image_path}")
                return None
        except Exception as e:
            print(f"❌ خطا در یافتن مسیر: {e}")
            return None
    #
    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    ##fonts
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
    