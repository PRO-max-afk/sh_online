from PyQt6.QtWidgets import (QStackedWidget,QMainWindow,QFrame, QLabel, QVBoxLayout, QHBoxLayout,QToolButton,
    QSizePolicy,QScrollArea,QWidget,QGridLayout)
from PyQt6.QtCore import Qt,QPoint,QPropertyAnimation,QEasingCurve
from PyQt6.QtGui import QIcon,QFontDatabase
from PyQt6 import QtCore
import jdatetime
import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel,QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt
from notifi_check import NotificationChecker
from globals import shown_notifications
from notifi_box import Notification




class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.label_UI()
        self.set_today_date()
        self.set_today_time()
        self.button_UI()
        self.load_all_fonts()
        self.start_notification_checker()
        ##هشدار ها
        self.notification_queue = []  # صف مرکزی نوتیفیکیشن‌ها
        self.notification_showing = False
        

        


    def init_ui(self):
        self.stack= QStackedWidget()
        self.setCentralWidget(self.stack)
       

        self.settings_page = QWidget()
        main_layout = QVBoxLayout(self.settings_page)

        # ScrollArea setup
        scroll_area = QScrollArea(self)
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
        scroll_layout = QVBoxLayout(scroll_widget)

        # لایه بالا
        top_layout = QHBoxLayout()
        self.label = QLabel("تنظیمات فروشگاه", self)


        ##
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        ##
        datetime_layout = QVBoxLayout()
        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        datetime_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(datetime_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.label, 1)


        # لایه جعبه‌ها
        self.box_layout = QGridLayout()
        self.box_layout.setSpacing(20)
        scroll_layout.addLayout(self.box_layout)
        scroll_layout.addStretch()

        # افزودن ویجت‌ها به main_layout
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(50)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_layout.addWidget(scroll_area)

        self.setStyleSheet("background-color: #D9D9D9;")
        ### buttons:
        self.store_settings= QToolButton()
        self.item_settings= QToolButton()
        self.sale_settings= QToolButton()
        self.user_settings= QToolButton()
        self.finance_settings= QToolButton()
        self.log_out= QToolButton()

        # 🟢 ایجاد notification_frame در انتها و بالا بردن آن
        self.notification_frame = QFrame(self.settings_page)
        self.notification_frame.setStyleSheet("background: transparent;")
        self.notification_frame.setGeometry(0, 0, self.width(), 100)
        self.notification_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.notification_frame.raise_()
        ##
        self.stack.addWidget(self.settings_page)

    
    def label_UI(self):
        self.label.setMinimumSize(200, 40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold; 
            color: black;
            font-family: Mirza;
            margin-top: 5px;
        ''')

    ##
    def button_UI(self):
        ##
        self.user_settings.clicked.connect(self.user_page)
        self.store_settings.clicked.connect(self.shop_se_page)
        self.item_settings.clicked.connect(self.item_page)
        self.log_out.clicked.connect(self.open_login_with_animation)
        self.sale_settings.clicked.connect(self.sale_change)        
        # آیکون و متن‌ها
        buttons_info = [
            (self.store_settings, "grocery-store_16893316.png", "تنظیمات فروشگاه"),
            (self.item_settings, "box.png", "تنظیمات محصولات"),
            (self.sale_settings, "setting_5935006.png", "تنظیمات فروشات"),
            (self.user_settings, "group_151943.png", "تنظیمات کاربران"),
            (self.finance_settings, "settings_1657673.png", "تنظیمات مالی"),
            (self.log_out, "export_5469314.png", "خروج از سیستم")
            # می‌توانید دکمه‌های بیشتر هم اضافه کنید.
        ]

        buttons = []
        for btn, icon_file, text in buttons_info:
            icon = QIcon(self.get_asset_path(icon_file))
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(90, 90))  # بزرگ‌تر شد
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumSize(160, 160)
            btn.setMaximumSize(200, 200)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet('''
                QToolButton {
                    background-color: #ffffff;
                    border: 1px solid #dcdcdc;
                    border-radius: 16px;
                    padding: 15px;
                    font-family: B Nazanin;
                    font-size: 18px;
                    font-weight: bold;
                    color: #333333;
                }
                QToolButton:hover {
                    background-color: #f2f2f2;
                }
                QToolButton:pressed {
                    background-color: white;
                }
            ''')
            buttons.append(btn)

        # اضافه کردن دکمه‌ها به `QGridLayout` به صورت سطری - ستونی
        max_per_row = 4
        for i, btn in enumerate(buttons):
            row = i // max_per_row
            col = i % max_per_row
            self.box_layout.addWidget(btn, row, col)
    ##
    def set_today_date(self):
        today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_label.setText(f"تاریخ: {today_jalali}")
        self.date_label.setMinimumHeight(30)
        self.date_label.setMaximumHeight(70)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_label.setStyleSheet('''
            font-size: 18px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
            margin-left:20px
        ''')
    ##
    def set_today_time(self):
        weekdays_fa = {
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌ شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج ‌شنبه',
            'Friday': 'جمعه',
        }
        weekday_en = jdatetime.date.today().togregorian().strftime("%A")
        weekday_fa = weekdays_fa.get(weekday_en, 'نامشخص')

        self.time_label.setText(f"امروز: {weekday_fa}")
        self.time_label.setMinimumHeight(30)
        self.time_label.setMaximumHeight(50)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.time_label.setStyleSheet('''
            font-size: 16px;
            font-family: Mirza;
            font-weight: bold;
            color: #333;
            margin-left:30px;
        ''')
    
    def user_page(self):
        from user_se import UserSettings

        self.user_settings = UserSettings()
        self.stack.addWidget(self.user_settings)

        # موقعیت اولیه: خارج از صفحه
        self.user_settings.move(self.stack.width(), 0)
        self.stack.setCurrentWidget(self.user_settings)

        # انیمیشن ورود از راست
        self.anim = QPropertyAnimation(self.user_settings, b"pos", self)
        self.anim.setDuration(700)
        self.anim.setStartValue(QPoint(self.stack.width(), 0))
        self.anim.setEndValue(QPoint(0, 0))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
    ##
    def item_page(self):
        from items import ItemsSettings

        self.user_settings = ItemsSettings()
        self.stack.addWidget(self.user_settings)

        # موقعیت اولیه: خارج از صفحه
        self.user_settings.move(self.stack.width(), 0)
        self.stack.setCurrentWidget(self.user_settings)

        # انیمیشن ورود از راست
        self.anim = QPropertyAnimation(self.user_settings, b"pos", self)
        self.anim.setDuration(700)
        self.anim.setStartValue(QPoint(self.stack.width(), 0))
        self.anim.setEndValue(QPoint(0, 0))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
    ##
    def shop_se_page(self):
        from shop_se import ShopSettings

        self.shop_paged = ShopSettings()
        self.stack.addWidget(self.shop_paged)

        # موقعیت اولیه: خارج از صفحه
        self.user_settings.move(self.stack.width(), 0)
        self.stack.setCurrentWidget(self.shop_paged)

        # انیمیشن ورود از راست
        self.anim = QPropertyAnimation(self.shop_paged, b"pos", self)
        self.anim.setDuration(700)
        self.anim.setStartValue(QPoint(self.stack.width(), 0))
        self.anim.setEndValue(QPoint(0, 0))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
    ##
    def sale_change(self):
        from change_sale import ChangingFactor
        self.ch_sale= ChangingFactor()
        self.stack.addWidget(self.ch_sale)
        
        self.user_settings.move(self.width(), 0)
        self.stack.setCurrentWidget(self.ch_sale)
        animation= QPropertyAnimation(self.ch_sale, b"pos",self)
        animation.setDuration(700)
        animation.setStartValue(QPoint(self.stack.width(), 0))
        animation.setEndValue(QPoint(0,0))
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start() 
    ##
    def open_login_with_animation(self):
        from first_login import Main_login

        # ساخت پنجره لاگین
        login_window = Main_login()
        login_window.setWindowOpacity(0)
        login_window.showMaximized()

        # اجرای انیمیشن
        animation = QPropertyAnimation(login_window, b"windowOpacity")
        animation.setDuration(700)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

        # حذف کامل و فوری تمام چهارچوب پنجره فعلی
        self.window().destroy()

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
        print(f"show exp names: {pro_names}")
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
        
        
