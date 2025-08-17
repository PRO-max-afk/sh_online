from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QFileDialog,QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush,QPixmap
from PyQt6 import QtCore
import sqlite3
import pymysql
from notifi_box import Notification
from notifi_check import NotificationChecker
from message_b import MessageBox
from globals import shown_notifications
import os
from db_connection import Connection


class ShopSettings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.feild_UI()
        self.Button_UI()
        self.btn_mode= True
       ##هشدار ها
        self.notification_queue = []  # صف مرکزی نوتیفیکیشن‌ها
        self.notification_showing = False
        self.load_all_fonts()
        self.start_notification_checker()

        


    def init_ui(self):
        self.stack_widget= QStackedWidget()
        self.setCentralWidget(self.stack_widget)
        
        self.user_settings= QWidget()
    
        main_layout = QVBoxLayout(self.user_settings)
        ### scroll
        scroll_area= QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #eee;
                width: 10px;
                margin: 4px 0 4px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #999;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
            
        """)

        scroll_widget = QWidget()
        scroll_layout= QVBoxLayout(scroll_widget)
        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("تنظیمات فروشگاه", self)

        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        datetime_layout = QVBoxLayout()
        self.back_btn= QPushButton()
        datetime_layout.addWidget(self.back_btn)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(2)
        top_layout.addWidget(self.label, 1)
        ##
        middle_layout= QGridLayout()
        ###
        user_frame= QFrame()
        user_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        user_frame.setMaximumHeight(340)


        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        user_frame.setGraphicsEffect(shadow)

        ##
        mn_us_lay= QVBoxLayout(user_frame)
        ##
        tt_layout= QHBoxLayout()
        self.tite_label= QLabel("تنظیم لوگو")
        self.tite_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        tt_layout.addWidget(self.tite_label)
        tt_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    
        # لایه نام فروشگاه
        name_layout = QHBoxLayout()
        self.name_label = QLabel("نام فروشگاه")
        self.name_line = QLineEdit()
        self.new_line = QLineEdit()

        # ترتیب: لیبل بعد LineEdit و چینش به راست
        name_layout.addStretch(1)  # فضای اضافی در انتها
        name_layout.addWidget(self.name_line,alignment=Qt.AlignmentFlag.AlignRight)
        name_layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        name_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # لایه لوگو
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(7)
        self.logo_title = QLabel("لوگوی فروشگاه")
        self.logo_title.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.show_picture = QLabel()
        
        pik_layout= QVBoxLayout()
        self.pick_btn = QPushButton()
        pik_layout.addWidget(self.pick_btn)
        pik_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        logo_layout.addWidget(self.logo_title, alignment=Qt.AlignmentFlag.AlignRight)
        logo_layout.addWidget(self.show_picture, alignment=Qt.AlignmentFlag.AlignRight)
        #logo_layout.addWidget(self.pick_btn, alignment=Qt.AlignmentFlag.AlignRight)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        ##
        btn_layout= QHBoxLayout()
        self.save_btn= QPushButton()
        btn_layout.addWidget(self.save_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        ####
        mn_us_lay.addLayout(tt_layout)
        mn_us_lay.addLayout(name_layout)
        mn_us_lay.addLayout(logo_layout)
        mn_us_lay.addLayout(pik_layout)
        mn_us_lay.addLayout(btn_layout)
        ##

        empty_frame= QFrame()
        empty_frame.setStyleSheet("background-color: white; border-radius: 12px;")

        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        empty_frame.setGraphicsEffect(shadow)
        ##
        frame2_layout= QVBoxLayout(empty_frame)
        ##
        right_layout= QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop |Qt.AlignmentFlag.AlignRight)
        ##
        top_title_ee= QHBoxLayout()
        self.tie_label= QLabel("تغییرات اطلاعات کاربری")
        self.tie_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        top_title_ee.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        top_title_ee.addWidget(self.tie_label)
        ##
        user_label= QHBoxLayout()
        self.user_lb= QLabel("نام کاربری جدید:")
        self.user_line= QLineEdit()
        user_label.addStretch(5)
        user_label.addWidget(self.user_line)
        user_label.addWidget(self.user_lb)
        
        ##
        old_pass= QHBoxLayout()
        self.old_lb= QLabel("پسورد فعلی:      ")
        self.old_line= QLineEdit()
        old_pass.addStretch(5)
        old_pass.addWidget(self.old_line)
        old_pass.addWidget(self.old_lb)
        ##
        new_pass= QHBoxLayout()
        self.new_lb= QLabel("پسوردجدید:      ")
        self.new_pass_line= QLineEdit()
        self.new_pass_line.setEchoMode(QLineEdit.EchoMode.Password)
        new_pass.addStretch(5)
        self.hide_btn= QPushButton(self.new_pass_line)
        # موقعیت دکمه در گوشه راست QLineEdit
        self.update_icon_position()
        self.new_pass_line.resizeEvent = self.resize_event_with_icon
        ##
        new_pass.addWidget(self.new_pass_line)
        new_pass.addWidget(self.new_lb)
        ##
        repeat_password= QHBoxLayout()
        self.repeat_lb= QLabel("تکرارپسورد:      ")
        self.repeat_line= QLineEdit()
        self.repeat_line.setEchoMode(QLineEdit.EchoMode.Password)
        repeat_password.addStretch(2)
        repeat_password.addWidget(self.repeat_line)
        repeat_password.addWidget(self.repeat_lb)
        ##
        self.save_button = QPushButton("ذخیره تغییرات")
        ##
        right_layout.addLayout(top_title_ee)
        right_layout.addLayout(user_label)
        right_layout.addLayout(old_pass)
        right_layout.addLayout(new_pass)
        right_layout.addLayout(repeat_password)
        right_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignLeft)
        ##
        frame2_layout.addLayout(right_layout)
      



        ####
        middle_layout.addWidget(user_frame,1,1)
        middle_layout.addWidget(empty_frame,2,1)
        middle_layout.setSpacing(10)


        ##
        scroll_layout.addLayout(middle_layout)

        
        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_layout.addLayout(scroll_layout)
        main_layout.addWidget(scroll_area)

        #self.setLayout(main_layout)
        self.setStyleSheet("background-color: #D9D9D9;")

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self.user_settings)
        #self.notification_frame.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
        
        ##
        self.stack_widget.addWidget(self.user_settings)
    
   ##
    def label_UI(self):
        self.label.setMinimumSize(90,25)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        for title in (self.tite_label,self.tie_label):
            title.setMaximumHeight(40)
            title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            title.setStyleSheet('''
                background-color: #4c5159;
                font-size: 18px;
                font-weight: bold; 
                color: white;
                font-family: B Nazanin;
                padding: 8px;
                border-radius: 5px;
                ''')
        ##
        for title in (self.logo_title,self.name_label,self.user_lb,self.old_lb,self.new_lb,self.repeat_lb):
            title.setMaximumHeight(40)
            title.setMaximumWidth(115)
            title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            title.setStyleSheet('''
                    background-color: transparent;
                    font-size: 16px;
                    font-weight: bold; 
                    color: black;
                    font-family: B Nazanin;
                    padding: 8px;
                    border-radius: 5px;
                ''')
        # اندازه ثابت برای تصویر
        pixmap = QPixmap(self.get_asset_path("shoppingcart.png"))

        # تنظیم روی QLabel
        self.show_picture.setPixmap(pixmap)
        self.show_picture.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # تنظیم سایز مناسب برای QLabel
        self.show_picture.setScaledContents(True)
        self.show_picture.setFixedSize(100, 100)  # کمی بزرگتر از عکس تا فضا برای حاشیه باشد

        # تنظیم حاشیه با استایل شیت
        self.show_picture.setStyleSheet("""
            QLabel {
                border: 1px solid transparent;
                border-radius: 8px;
                background-color: white;
            }
        """)
        ##
        shadow= QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(2)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0,0,0,70))
        self.show_picture.setGraphicsEffect(shadow)
    ##
    def Button_UI(self):
        back_icon= QIcon(self.get_asset_path("left.png"))
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(50,50))
        self.back_btn.clicked.connect(self.back_settings)
        self.back_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.back_btn.setStyleSheet('''
        QPushButton{
            background-color: transparent;
            border-radius: 27px;
            padding: 5px;
                                    }
        QPushButton:hover{
            background-color: #f5f5f5;
                                    }
        QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            } 
        ''')
        ##
        self.pick_btn.setMaximumSize(120,40)
        self.pick_btn.setMinimumSize(100,30)
        self.pick_btn.setText("انتخاب تصویر")
        self.pick_btn.setStyleSheet('''
            QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #dcdcdc;
                    border-radius: 12px;
                    font-family: B Nazanin;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #f2f2f2;
                }
                QPushButton:pressed {
                    background-color: white;
                }
        ''')
        self.pick_btn.clicked.connect(self.pick_logo_image)
        ##
        save_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.save_btn.setIcon(save_icon)
        self.save_btn.setIconSize(QtCore.QSize(30,30))
        self.save_btn.setMaximumSize(120,40)
        self.save_btn.setMinimumSize(100,35)
        self.save_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.save_btn.clicked.connect(self.upload_logo_to_db)
        self.save_btn.setText("تنظیم اطلاعات")
        self.save_btn.setStyleSheet('''
        QPushButton{
            background-color: #11BD36;
            border-radius: 8px;
            padding: 5px;
            color: white;
            font-family: Mirza, "B Nazanin";
            font-weight: bold; 
            font-size: 16px;
                                    }
        QPushButton:hover{
            background-color: #63ff8d;
                                    }
        QPushButton:Pressed{
            background-color: #11BD36;
                                    }
        ''')
        ##
        
        self.hide_icon= QIcon(self.get_asset_path("Invisible.png"))
        self.hide_btn.setIcon(self.hide_icon)
        self.hide_btn.setIconSize(QtCore.QSize(25,25))
        self.hide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide_btn.clicked.connect(self.un_hide)
        self.hide_btn.setStyleSheet('''
        background-color: transparent;
        ''')
        ##
        
        self.save_button.setFixedSize(120, 40)
        self.save_button.setIcon(QIcon(self.get_asset_path("Bookmark.png")))
        self.save_button.setIconSize(QtCore.QSize(24, 24))
        self.save_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.save_button.clicked.connect(self.update_password)
        self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #00C853;
                    color: white;
                    border-radius: 8px;
                    font-family: B Nazanin;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00B44A;
                }
                QPushButton:Pressed{
                    background-color: #00C853;
                                      }
            """)

            # آیکون وسط

    ##
    def feild_UI(self):
        for input in (self.name_line,self.new_line):
            input.setFixedSize(200,40)
            input.setPlaceholderText("Enter...")
            input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            input.setStyleSheet('''
                QLineEdit {
                background-color: white;
                font-family:B Nazanin,"arial";
                font-weight: bold;
                font-size: 14px;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #e3e4e6;
            }
        ''')
        for input in (self.user_line,self.old_line,self.new_pass_line,self.repeat_line):
            input.setMaximumSize(350,40)
            input.setMinimumSize(250,30)
            input.setPlaceholderText("Enter...")
            input.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Maximum)
            input.setStyleSheet('''
                QLineEdit {
                background-color: white;
                font-family:Roboto,'arial';
                font-weight: bold;
                font-size: 14px;
                color: black;
                border: 1px solid #c2c2c2;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #e3e4e6;
            }
        ''')
        
        # تنظیم ترتیب فوکوس به صورت راست به چپ
       # self.setTabOrder(self.name_line, self.last_line)


    ##
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            if any(line.hasFocus() for line in [self.name_line]):
                self.add_user()
            elif any(line.hasFocus() for line in[
                self.new_pass_line,self.repeat_line,self.user_line,self.old_line
            ]):
                self.update_password()
    ##
    def update_icon_position(self):
        btn_size = self.hide_btn.sizeHint()
        line_width = self.new_pass_line.width()
        self.hide_btn.move(line_width - btn_size.width() - 5, (self.new_pass_line.height() - btn_size.height()) // 2)

    ##
    def resize_event_with_icon(self, event):
        self.update_icon_position()
        QLineEdit.resizeEvent(self.new_pass_line, event)

    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    ##
    def back_settings(self):
        from settings import Settings

        self.settings= Settings()
        self.stack_widget.addWidget(self.settings)

        
        self.stack_widget.setCurrentWidget(self.settings)
        ##
        start_pos = QPoint(-self.width(), 0)
        end_pos = QPoint(0, 0)
        self.settings.move(start_pos)
       
        ##
        self.animate= QPropertyAnimation(self.settings, b"pos",self)
        self.animate.setDuration(700)
        self.animate.setStartValue(start_pos)
        self.animate.setEndValue(end_pos)
        self.animate.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animate.start()

    ##
    def un_hide(self):
        if self.btn_mode:
            self.hide_btn.setIcon(QIcon(self.get_asset_path("Eye.png")))
            self.new_pass_line.setEchoMode(QLineEdit.EchoMode.Normal)
            self.repeat_line.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.hide_btn.setIcon(QIcon(self.get_asset_path("Invisible.png")))
            self.new_pass_line.setEchoMode(QLineEdit.EchoMode.Password)
            self.repeat_line.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_mode = not self.btn_mode
    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)
    ##
    def start_notification_checker(self):
        self.notif_checker = NotificationChecker()
        self.notif_checker.new_message.connect(self.show_notification_message)  # بدون ()
        self.notif_checker.exp_msg.connect(self.show_notification_exp)
        self.notif_checker.disc_msgs.connect(self.show_notification_disc)
        self.notif_checker.qua_msg.connect(self.show_quantity_msg)
        self.notif_checker.start()
    ##
    def enqueue_notification(self, pro_name: str, message: str):
        notif_key = f"{pro_name}:{message}"
        if notif_key in shown_notifications:
            return  # این هشدار قبلاً نمایش داده شده

        shown_notifications.add(notif_key)
        self.notification_queue.append((pro_name, message))
        if not self.notification_showing:
            self.show_next_notification()


    ##messages:
    def show_next_notification(self):
        if not self.notification_queue:
            self.notification_showing = False
            return

        self.notification_showing = True
        pro_name, message = self.notification_queue.pop(0)

        notif = Notification(
            pro_name=pro_name,
            message=message,
            parent_frame=self.notification_frame,
            icon_path=self.get_asset_path("alarm.png")
        )

        notif.closed.connect(self.show_next_notification)
        notif.show()
    ##
    def show_notification_message(self, pro_name: str, message: str):
        self.enqueue_notification(pro_name, message)
    ##
    def show_notification_exp(self, pro_names: list):
        print(f"show exp names shopes")
        for name in pro_names:
            self.enqueue_notification(name, "محصول انقضاء شده است لطفاً بررسی کنید")
    ##
    def show_notification_disc(self, product_names: list):
        for name in product_names:
            self.enqueue_notification("پایان اعتبار تخفیف", f"محصول {name} مدت اعتبار تخفیف آن به پایان رسید")
    ##
    def show_quantity_msg(self, product_names: list):
        for name in product_names:
            self.enqueue_notification("موجودی محصول", f"محصول {name} موجودی آن رو به اتمام است")
    
    ##
    def update_password(self):
        self.db_data = Connection().get_connection()
        user_name= self.user_line.text()
        old = self.old_line.text()
        new = self.new_pass_line.text()
        confirm = self.repeat_line.text()

        if not all([old, new, confirm,user_name]):
            MessageBox(text="لطفاً برای تغییر پسورد اطلاعات پسورد خود را وارد کنید", type="warning", title="هشدار").show()
            return

        if not self.db_data:
            print("خطا در اتصال به دیتابیس")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # رفتن یک سطح بالاتر از پوشه GUI
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

        if not os.path.exists(db_path):
            MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
            return

        try:
            conn_sq = sqlite3.connect(db_path)
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute("SELECT id FROM users;")
            res_id = cursor_sq.fetchone()
            if not res_id:
                MessageBox(text="یوزر محلی یافت نشد!", title="❌ خطا", type="error").show()
                return
            id_user = res_id[0]
        except Exception as e:
            MessageBox(text=f"خطا در خواندن یوزر محلی: {e}", title="❌ خطا", type="error").show()
            return

        try:
            curosr = self.db_data.cursor()
            curosr.execute("SELECT password FROM user_s WHERE id = %s AND password = %s", (id_user, old))
            result = curosr.fetchone()
            old_pass= result[0]
            if old_pass != old:
                MessageBox(text="پسورد قدیمی اشتباه است", title="هشدار", type="warning").show()
                return

            if new != confirm:
                MessageBox(text="پسورد جدید و تایید آن مطابقت ندارند", type="error", title="خطا").show()
                self.new_p_line.setEchoMode(QLineEdit.EchoMode.Normal)
                self.confirm_p_line.setEchoMode(QLineEdit.EchoMode.Normal)
                return

            # بروزرسانی پسورد
            curosr.execute("UPDATE user_s SET password = %s, username= %s WHERE id = %s and password=%s", (new, user_name,id_user,old))
            self.db_data.commit()

            notif = Notification(
                message="پسورد موفقانه تغییر کرد",
                icon_path=self.get_asset_path("Check Mark.png"),
                pro_name="!موفقانه",
                parent_frame=self.notification_frame
            )
            notif.show()
            

            # پاک‌سازی فیلدها
            self.old_line.clear()
            self.new_pass_line.clear()
            self.repeat_line.clear()
            self.user_line.clear()

        except pymysql.Error as e:
            print(f"{e}: خطا در دیتابیس")
  
  
    def upload_logo_to_db(self):
        from app_signals import global_signals  # ایمپورت در داخل تابع یا بالای فایل

        store_name = self.name_line.text().strip()

        if not hasattr(self, 'selected_logo_path') or not os.path.exists(self.selected_logo_path):
            MessageBox(text="لطفاً یک تصویر لوگو انتخاب کنید", title="⚠ هشدار", type="warning").show()
            return

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            with open(self.selected_logo_path, 'rb') as file:
                image_data = file.read()

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM logo")
            exists = cursor.fetchone()[0]

            if exists:
                cursor.execute("UPDATE logo SET image = ?, store_name = ?", (image_data, store_name))
            else:
                cursor.execute("INSERT INTO logo (image, store_name) VALUES (?, ?)", (image_data, store_name))

            conn.commit()
            conn.close()

            # ✅ سیگنال ارسال شود تا همه‌ی ویجت‌های پروفایل آپدیت شوند
            global_signals.logo_updated.emit()

            self.name_line.clear()
            self.show_picture.clear()
            notifi = Notification(
                message="لوگو آپدیت شد✅",
                pro_name="تغییر لوگو",
                parent_frame=self.notification_frame,
                icon_path=self.get_asset_path("Check Mark.png")
            )
            notifi.show()
            print("✅ لوگو ذخیره شد.")
        except Exception as e:
            print("❌ خطا در ذخیره لوگو:", e)


    ##
    def pick_logo_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب تصویر لوگو", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # نمایش در QLabel
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.show_picture.setPixmap(pixmap)

            # 🔵 مسیر فایل انتخاب‌شده را موقتاً ذخیره کنیم برای استفاده بعدی
            self.selected_logo_path = file_path
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
    
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
    
