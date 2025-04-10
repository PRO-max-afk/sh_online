from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QLineEdit,QPushButton,QMainWindow
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint,QEasingCurve
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFontDatabase, QPalette, QFont,QColor,QIcon
import os
from PyQt6 import QtCore
import sys
from new_password import New_login

class Verify_login(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.x(), screen.y(), screen.width(), screen.height())
        # اینجا ابعاد حداقلی تعیین می‌کنیم ولی اجازه resize می‌دیم
        self.setMinimumSize(1200, 600)
        self.setWindowTitle("برنامه فروشگاه")
        self.setStyleSheet("background-color: #D9D9D9;")
        
         # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ----- layout اصلی عمودی -----
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # تنظیم layout روی ویجت مرکزی
        central_widget.setLayout(main_layout)

        # ----- layout افقی بالا -----
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # --- تصویر سمت چپ ---
        self.img_label = QLabel()
        self.img_label.setFixedSize(700, 700)
        image_path = self.get_asset_path("Enter OTP-cuate 1.png")
        if image_path:
            pixmap = QPixmap(image_path)
            self.img_label.setPixmap(pixmap.scaled(self.img_label.size()))
        else:
            self.img_label.setText("تصویر یافت نشد.")

        # --- فریم سمت راست ---
        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: white;")
        self.frame.setFixedSize(550, screen.height() + 30)

        # --- اضافه کردن به layout افقی ---
        top_layout.addWidget(self.img_label)
        top_layout.addStretch()  # اسپیس بین عکس و فریم
        top_layout.addWidget(self.frame)

        # اضافه به layout اصلی
        main_layout.addLayout(top_layout)
        self.setLayout(main_layout)
        
        # ایجاد layout برای man و title
        man_icon = self.get_asset_path("mobile_15702851 1.png")
        self.manlabel = QLabel()
        self.manlabel.setFixedSize(100, 100)
        self.manlabel.setContentsMargins(0, 0, 0, 0)

        # layout عمودی man و title
        man_layout = QVBoxLayout()
        man_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        # layout افقی برای جابجایی عکس
        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_row.addSpacing(40)  # تنظیم میزان حرکت به راست
        icon_row.addWidget(self.manlabel)

        # اضافه کردن به layout کلی
        man_layout.addLayout(icon_row)

        # بارگذاری تصویر آیکون
        if man_icon:
            man_pix = QPixmap(man_icon)
            self.manlabel.setPixmap(man_pix.scaled(self.manlabel.size()))
        else:
            self.manlabel.setText("تصویر یافت نشد")

        # ایجاد layout برای فیلدهای ورودی
        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # اضافه کردن label برای نام کاربری
        self.username_label = QLabel(":کد")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی نام کاربری
        self.username_input = self.create_verification_inputs()


     
        # دکمه ورود
        icon_path = self.get_asset_path("back.png")
        icon = QIcon(icon_path)

        self.submit_btn = QPushButton("تایید")
        self.submit_btn.clicked.connect(self.show_new_login_fullscreen)
        self.back_btn = QPushButton()
        self.back_btn.setIcon(icon)
        self.back_btn.setIconSize(QtCore.QSize(40, 40))
        self.back_btn.setText(" برگشت")
        self.back_btn.clicked.connect(self.show_otp_login_fullscreen)

        # لایه اصلی دکمه‌ها
        button_layout = QHBoxLayout()

        # اضافه کردن back_btn به سمت چپ
        button_layout.addWidget(self.back_btn)

        # Spacer برای قرار دادن submit_btn در مرکز
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # اضافه کردن submit_btn در مرکز
        button_layout.addWidget(self.submit_btn)

        # Spacer دیگر برای متعادل‌سازی سمت راست (در صورت نیاز)
        button_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # ست کردن alignment کل layout (اختیاری)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #
        self.lb= QLabel("")
        self.n_lb= QLabel("")
        self.note_lb= QLabel("بعداز دریافت پیام، کد را وارد کنید")
        self.help_lb= QLabel("")
        self.lbe= QLabel("")
        self.n_lbe= QLabel("")
        self.no_lb= QLabel("")
        
        
        # اضافه کردن لیبل‌ها و فیلدهای ورودی به input_layout
        self.input_layout.addWidget(self.username_label)
        self.input_layout.setSpacing(20)
        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.lb)
        self.input_layout.addWidget(self.n_lb)
        self.input_layout.addWidget(self.note_lb)
        self.input_layout.addWidget(self.help_lb)
        self.input_layout.addWidget(self.no_lb)
        #self.input_layout.addWidget(self.lbe)
        #self.input_layout.addWidget(self.n_lbe)
        # اضافه کردن دکمه به layout اصلی
        self.input_layout.addLayout(button_layout)

        # ایجاد اسپیس برای قرار دادن فیلدها در وسط
        spacer_top = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        spacer_bottom = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # ایجاد layout برای فریم که شامل فقط input_layout باشد
        frame_layout = QVBoxLayout(self.frame)
        
        # اضافه کردن man_layout به بالای فریم
        frame_layout.addLayout(man_layout)
        
        # اضافه کردن اسپیس‌ها و input_layout در فریم
        frame_layout.addItem(spacer_top)  # اسپیس بالای فیلدهای ورودی
        frame_layout.addLayout(self.input_layout)  # اضافه کردن input_layout
        frame_layout.addItem(spacer_bottom)  # اسپیس پایین فیلدهای ورودی

        # تنظیم layout به فریم
        self.frame.setLayout(frame_layout)

        self.InUI()
        self.load_all_fonts()
    
    def InUI(self):

        self.username_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:30px;")
        self.note_lb.setFixedHeight(30)
        self.note_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            font-family: Mirza;
            text-align: right;
            margin-right: 20px;
            ''')
        

        # تنظیم ویژگی‌های دکمه
        self.submit_btn.setFixedSize(140, 50)

        # تعریف استایل برای دکمه
        self.submit_btn.setStyleSheet('''
            QPushButton {
                background-color: #2251DB;
                font-family: "B Nazanin";
                font-size: 21px;
                font-weight: bold;
                border-radius: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed{
                background-color: #2251DB;
                                      }
        ''')
        #back_btn
        self.back_btn.setStyleSheet('''
        background-color: white;
        font-size:16px;
        font-family:Mirza;
        color:black;
        font-weight:bold;
            ''')        
    ##
    def create_verification_inputs(self):
        container = QWidget(self)
        container.setFixedSize(500, 60)

        layout = QHBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 5, 20, 5)

        self.code_inputs = []

        for i in range(6):
            code_input = QLineEdit()
            code_input.setMaxLength(1)
            code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            code_input.setFont(QFont("Arial", 18))
            code_input.setFixedSize(50, 50)
            code_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #7b8db0;
                    border-radius: 6px;
                    background-color: white;
                    color:black;
                }
                QLineEdit:focus {
                    border: 2px solid #2251DB;
                }
            """)

            # سایه
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setXOffset(0)
            shadow.setYOffset(0)
            shadow.setColor(QColor(0, 0, 0, 40))
            code_input.setGraphicsEffect(shadow)

            # Event سفارشی
            code_input.installEventFilter(self)

            self.code_inputs.append(code_input)
            layout.addWidget(code_input)

        return container
    ##
    def eventFilter(self, source, event):
        if isinstance(source, QLineEdit) and event.type() == event.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Backspace:
                for input_field in self.code_inputs:
                    input_field.clear()
                self.code_inputs[0].setFocus()
                return True
            elif source.text():
                index = self.code_inputs.index(source)
                if index < len(self.code_inputs) - 1:
                    self.code_inputs[index + 1].setFocus()
                return True
        return super().eventFilter(source, event)

    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
     ##animated
    ##animated
    def show_new_login_fullscreen(self):
        # پاک کردن محتوای فعلی پنجره
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # ایجاد یک نمونه از Security_login به‌صورت ویجت (نه پنجره‌ی جدید)
        new_widget = New_login()  # توجه: کلاس باید از QWidget ارث ببرد نه QMainWindow

        self.setCentralWidget(new_widget)

        # انیمیشن اسلاید از راست
        start_pos = QPoint(self.width(), 0)
        end_pos = QPoint(0, 0)
        new_widget.move(start_pos)

        self.anim = QPropertyAnimation(new_widget, b"pos", self)
        self.anim.setDuration(600)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
     ##animated
    #
    def show_otp_login_fullscreen(self):
        from otp_security import Otp_login
        # پاک کردن محتوای فعلی پنجره
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # ایجاد یک نمونه از Security_login به‌صورت ویجت (نه پنجره‌ی جدید)
        otp_widget = Otp_login()  # توجه: کلاس باید از QWidget ارث ببرد نه QMainWindow

        self.setCentralWidget(otp_widget)

        # انیمیشن اسلاید از چپ
        start_pos = QPoint(-self.width(), 0)
        end_pos = QPoint(0, 0)
        otp_widget.move(start_pos)

        self.anim = QPropertyAnimation(otp_widget, b"pos", self)
        self.anim.setDuration(600)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Verify_login()
    window.show()
    sys.exit(app.exec())

