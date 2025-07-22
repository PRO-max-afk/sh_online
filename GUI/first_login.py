from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QLineEdit,QPushButton,QMainWindow,QApplication
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint,QEasingCurve
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFontDatabase, QPalette, QFont,QColor
import os
import sys
from security_qustion import Security_login
from message_b import MessageBox
import sqlite3
import pymysql
import ntplib
import pytz
from datetime import datetime



class Main_login(QMainWindow):
    def __init__(self):
        super().__init__()

        # تنظیمات پنجره
        screen = QApplication.instance().primaryScreen().geometry()
        self.setGeometry(screen.x(), screen.y(), screen.width(), screen.height())
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
        self.img_label.setFixedSize(750, 750)
        image_path = self.get_asset_path("first_img.png")
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
        man_icon = self.get_asset_path("man_1.png")
        self.manlabel = QLabel()
        self.manlabel.setFixedSize(100, 100)
        self.manlabel.setContentsMargins(0, 0, 0, 0)

        # ساخت لیبل عنوان
        self.title_label = QLabel("ورود به سیستم فروشگاه")
        self.title_label.setFixedHeight(40)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.title_label.setContentsMargins(0, -3, 0, 0)

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
        man_layout.addWidget(self.title_label)

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
        self.username_label = QLabel("نام کاربری")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی نام کاربری
        self.username_input = self.create_floating_input("username")

        # اضافه کردن label برای رمز عبور
        self.password_label = QLabel("رمز عبور")
        self.password_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی رمز عبور
        self.password_input = self.create_floating_input("password")
        self.ne_lb= QLabel("")
        # دکمه ورود
        self.submit_btn = QPushButton("ورود به حساب")

        # برای وسط چین کردن دکمه، آن را داخل یک QHBoxLayout قرار می‌دهیم
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # مرکز چین کردن دکمه
        #
        self.forgot_btn= QPushButton("پسورد خود را فراموش کردید")
        self.forgot_btn.clicked.connect(self.show_security_login_fullscreen)
        
        # ایجاد layout افقی برای دکمه "فراموشی پسورد"
        forgot_password_layout = QHBoxLayout()
        forgot_password_layout.addWidget(self.forgot_btn)
        
        
        # اضافه کردن لیبل‌ها و فیلدهای ورودی به input_layout
        self.input_layout.addWidget(self.username_label)
        self.input_layout.setSpacing(20)
        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.password_label)
        self.input_layout.addWidget(self.password_input)
        self.input_layout.addWidget(self.ne_lb)
        # اضافه کردن دکمه به layout اصلی
        self.input_layout.addLayout(button_layout)
        self.input_layout.addLayout(forgot_password_layout)

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
        self.db_data= self.get_db_config()
        self.load_all_fonts()
        
    
    def InUI(self):
        ##label
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            font-family: Mirza;
        """)
        self.username_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:15px;")
        self.password_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:15px;")    
        # تنظیم ویژگی‌های دکمه
        self.submit_btn.setFixedSize(140, 50)
        self.submit_btn.clicked.connect(self.user_login)
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
        #forgot_btn
        self.forgot_btn.setFixedSize(160,30)
        self.forgot_btn.setStyleSheet('''
            QPushButton{
                background-color:white;
                font-family: B Nazanin;
                font-weight:bold;
                color: #2251DB;
                font-size: 16px;
                border: none;
                text-decoration: underline;}
            
            QPushButton:hover{
                background-color:white;
                                      }
            QPushButton:pressed{
                background-color:white;
                                      }
        ''')

    ##inputs 
    def create_floating_input(self, placeholder_text):
        container = QWidget(self)
        container.setFixedSize(500, 50)
        container.setStyleSheet("background: transparent;")

        # ایجاد LineEdit
        line_edit = QLineEdit(container)
        line_edit.setFixedSize(500, 50)

        # اگر فیلد رمز عبور بود، حالت نمایش را مخفی کن
        if placeholder_text.lower() == "password":
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        line_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: 2px solid gray;
                padding: 10px;
                font-size: 14px;
                outline: none;
                color: black;
                border-radius: 7px;
                margin-left: 10px;
            }
            QLineEdit:hover {
                border: 2px solid #2251DB;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        line_edit.setGraphicsEffect(shadow)

        palette = line_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
        line_edit.setPalette(palette)

        label = QLabel(placeholder_text, container)
        label.setFont(QFont("Roboto", 16))
        label.setStyleSheet("""
            color: gray;
            background: white;
            padding: 0 5px;
            font-size: 16px;
            font-family: Roboto;
            font-style: bold;
            position: absolute;
            text-align: center;
            left: 10px;
            top: 12px;
            border-radius: 7px;
            margin-left: 10px;
            width: calc(100% - 20px);
        """)
        label.move(10, 12)

        line_edit.installEventFilter(self)
        label._original_pos = label.pos()

        animation = QPropertyAnimation(label, b"pos")
        animation.setDuration(150)

        line_edit._floating_label = label
        line_edit._floating_animation = animation
        line_edit.textChanged.connect(lambda: self.update_label_visibility(label, line_edit))

        # ذخیره LineEdit در container برای دسترسی راحت‌تر
        container.line_edit = line_edit
        return container

    def eventFilter(self, obj, event):
        if isinstance(obj, QLineEdit):
            label = obj._floating_label
            animation = obj._floating_animation
            if event.type() == event.Type.FocusIn:
                self.move_label(label, animation, up=True)
                obj.setStyleSheet("""
                    QLineEdit {
                        background: transparent;
                        border: 2px solid #2251DB;  /* تغییر رنگ مرز هنگام focus */
                        padding: 10px;
                        font-size: 14px;
                        border-radius: 7px;
                        outline: none;
                        color: black;
                        margin-left: 10px;
                    }
                """)
            elif event.type() == event.Type.FocusOut:
                if not obj.text():
                    self.move_label(label, animation, up=False)
                obj.setStyleSheet("""
                    QLineEdit {
                        background: transparent;
                        border: 2px solid gray;  /* مرز پیش‌فرض */
                        padding: 10px;
                        font-size: 14px;
                        outline: none;
                        color: black;
                        margin-left: 10px;
                        border-radius: 7px;  /* گوشه‌های گرد */
                    }
                """)
        return super().eventFilter(obj, event)

    def move_label(self, label, animation, up):
        if up:
            animation.setStartValue(label.pos())
            animation.setEndValue(QPoint(label.x(), label.y() - 15))
            label.setStyleSheet("color: #2251DB; text-align: center; font-size: 10px; background: white; padding: 5px 2px; text-decoration: underline; margin-left: 10px;")
        else:
            animation.setStartValue(label.pos())
            animation.setEndValue(label._original_pos)
            label.setStyleSheet("color: gray; text-align: center; font-size: 12px; background: white; padding: 0 5px; margin-left: 10px;")
        animation.start()

    def update_label_visibility(self, label, line_edit):
        """این متد برای اطمینان از نمایش صحیح label وقتی متن وارد می‌شود یا فیلد تغییر می‌کند"""
        if line_edit.text():  # اگر متنی وارد شده باشد، label باید ثابت باشد
            label.setStyleSheet("color: #2251DB; text-align: center; font-size: 10px; background: white; padding: 0 5px; text-decoration: underline; margin-left: 10px;")
        else:  # اگر فیلد خالی است، label باید در موقعیت اصلی خود باشد
            label.setStyleSheet("color: gray; text-align: center; font-size: 12px; background: white; padding: 0 5px; margin-left: 10px;")
    ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.user_login()
    ##
    def open_mainwindow_with_animation(self):
        from main import mainwindow
        self.new_window = mainwindow()  # ساخت نمونه‌ای از صفحه اصلی
        self.new_window.setWindowOpacity(0)  # شفافیت اولیه صفر

        self.new_window.showMaximized()  # تمام صفحه باز شود

        self.animation = QPropertyAnimation(self.new_window, b"windowOpacity")
        self.animation.setDuration(500)  # زمان انیمیشن
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

        self.close()  # بستن صفحه لاگین

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
    def show_security_login_fullscreen(self):
        # پاک کردن محتوای فعلی پنجره
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # ایجاد یک نمونه از Security_login به‌صورت ویجت (نه پنجره‌ی جدید)
        security_widget = Security_login()  # توجه: کلاس باید از QWidget ارث ببرد نه QMainWindow

        self.setCentralWidget(security_widget)

        # انیمیشن اسلاید از راست
        start_pos = QPoint(self.width(), 0)
        end_pos = QPoint(0, 0)
        security_widget.move(start_pos)

        self.anim = QPropertyAnimation(security_widget, b"pos", self)
        self.anim.setDuration(800)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
    ##
    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    # دریافت اطلاعات دیتابیس از سرور
    def get_db_config(self):
        import requests

        url = "https://aryaict.com/connect.php"

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        cookies = {
            'humans_21909': '1'
        }

        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=60)

            if response.status_code != 200:
                print("⚠️ خطای ارتباطی:", response.status_code, response.text)
                response.raise_for_status()

            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست! محتوای پاسخ:\n" + response.text)

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است:\n" + str(data))

            return data

        except Exception as e:
            print("❌ خطا در دریافت کانفیگ:", e)
            return None

    ## 
    def user_login(self):
        username = self.username_input.line_edit.text()
        password = self.password_input.line_edit.text()

        if not username or not password:
            MessageBox(text="تمامی فیلد ها را پر کنید", title="⚠هشدار", type="warning").show()
            return False

        if not self.db_data:
            MessageBox(text="لطفاً اینترنت خود را بررسی کنید❌ اتصال به سرور ناموفق بود", title="❌خطا", type="error").show()
            return False

        conn = None
        cursor = None
        conn_sq = None
        cursor_sq = None
        id_s= None

        try:
            try:
                # دریافت زمان از NTP سرور
                ntp_client = ntplib.NTPClient()
                response = ntp_client.request('pool.ntp.org', version=3)
                utc_time = datetime.utcfromtimestamp(response.tx_time)

            except Exception as e:
                # اگر نتوانست دریافت کند، از زمان سیستم استفاده کند
                print(f"NTP Server error: {e}, using local system time instead.")
                utc_time = datetime.utcnow()

            # ادامه کار
            kabul_tz = pytz.timezone('Asia/Kabul')
            kabul_time = pytz.utc.localize(utc_time).astimezone(kabul_tz)
            expire_date = kabul_time.strftime('%Y-%m-%d %H:%M:%S')

            # اتصال به دیتابیس اصلی (MySQL)
            conn = pymysql.connect(
                host=self.db_data["host"],
                user=self.db_data["user"],
                password=self.db_data["password"],
                database=self.db_data["database"]
            )
            cursor = conn.cursor()

            # چک کردن اطلاعات کاربر
            cursor.execute("""
                SELECT id, username, password, expirition_dates 
                FROM user_s 
                WHERE username = %s 
                AND password = %s 
                AND expirition_dates > %s
            """, (username, password, expire_date))

            result = cursor.fetchone()

            if result:
                id_s= result[0]

                base_dir = os.path.dirname(os.path.abspath(__file__))
                # رفتن یک سطح بالاتر از پوشه GUI
                root_dir = os.path.dirname(base_dir)
                db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

                if not os.path.exists(db_path):
                    MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                    return False

                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()

                # اطمینان از وجود فقط یک ردیف در جدول users
                cursor_sq.execute("DELETE FROM users")
                cursor_sq.execute("INSERT INTO users (id) VALUES(?)", (id_s,))


                conn_sq.commit()
                MessageBox(text="ورود با موفقیت انجام شد ✅", title="✅ موفقانه", type="info").show()
                self.open_mainwindow_with_animation()
                # ادامه عملیات ورود...
            else:
                MessageBox(text="نام کاربری یا رمز عبور اشتباه است یا حساب منقضی شده است", title="⚠ خطا", type="warning").show()

        except pymysql.Error as e:
            MessageBox(text=f"{e}: خطا در اتصال به دیتابیس", title="❌ خطا", type="error").show()
        except ntplib.NTPException as e:
            MessageBox(text=f"{e}: خطا در دریافت زمان از NTP", title="❌ خطا", type="error").show()
        except Exception as e:
            MessageBox(text=f"{e}: خطای غیرمنتظره", title="❌ خطا", type="error").show()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            if cursor_sq:
                cursor_sq.close()
            if conn_sq:
                conn_sq.close()

    
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_login()
    window.show()
    sys.exit(app.exec())

