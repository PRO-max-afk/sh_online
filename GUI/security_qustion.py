from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QLineEdit,QPushButton,QMainWindow
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint,QEasingCurve
from PyQt6.QtGui import QPixmap, QFontDatabase, QPalette, QFont
import os,sys,pymysql,sqlite3
from message_b import MessageBox
from otp_security import Otp_login
from new_password import New_login
from db_connection_f import Connection


class Security_login(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
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
        self.img_label.setFixedSize(750, 563)
        self.img_label.setScaledContents(True)
        image_path = self.get_asset_path("computer-security-with-login-password-padlock.png")
        if image_path:
            pixmap = QPixmap(image_path)
            self.img_label.setPixmap(pixmap.scaled(self.img_label.size()))
        else:
            self.img_label.setText("تصویر یافت نشد.")

        # --- فریم سمت راست ---
        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: white;")
        self.frame.setFixedSize(550, screen.height())

        # --- اضافه کردن به layout افقی ---
        top_layout.addWidget(self.img_label)
        top_layout.addStretch()  # اسپیس بین عکس و فریم
        top_layout.addWidget(self.frame)

        # اضافه به layout اصلی
        main_layout.addLayout(top_layout)
        #self.setLayout(main_layout)
        
        # ایجاد layout برای man و title
        man_icon = self.get_asset_path("freepik__background__8496 1.png")
        self.manlabel = QLabel()
        self.manlabel.setFixedSize(100, 100)
        self.manlabel.setContentsMargins(0, 0, 0, 0)

        # ساخت لیبل عنوان
        self.title_label = QLabel("سوال امنیتی")
        self.title_label.setFixedHeight(30)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.title_label.setContentsMargins(40, -2, 0, 0)

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
            self.manlabel.setScaledContents(True)
        else:
            self.manlabel.setText("تصویر یافت نشد")

        # ایجاد layout برای فیلدهای ورودی
        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignJustify)

        # اضافه کردن label برای نام کاربری
        self.username_label = QLabel("نمبر تذکره")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی نام کاربری
        self.username_input = self.create_floating_input("id card")
    

        # اضافه کردن label برای رمز عبور
        self.password_label = QLabel("سال تولد")
        self.password_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

        # ایجاد فیلد ورودی رمز عبور
        self.password_input = self.create_floating_input("birthday")
        self.note_lb= QLabel("سوالاتی که جهت ابراز هویت گفته شده را پاسخ دهید")
        self.note_lb.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # دکمه ورود
        self.submit_btn = QPushButton("بعدی")
        self.submit_btn.clicked.connect(self.security_qua)
        #
        self.forgot_btn= QPushButton("ارسال کد به شماره تماس")
        self.forgot_btn.clicked.connect(self.show_otp_login_fullscreen)

        # ایجاد layout افقی برای دکمه "فراموشی پسورد"
        forgot_password_layout = QHBoxLayout()
        forgot_password_layout.addWidget(self.forgot_btn)

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
        self.input_layout.addWidget(self.note_lb)
        # اضافه کردن دکمه به layout اصلی
        self.input_layout.addLayout(button_layout)
        #self.input_layout.addLayout(forgot_password_layout)


        # ایجاد اسپیس برای قرار دادن فیلدها در وسط
        spacer_top = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        spacer_bottom = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

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
        self.username_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:0px;")
        self.password_label.setStyleSheet("font-size: 18px; color: #333333; font-family: Mirza; font-weight: bold; margin-right:0px;")   
        self.note_lb.setStyleSheet('''
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            font-family: Mirza;
            text-align: right;
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
        container.setFixedSize(300, 50)
        container.setStyleSheet("background: transparent;")

        # ایجاد LineEdit
        line_edit = QLineEdit(container)
        line_edit.setFixedSize(300, 50)
        line_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: 2px solid gray;  /* مرز کامل برای QLineEdit */
                padding: 10px;
                font-size: 14px;
                outline: none;
                color: black;
                border-radius: 7px;  /* گوشه‌های گرد */
                margin-left: 10px;  /* فاصله از سمت چپ */
            }
            QLineEdit:hover {
                border: 2px solid #2251DB;  /* تغییر رنگ مرز هنگام hover */
            }
        """)

        # شفاف کردن پس‌زمینه QLineEdit
        palette = line_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
        line_edit.setPalette(palette)

        # ایجاد لیبل داخل LineEdit
        label = QLabel(placeholder_text, container)
        label.setFont(QFont("Roboto", 16))
        label.setStyleSheet("""
            color: gray;
            background: white;  /* پس‌زمینه سفید برای label */
            padding: 0 5px;
            font-size: 16px;
            font-family: Roboto;
            font-style: bold;
            position: absolute;
            text-align: center;  /* قرار دادن متن در مرکز */
            left: 10px;
            top: 12px;
            border-radius: 7px;  /* گوشه‌های گرد */
            margin-left: 10px;  /* فاصله از سمت چپ */
            width: calc(100% - 20px);  /* عرض به اندازه 100% عرض container (با احتساب margin) */
        """)
        label.move(10, 12)

        # نصب Event Filter روی LineEdit
        line_edit.installEventFilter(self)

        # ذخیره موقعیت اولیه لیبل
        label._original_pos = label.pos()

        # تنظیم انیمیشن
        animation = QPropertyAnimation(label, b"pos")
        animation.setDuration(150)

        # اتصال ویجت‌ها
        line_edit._floating_label = label
        line_edit._floating_animation = animation

        # چک کردن برای نمایش label در صورت وجود متن
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
    def show_otp_login_fullscreen(self):
        # پاک کردن محتوای فعلی پنجره
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # ایجاد یک نمونه از Security_login به‌صورت ویجت (نه پنجره‌ی جدید)
        otp_widget = Otp_login()  # توجه: کلاس باید از QWidget ارث ببرد نه QMainWindow

        self.setCentralWidget(otp_widget)

        # انیمیشن اسلاید از راست
        start_pos = QPoint(self.width(), 0)
        end_pos = QPoint(0, 0)
        otp_widget.move(start_pos)

        self.anim = QPropertyAnimation(otp_widget, b"pos", self)
        self.anim.setDuration(600)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
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
    ##
    def keyPressEvent(self,event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.security_qua()
    ##
    def security_qua(self):
        id_card = str(self.username_input.line_edit.text()).strip()
        birthday = str(self.password_input.line_edit.text()).strip()
        conn = Connection().get_connection()
        id_user = None

        # مسیر دیتابیس آفلاین
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data","sh_online.db")  # اینجا نام دیتابیس محلی‌ات رو بگذار

        if not os.path.exists(db_path):
            print("no path db_offline found")
            return

        # بررسی ورودی‌ها
        if not id_card or not birthday:
            MessageBox(
                text="برای تغییر پسورد معلومات را کامل وارد کنید",
                title="هشدار",
                type="warning"
            ).show()
            return

        if not conn:
            MessageBox(
                text="ارتباط با سرور برقرار نشد",
                title="خطا",
                type="error"
            ).show()
            return

        # گرفتن user_id از دیتابیس آفلاین
        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users LIMIT 1")
            id_use = cursor_sq.fetchone()
            if id_use:
                id_user = id_use[0]
            conn_sq.close()
        except sqlite3.Error as e:
            print(f"خطا در دیتابیس آفلاین {e}")
            return

        # بررسی اطلاعات با دیتابیس آنلاین
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT birthday, id_number FROM user_s WHERE id=%s",
                (id_user,)
            )
            result = cursor.fetchone()

            if result:
                db_birthday, db_id_number = str(result[0]).strip(), str(result[1]).strip()
                if birthday == db_birthday and id_card == db_id_number:
                    self.show_new_login_fullscreen()
                else:
                    MessageBox(
                        text="اطلاعات شما درست نمی باشد لطفاً بررسی کنید",
                        title="نادرست",
                        type="warning"
                    ).show()
            else:
                MessageBox(
                    text="اطلاعات شما درست نمی باشد لطفاً بررسی کنید",
                    title="نادرست",
                    type="warning"
                ).show()

        except pymysql.MySQLError as e:
            print(f"online db problem: {e}")

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
    window = Security_login()
    window.show()
    sys.exit(app.exec())
