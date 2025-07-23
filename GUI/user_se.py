from PyQt6.QtWidgets import (QMainWindow,QGridLayout,QFrame, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QRadioButton,QAbstractItemView,
    QGraphicsDropShadowEffect, QSizePolicy,QScrollArea,QMessageBox,QWidget,QTableWidgetItem,QTableWidget,QHeaderView,QListWidget,QStackedWidget)
from PyQt6.QtCore import Qt,QTimer,QThread,QEvent,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QColor,QIcon,QFontDatabase,QFont,QBrush
from PyQt6 import QtCore
from circle import CircularSpinner
import sqlite3
import pymysql
import requests
from notifi_box import Notification
from user_info import UserFetchThread
import threading
from switch import ToggleSwitch
from message_b import MessageBox
from switch import ToggleSwitch
import os
import sys

class UserSettings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.feild_UI()
        self.Button_UI()
        self.btn_mode= True
        self.show_first_spinner()
        #self.active_user()
        self.load_all_fonts()

        


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
        self.label = QLabel("تنظیمات کاربران", self)

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


        shadow= QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        user_frame.setGraphicsEffect(shadow)

        ##
        mn_us_lay= QVBoxLayout(user_frame)
        #
        all_layout= QGridLayout()
        ##
        tt_layout= QHBoxLayout()
        self.tite_label= QLabel("معلومات کاربر")
        self.tite_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        tt_layout.addWidget(self.tite_label)
        tt_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    
        ##
        name_layout= QHBoxLayout()
        self.name_label= QLabel("نام استفاده کننده")
        self.name_line= QLineEdit()
        #
        name_layout.addStretch(0)
        name_layout.addWidget(self.name_line)
        name_layout.addWidget(self.name_label)
        
        ##
        last_layout= QHBoxLayout()
        self.last_name= QLabel("تخلص")
        self.last_line= QLineEdit()
        ##
        users_layout= QHBoxLayout()
        self.user_label= QLabel("نام کاربری")
        self.user_line= QLineEdit()
        #
        users_layout.addStretch(0)
        users_layout.addWidget(self.user_line)
        users_layout.addWidget(self.user_label)
        #
        last_layout.addStretch(0)
        last_layout.addWidget(self.last_line)
        last_layout.addWidget(self.last_name)
        ##
        password= QHBoxLayout()
        self.pass_na= QLabel("رمز عبور")
        self.passwor_line= QLineEdit()
        self.passwor_line.setEchoMode(QLineEdit.EchoMode.Password)
        ##
        self.hide_btn= QPushButton(self.passwor_line)
        # موقعیت دکمه در گوشه راست QLineEdit
        self.update_icon_position()
        self.passwor_line.resizeEvent = self.resize_event_with_icon
        ##

        ##
        password.addStretch(0)
        password.addWidget(self.passwor_line)
        password.addWidget(self.pass_na)
        
        ##
        ca_password= QHBoxLayout()
        self.pass_nae= QLabel("تایید رمز عبور")
        self.ca_passwor_line= QLineEdit()
        self.ca_passwor_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.emty_lb= QLabel("")
        ca_password.addStretch(0)
        ca_password.addWidget(self.ca_passwor_line)
        ca_password.addWidget(self.pass_nae)
        
        ##
        #password_la= QHBoxLayout()
        #password_la.addLayout(ca_password)
        #password_la.addLayout(password)
        ##
        btn_layout= QHBoxLayout()
        self.save_btn= QPushButton()
        btn_layout.addWidget(self.save_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        ##
        all_layout.setSpacing(10)
        all_layout.addLayout(users_layout,2,3)
        all_layout.addLayout(last_layout,1,2)
        all_layout.addLayout(name_layout,1,3)
        all_layout.addLayout(ca_password,2,1)
        all_layout.addLayout(password,2,2)
        
        ####
        mn_us_lay.addLayout(tt_layout)
        #mn_us_lay.addLayout(user_layout)
        #mn_us_lay.addLayout(password_la)
        mn_us_lay.addLayout(all_layout)
        mn_us_lay.addLayout(btn_layout)
        


        ###ٌ#
        password_frame = QFrame()
        password_frame.setStyleSheet("background-color: white; border-radius: 12px;")
       # password_frame.setMaximumHeight(170)  # 👈 تنظیم ارتفاع فریم دقیق و جمع‌وجور

        shadows = QGraphicsDropShadowEffect(self)
        shadows.setBlurRadius(12)
        shadows.setXOffset(0)
        shadows.setYOffset(5)
        shadows.setColor(QColor(0, 0, 0, 70))
        password_frame.setGraphicsEffect(shadows)

        # چیدمان کلی
        mn_lay= QVBoxLayout(password_frame)
        password_layout = QHBoxLayout()

        ###
        titel_layout = QHBoxLayout()
        self.titel_label = QLabel("تغییر رمزعبور")
        self.titel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titel_layout.addWidget(self.titel_label)
        titel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # چیدمان‌ها با فاصله‌ی کم
        old_layout = QHBoxLayout()
        self.old_line = QLineEdit()
        self.old_label = QLabel("رمز عبور قدیمی")
        old_layout.addStretch(0)
        old_layout.addWidget(self.old_line)
        old_layout.addWidget(self.old_label)
        ##
        new_p_layout = QHBoxLayout()
        self.new_password = QLabel("رمز عبور جدید")
        self.new_p_line = QLineEdit()
        self.new_p_line.setEchoMode(QLineEdit.EchoMode.Password)
        #
        new_p_layout.addStretch(0)
        new_p_layout.addWidget(self.new_p_line)
        new_p_layout.addWidget(self.new_password)
        
       
        ##
        confirm_layout = QHBoxLayout()
        self.confirm_password = QLabel("تایید رمزعبور")
        self.confirm_p_line = QLineEdit()
        self.confirm_p_line.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addStretch(0)
        confirm_layout.addWidget(self.confirm_p_line)
        confirm_layout.addWidget(self.confirm_password)
        ##
        change_layout= QHBoxLayout()
        self.change_btn= QPushButton()
        change_layout.addWidget(self.change_btn)
        change_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)


        
        # اضافه‌کردن به چیدمان اصلی
        password_layout.addLayout(confirm_layout)
        password_layout.addLayout(new_p_layout)
        password_layout.addLayout(old_layout)
        
        ##
        mn_lay.addLayout(titel_layout)
        mn_lay.addLayout(password_layout)
        mn_lay.addLayout(change_layout)
        
        ##
        list_frame= QFrame()
        list_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        ##
        shad= QGraphicsDropShadowEffect(self)
        shad.setBlurRadius(12)
        shad.setXOffset(0)
        shad.setYOffset(5)
        shad.setColor(QColor(0,0,0,70))
        list_frame.setGraphicsEffect(shad)
        ##
        self.mn_li_layout= QVBoxLayout(list_frame)
        ##
        t_li_layout= QHBoxLayout()
        self.tt_titel= QLabel("معلومات کاربران موبایل")
        self.tt_titel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t_li_layout.addWidget(self.tt_titel)
        t_li_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        ##
        # جدول نمایش کاربران موبایل
        self.mobile_user_table = QTableWidget()
        self.mobile_user_table.setColumnCount(3)
        self.mobile_user_table.setHorizontalHeaderLabels(["نام کاربر", "تخلص کاربر", "وضعیت"])
        self.mobile_user_table.horizontalHeader().setStretchLastSection(True)
        self.mobile_user_table.verticalHeader().setVisible(False)
        self.mobile_user_table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 14px;
                color: black;
                font-family: B Nazanin,Arial;
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #888;
                font-family: "B Nazanin", "Mirza";
                font-size: 16px;
                font-weight: bold;
            }

        """)
        self.mobile_user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.mobile_user_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.mobile_user_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.mobile_user_table.setShowGrid(False)

        self.mn_li_layout.addLayout(t_li_layout)
        self.mn_li_layout.addWidget(self.mobile_user_table)
        ####
        middle_layout.addWidget(user_frame,1,1)
        middle_layout.setSpacing(10)
        middle_layout.addWidget(password_frame,2,1)
        middle_layout.setSpacing(10)
        middle_layout.addWidget(list_frame,3,1)
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
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
        ##
        self.stack_widget.addWidget(self.user_settings)
    
   ##
    def label_UI(self):
        self.label.setMinimumSize(120,20)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
        ''')
        ##
        for label in (self.name_label,self.last_name,self.user_label,self.old_label,self.new_password,self.confirm_password,self.pass_na,self.pass_nae):
            label.setMinimumSize(90,5)
            label.setFixedHeight(40)
            label.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
            label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold; 
            color: black;
            font-family: B Nazanin;
        ''')
        
        for title in (self.titel_label,self.tite_label,self.tt_titel):
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
        save_icon= QIcon(self.get_asset_path("Bookmark.png"))
        self.save_btn.setIcon(save_icon)
        self.save_btn.setIconSize(QtCore.QSize(30,30))
        self.save_btn.setMaximumSize(110,40)
        self.save_btn.setMinimumSize(100,35)
        self.save_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.save_btn.clicked.connect(self.add_user)
        self.save_btn.setText("ایجاد کاربر")
        self.save_btn.setStyleSheet('''
        QPushButton{
            background-color: #11BD36;
            border-radius: 8px;
            padding: 5px;
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
        change_icon= QIcon(self.get_asset_path("change password.png"))
        self.change_btn.setIcon(change_icon)
        self.change_btn.setIconSize(QtCore.QSize(30,30))
        self.change_btn.setMaximumSize(110,40)
        self.change_btn.setMinimumSize(100,35)
        self.change_btn.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.change_btn.setText("تغییر پسورد")
        self.change_btn.setStyleSheet('''
        QPushButton{
            background-color: #11BD36;
            border-radius: 8px;
            padding: 5px;
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
    def feild_UI(self):
        for input in (self.name_line,self.last_line,self.user_line,self.new_p_line,self.old_line,self.confirm_p_line,self.passwor_line,self.ca_passwor_line):
            input.setFixedSize(200,40)
            input.setPlaceholderText("Enter...")
            input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            input.setStyleSheet('''
                QLineEdit {
                background-color: white;
                font-family:Roboto,"B Nazanin";
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
        self.setTabOrder(self.name_line, self.last_line)
        self.setTabOrder(self.last_line,self.user_line)
        self.setTabOrder(self.user_line,self.passwor_line)
        self.setTabOrder(self.passwor_line, self.ca_passwor_line)
        self.setTabOrder(self.ca_passwor_line,self.save_btn)
        self.setTabOrder(self.old_line, self.new_p_line)
        self.setTabOrder(self.new_p_line, self.confirm_p_line)
    ##
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            if any(line.hasFocus() for line in [self.name_line,self.last_line,self.passwor_line,self.ca_passwor_line]):
                self.add_user()
            elif any( line.hasFocus() for line in [self.old_line,self.new_p_line,self.confirm_p_line]):
                self.update_password()

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
        self.settings_main= Settings()
        self.stack_widget.addWidget(self.settings_main)
        self.stack_widget.setCurrentWidget(self.settings_main)
        self.settings_main.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        ##animation:
        start_pos= QPoint(-self.width(),0)
        end_pos= QPoint(0,0)
        self.settings_main.move(start_pos)
        ##
        animation= QPropertyAnimation(self.settings_main, b'pos',self)
        animation.setDuration(700)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    ##
    def un_hide(self):
        if self.btn_mode:
            self.hide_btn.setIcon(QIcon(self.get_asset_path("Eye.png")))
            self.passwor_line.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ca_passwor_line.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.hide_btn.setIcon(QIcon(self.get_asset_path("Invisible.png")))
            self.passwor_line.setEchoMode(QLineEdit.EchoMode.Password)
            self.ca_passwor_line.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_mode = not self.btn_mode
    ##notifications
    def resizeEvent(self, event):
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        return super().resizeEvent(event)
    ##
    def update_icon_position(self):
        btn_size = self.hide_btn.sizeHint()
        line_width = self.passwor_line.width()
        self.hide_btn.move(line_width - btn_size.width() - 5, (self.passwor_line.height() - btn_size.height()) // 2)

    ##
    def resize_event_with_icon(self, event):
        self.update_icon_position()
        QLineEdit.resizeEvent(self.passwor_line, event)

    ##
    def add_user(self):
        name = self.name_line.text()
        last_name = self.last_line.text()
        username = self.user_line.text()
        passwrod = self.passwor_line.text()
        confirm = self.ca_passwor_line.text()

        # دریافت اطلاعات اتصال
        data = self.get_db_config()

        # بررسی خالی نبودن فیلدها
        if not all([name, last_name, username, passwrod, confirm]):
            MessageBox(text="برای ساخت کاربر باید تمامی فیلدهای لازم پر شود", title="هشدار", type="warning").show()
            return

        # بررسی تطابق رمز و تایید آن
        if passwrod != confirm:
            MessageBox(text="رمز عبور و تایید آن مطابقت ندارند", type="error", title="خطا").show()
            return

        if not data:
            print("اتصال به سرور انجام نشد")
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
            id_user = res_id[0]
        except Exception as e:
            MessageBox(text=f"خطا در خواندن یوزر محلی: {e}", title="❌ خطا", type="error").show()
            return
        try:
            conn = pymysql.connect(
                host=data["host"],
                user=data["user"],
                password=data["password"],
                database=data["database"]
            )
            cursor = conn.cursor()
            cursor.execute("SELECT limit_reach From user_s where id=%s",(id_user,))
            reach=cursor.fetchone()
            limit_reach= reach[0]
            cursor.execute("select count(*) from mobile_user where user_id= %s",(id_user,))
            row=cursor.fetchone()
            row_number= row[0]
            print(f"{limit_reach}: limit")
            print(f'{row_number}: number')
            
            if limit_reach > row_number :
                cursor.execute(
                    "INSERT INTO mobile_user(name, last_name, username, password,user_id) VALUES (%s,%s, %s, %s, %s)",
                    (name, last_name, username, passwrod,id_user)
                )
                cursor.execute(
                    "UPDATE mobile_user SET approve=1 WHERE username=%s",
                    (username,)
                )
                conn.commit()
                self.name_line.clear()
                self.last_line.clear()
                self.user_line.clear()
                self.passwor_line.clear()
                self.ca_passwor_line.clear()

                notif = Notification(
                    message="کاربر موفقانه ایجاد شد",
                    icon_path=self.get_asset_path("Check Mark.png"),
                    pro_name="موفقانه!",
                    parent_frame=self.notification_frame
                )
                notif.show()
            else:
                notifs= Notification(
                    message="اجازه ساخت یوزر موبایل ندارید، باید پلان خود را Upgrade کنید",
                    icon_path=self.get_asset_path("alarm.png"),
                    pro_name="متاسفانه!",
                    parent_frame=self.notification_frame)
                notifs.show()
                self.name_line.clear()
                self.last_line.clear()
                self.user_line.clear()
                self.passwor_line.clear()
                self.ca_passwor_line.clear()

        except pymysql.Error as e:
            print(f"{e}: خطا در اتصال به سرور")
    ##
    def update_password(self):
        db_data = self.get_db_config()
        old = self.old_line.text()
        new = self.new_p_line.text()
        confirm = self.confirm_p_line.text()

        if not all([old, new, confirm]):
            MessageBox(text="لطفاً برای تغییر پسورد اطلاعات پسورد خود را وارد کنید", type="warning", title="هشدار").show()
            return

        if not db_data:
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
            conn = pymysql.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            curosr = conn.cursor()
            curosr.execute("SELECT password FROM mobile_user WHERE user_id = %s AND password = %s", (id_user, old))
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
            curosr.execute("UPDATE mobile_user SET password = %s WHERE user_id = %s and password=%s", (new, id_user,old))
            conn.commit()

            notif = Notification(
                message="پسورد موفقانه تغییر کرد",
                icon_path=self.get_asset_path("Check Mark.png"),
                pro_name="!موفقانه",
                parent_frame=self.notification_frame
            )
            notif.show()
            

            # پاک‌سازی فیلدها
            self.old_line.clear()
            self.new_p_line.clear()
            self.confirm_p_line.clear()

        except pymysql.Error as e:
            print(f"{e}: خطا در دیتابیس")
    ##
    def get_db_config(self):
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
    def show_first_spinner(self):
        self.show_spinner_and_load_data()
    ##
    def show_spinner_and_load_data(self):
        # نمایش spinner
        self.spinner_wrapper = QWidget()  # ذخیره به عنوان یک ویژگی برای دسترسی بعدی
        spinner_layout = QVBoxLayout(self.spinner_wrapper)
        spinner_layout.setContentsMargins(0, 100, 0, 100)
        spinner_layout.addStretch()

        self.spinner = CircularSpinner(self)
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        spinner_layout.addStretch()

        self.mn_li_layout.addWidget(self.spinner_wrapper)

        # شروع بارگذاری داده‌ها
        QTimer.singleShot(100, self.active_users)

    ##
    def active_users(self):
        self.user_thread = UserFetchThread()
        self.user_thread.data_ready.connect(self.load_users)
        self.user_thread.error.connect(lambda msg: MessageBox(text=msg, title="❌ خطا", type="error").show())
        self.user_thread.start()

    ##
    def load_users(self, user_list):
        # حذف spinner بعد از دریافت داده‌ها
        if hasattr(self, "spinner_wrapper"):
            self.spinner_wrapper.setParent(None)
            del self.spinner_wrapper

        self.mobile_user_table.setRowCount(len(user_list))

        for i, row in enumerate(user_list):
            user_id, username, name, last_name, approve, denied = row

            self.mobile_user_table.setItem(i, 0, QTableWidgetItem(name))
            self.mobile_user_table.setItem(i, 1, QTableWidgetItem(last_name))
            self.mobile_user_table.setRowHeight(i, 32)  # به‌جای 32، عدد دلخواه

            switch = ToggleSwitch()
            switch.setChecked(True if approve == 1 else False)

            def make_handler(uid, uname, switch_obj):
                def handle_switch_toggled(state):
                    db_info = self.get_db_config()
                    try:
                        conn = pymysql.connect(
                            host=db_info["host"],
                            user=db_info["user"],
                            password=db_info["password"],
                            database=db_info["database"]
                        )
                        cursor = conn.cursor()
                        if state:
                            cursor.execute("UPDATE mobile_user SET approve=1, denied=0 WHERE id=%s AND username=%s", (uid, uname))
                            msg = "کاربر فعال شد"
                            icon = "Check Mark.png"
                        else:
                            cursor.execute("UPDATE mobile_user SET approve=0, denied=1 WHERE id=%s AND username=%s", (uid, uname))
                            msg = "کاربر غیر فعال شد"
                            icon = "alarm.png"

                        conn.commit()
                        conn.close()

                        notif = Notification(
                            message=msg,
                            icon_path=self.get_asset_path(icon),
                            pro_name="وضعیت!",
                            parent_frame=self.notification_frame
                        )
                        notif.show()
                    except Exception as ex:
                        print(f"خطا در آپدیت وضعیت: {ex}")
                return handle_switch_toggled

            switch.toggled.connect(make_handler(user_id, username, switch))

            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(switch)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.mobile_user_table.setCellWidget(i, 2, cell_widget)
    ##
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

