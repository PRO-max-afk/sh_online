from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QLineEdit,QPushButton,QMainWindow
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint,QEasingCurve
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFontDatabase, QPalette, QFont,QColor
import os,sys,pymysql,sqlite3
from message_b import MessageBox
from db_connection_f import Connection
from main import mainwindow

class New_login(QMainWindow):
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
        self.img_label.setFixedSize(750, 750)
        image_path = self.get_asset_path("Secure login-rafiki 1.png")
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
        #self.setLayout(main_layout)
        
        # ایجاد layout برای man و title
        man_icon = self.get_asset_path("protect 1.png")
        self.manlabel = QLabel()
        self.manlabel.setFixedSize(100, 100)
        self.manlabel.setContentsMargins(0, 0, 0, 0)

        # ساخت لیبل عنوان
        self.title_label = QLabel("پسورد جدید")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.title_label.setContentsMargins(40, -3, 0, 0)

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
        self.username_label = QLabel("رمز عبور جدید")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی نام کاربری
        self.username_input = self.create_floating_input("new password")

        # اضافه کردن label برای رمز عبور
        self.password_label = QLabel("تایید رمز عبور")
        self.password_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی رمز عبور
        self.password_input = self.create_floating_input("confirm password")
        self.ne_lb= QLabel("نوت: به یاد داشته باشید که پسورد جدید خود را ذخیره کنید تا که حساب شما ایمن باشد.")
        # دکمه ورود
        self.submit_btn = QPushButton("تایید")
        #self.submit_btn.clicked.connect(self.show_verify_login_fullscreen)

        # برای وسط چین کردن دکمه، آن را داخل یک QHBoxLayout قرار می‌دهیم
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # مرکز چین کردن دکمه
                
        # اضافه کردن لیبل‌ها و فیلدهای ورودی به input_layout
        self.input_layout.addWidget(self.username_label)
        self.input_layout.setSpacing(20)
        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.password_label)
        self.input_layout.addWidget(self.password_input)
        self.input_layout.addWidget(self.ne_lb)
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
        ##label
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            font-family: Mirza;
        """)
        self.title_label.setFixedHeight(30)
        self.username_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:30px;")
        self.password_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:30px;")    
        self.ne_lb.setFixedSize(500,40)
        self.ne_lb.setStyleSheet("font-size: 15px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:0px;")
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
       

    ##inputs 
    def create_floating_input(self, placeholder_text):
        container = QWidget(self)
        container.setFixedSize(500, 50)
        container.setStyleSheet("background: transparent;")

        # ایجاد LineEdit
        line_edit = QLineEdit(container)
        line_edit.setFixedSize(500, 50)
        line_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: 2px solid gray;
                padding: 10px;
                font-size: 14px;
                outline: none;
                color: black;
                border-radius: 7px;
                margin-left: 20px;
            }
            QLineEdit:hover {
                border: 2px solid #2251DB;
            }
        """)

        # افزودن سایه به LineEdit با radius هماهنگ
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)  # نرمی سایه دقیقاً اندازه radius
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))  # سایه مشکی ملایم با شفافیت
        line_edit.setGraphicsEffect(shadow)

        # شفاف کردن پس‌زمینه QLineEdit
        palette = line_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
        line_edit.setPalette(palette)

        # ایجاد لیبل داخل LineEdit
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
            margin-left: 20px;
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
                        margin-left: 20px;
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
                        margin-left: 20px;
                        border-radius: 10px;  /* گوشه‌های گرد */
                    }
                """)
        return super().eventFilter(obj, event)

    def move_label(self, label, animation, up):
        if up:
            animation.setStartValue(label.pos())
            animation.setEndValue(QPoint(label.x(), label.y() - 15))
            label.setStyleSheet("color: #2251DB; text-align: center; font-size: 10px; background: white; padding: 5px 2px; text-decoration: underline; margin-left: 20px;")
        else:
            animation.setStartValue(label.pos())
            animation.setEndValue(label._original_pos)
            label.setStyleSheet("color: gray; text-align: center; font-size: 12px; background: white; padding: 0 5px; margin-left: 20px;")
        animation.start()

    def update_label_visibility(self, label, line_edit):
        """این متد برای اطمینان از نمایش صحیح label وقتی متن وارد می‌شود یا فیلد تغییر می‌کند"""
        if line_edit.text():  # اگر متنی وارد شده باشد، label باید ثابت باشد
            label.setStyleSheet("color: #2251DB; text-align: center; font-size: 10px; background: white; padding: 0 5px; text-decoration: underline; margin-left: 20px;")
        else:  # اگر فیلد خالی است، label باید در موقعیت اصلی خود باشد
            label.setStyleSheet("color: gray; text-align: center; font-size: 12px; background: white; padding: 0 5px; margin-left: 20px;")
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
    def show_verify_login_fullscreen(self):
        # پاک کردن محتوای فعلی پنجره
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # ایجاد یک نمونه از Security_login به‌صورت ویجت (نه پنجره‌ی جدید)
        main_widget = mainwindow()  # توجه: کلاس باید از QWidget ارث ببرد نه QMainWindow

        self.setCentralWidget(main_widget)

        # انیمیشن اسلاید از راست
        start_pos = QPoint(self.width(), 0)
        end_pos = QPoint(0, 0)
        main_widget.move(start_pos)

        self.anim = QPropertyAnimation(main_widget, b"pos", self)
        self.anim.setDuration(1000)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()#   
    ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.update_password()
    ##
    def update_password(self):
        self.db_data = Connection().get_connection()
        old_password = str(self.username_input.line_edit.text()).strip()
        new_password = str(self.password_input.line_edit.text()).strip()

        if not all([old_password, new_password]):
            MessageBox(
                text="لطفاً برای تغییر پسورد، پسورد مورد نظر خود را وارد کنید",
                type="warning",
                title="هشدار"
            ).show()
            return

        if not self.db_data:
            print("خطا در اتصال به دیتابیس")
            return

        # مسیر دیتابیس آفلاین
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(
                text="فایل دیتابیس محلی یافت نشد!",
                title="❌ خطا",
                type="error"
            ).show()
            return

        # گرفتن user_id از دیتابیس آفلاین
        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            conn_sq.close()

            if not res_id:
                MessageBox(
                    text="یوزر محلی یافت نشد!",
                    title="❌ خطا",
                    type="error"
                ).show()
                return

            id_user = res_id[0]
        except Exception as e:
            MessageBox(
                text=f"خطا در خواندن یوزر محلی: {e}",
                title="❌ خطا",
                type="error"
            ).show()
            return

        try:
            cursor = self.db_data.cursor()

            # شرط: وقتی پسورد قدیم و جدید یکسان باشند
            if old_password == new_password:
                cursor.execute(
                    "UPDATE user_s SET password = %s WHERE id = %s",
                    (new_password, id_user)
                )
                self.db_data.commit()

                MessageBox(
                    "پسورد موفقانه تغییر کرد",
                    title="موفقانه",
                    type="info"
                ).show()

                # اجرای تابع مورد نظر بعد از تغییر پسورد
                self.show_verify_login_fullscreen()
            else:
                MessageBox(
                    text="پسورد ها باهم مطابقت ندارند",
                    type="error",
                    title="خطا"
                ).show()

        except pymysql.Error as e:
            print(f"{e}: خطا در دیتابیس")

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
    window = New_login()
    window.show()
    sys.exit(app.exec())
