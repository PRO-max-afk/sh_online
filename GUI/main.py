from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGraphicsBlurEffect, QGraphicsDropShadowEffect,QLabel,QFileDialog
from PyQt6.QtCore import QPropertyAnimation, QRect, Qt
from PyQt6.QtGui import QColor,QIcon,QPixmap,QPainter,QPainterPath
import sys
from PyQt6 import QtCore
from home import WidgetManager  
import os
from profile_picture import ProfileImage


class mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.x(), screen.y(), screen.width(), screen.height())
        self.setWindowTitle("برنامه فروشگاه")
        self.setStyleSheet("background-color:#D9D9D9;")

        self.panel_width = 90
        panel_x = screen.width() - self.panel_width  # قرار دادن پنل در سمت راست
        
        self.side_panel = QWidget(self)
        self.side_panel.setGeometry(panel_x, 0, self.panel_width, screen.height())

        # ویجت پس‌زمینه برای بلور
        self.background_widget = QWidget(self.side_panel)
        self.background_widget.setGeometry(0, 0, self.panel_width, screen.height())
        self.background_widget.setStyleSheet("background-color: white; border-radius: 44px;")


        # انیمیشن پنل از راست به چپ
        self.animation = QPropertyAnimation(self.side_panel, b"geometry")
        self.animation.setDuration(400)
        self.animation.setStartValue(QRect(screen.width(), 0, self.panel_width, screen.height()))  # شروع از بیرون صفحه
        self.animation.setEndValue(QRect(panel_x, 0, self.panel_width, screen.height()))  # ورود به صفحه
        self.animation.start()

        # 👇 Drop Shadow قوی‌تر و واضح‌تر برای side_panel
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.panel_width)  # سایه به اندازه عرض پنل
        shadow.setOffset(-10, 0)  # سایه به سمت چپ بیاد
        shadow.setColor(QColor(0, 0, 0, 150))  # سایه‌ی تیره‌تر و نیمه‌شفاف
        self.side_panel.setGraphicsEffect(shadow)
        ##icons
        #home_icon
        self.active_button = None
        self.home_btn= QPushButton(self.side_panel)
        h_icon_path= self.get_asset_path("home_24dp_999999_FILL0_wght400_GRAD0_opsz24 1.png")
        self.h_icon_black = QIcon(self.get_asset_path("home.png"))
        self.h_icon= QIcon(h_icon_path)
        self.home_btn.setIcon(self.h_icon)
        self.home_btn.setIconSize(QtCore.QSize(35,35))
        self.home_btn.clicked.connect(lambda: self.toggle_home())

        ##notificaton
        self.notification_btn= QPushButton(self.side_panel)
        n_icon_path= self.get_asset_path("notifications.png")
        self.n_icons= QIcon(self.get_asset_path("notification.png"))
        self.n_icon= QIcon(n_icon_path)
        self.notification_btn.setIcon(self.n_icon)
        self.notification_btn.setIconSize(QtCore.QSize(35,35))
        self.notification_btn.clicked.connect(lambda: self.toggle_notification())
        ##dasboard
        self.dashboard_btn= QPushButton(self.side_panel)
        self.d_icon= QIcon(self.get_asset_path("dashboard 1.png"))
        self.d_icons_black= QIcon(self.get_asset_path("dashboard_9055107.png"))
        self.dashboard_btn.setIcon(self.d_icon)
        self.dashboard_btn.setIconSize(QtCore.QSize(35,35))
        self.dashboard_btn.clicked.connect(lambda: self.set_active_button(self.dashboard_btn))
        ##orders
        self.order_btn= QPushButton(self.side_panel)
        self.order_icon= QIcon(self.get_asset_path("shopping-cart.png"))
        self.order_icon_black= QIcon(self.get_asset_path("shopping-cart_4824141.png"))
        self.order_btn.setIcon(self.order_icon)
        self.order_btn.setIconSize(QtCore.QSize(35,35))
        self.order_btn.clicked.connect(lambda: self.set_active_button(self.order_btn))
        ##finance
        self.finance_btn= QPushButton(self.side_panel)
        self.finance_icon= QIcon(self.get_asset_path("money (1).png"))
        self.finance_icon_black= QIcon(self.get_asset_path("money_1604644.png"))
        self.finance_btn.setIcon(self.finance_icon)
        self.finance_btn.setIconSize(QtCore.QSize(35,35))
        self.finance_btn.clicked.connect(lambda: self.set_active_button(self.finance_btn))
        ##inventory
        self.inventory_btn= QPushButton(self.side_panel)
        self.inventory_icon= QIcon(self.get_asset_path("store (2).png"))
        self.inventory_icon_black= QIcon(self.get_asset_path("store_10103219.png"))
        self.inventory_btn.setIcon(self.inventory_icon)
        self.inventory_btn.setIconSize(QtCore.QSize(35,35))
        self.inventory_btn.clicked.connect(lambda: self.set_active_button(self.inventory_btn))
        ##settings
        self.settings_btn= QPushButton(self.side_panel)
        self.se_icon= QIcon(self.get_asset_path("gear 1.png"))
        self.se_icon_black= QIcon(self.get_asset_path("settings_3524659.png"))
        self.settings_btn.setIcon(self.se_icon)
        self.settings_btn.setIconSize(QtCore.QSize(35,35))
        self.settings_btn.clicked.connect(lambda: self.set_active_button(self.settings_btn))

        # ایجاد و مدیریت فریم‌ها
        self.widget_manager = WidgetManager(self)
        self.stack = self.widget_manager.get_stack()
        self.stack.setGeometry(0, 0, screen.width() - self.panel_width, screen.height())  # فریم‌ها باید کل فضای چپ را بگیرند

        # چینش دکمه‌های پنل
        panel_layout = QVBoxLayout(self.side_panel)
        panel_layout.addWidget(self.home_btn)
        panel_layout.addWidget(self.notification_btn)
        panel_layout.addWidget(self.dashboard_btn)
        panel_layout.addWidget(self.order_btn)
        panel_layout.addWidget(self.finance_btn)
        panel_layout.addWidget(self.inventory_btn)
        panel_layout.addWidget(self.settings_btn)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # 🔹 دکمه‌ها در بالا و وسط چین شوند
        panel_layout.setSpacing(20)  # 🔹 فاصله بین دکمه‌ها

        # 🔵 عکس پروفایل با کیفیت و کلیک‌پذیر
        profile_image_path = self.get_asset_path("profile.png")  # مسیر پیش‌فرض عکس
        self.profile_widget = ProfileImage(profile_image_path, 70, self)
        panel_layout.insertWidget(0, self.profile_widget, alignment=Qt.AlignmentFlag.AlignHCenter)



        #panel_layout.addWidget(self.btn1)
        #panel_layout.addWidget(self.btn2)
        panel_layout.addStretch()
        self.side_panel.setLayout(panel_layout)

        self.iniUI()
        self.icons_UI()
        #self.Icon_change()

    def iniUI(self):
        """تنظیمات اولیه‌ی دکمه‌ها"""
    ##
    def toggle_home(self):
        self.widget_manager.switch_frame("frame1")
        self.set_active_button(self.home_btn)
    ##
    def toggle_notification(self):
        self.widget_manager.switch_frame("frame2")
        self.set_active_button(self.notification_btn)
    ##
    def icons_UI(self):
        ##home
        self.home_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        ##notification
        self.notification_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius:20px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
    ''')
        ##dashboard
        self.dashboard_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        ##order
        self.order_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        ## finance
        self.finance_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        ##inventory
        self.inventory_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        ##settings
        self.settings_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
    ##
    def set_active_button(self, button):
        # 1. بازگردانی آیکون دکمه‌ی قبلی (اگه هست)
        if self.active_button:
            if self.active_button == self.home_btn:
                self.home_btn.setIcon(self.h_icon)
            elif self.active_button == self.notification_btn:
                self.notification_btn.setIcon(self.n_icon)
            elif self.active_button == self.dashboard_btn:
                self.dashboard_btn.setIcon(self.d_icon)
            elif self.active_button == self.order_btn:
                self.order_btn.setIcon(self.order_icon)
            elif self.active_button == self.finance_btn:
                self.finance_btn.setIcon(self.finance_icon)
            elif self.active_button == self.inventory_btn:
                self.inventory_btn.setIcon(self.inventory_icon)
            elif self.active_button == self.settings_btn:
                self.settings_btn.setIcon(self.se_icon)
            # در صورت وجود دکمه‌های بیشتر، اینجا اضافه کن

        # 2. تنظیم آیکون جدید
        if button == self.home_btn:
            self.home_btn.setIcon(self.h_icon_black)
        elif button == self.notification_btn:
            self.notification_btn.setIcon(self.n_icons)
        elif button == self.dashboard_btn:
            self.dashboard_btn.setIcon(self.d_icons_black)
        elif button == self.order_btn:
            self.order_btn.setIcon(self.order_icon_black)
        elif button == self.finance_btn:
            self.finance_btn.setIcon(self.finance_icon_black)
        elif button == self.inventory_btn:
            self.inventory_btn.setIcon(self.inventory_icon_black)
        elif button == self.settings_btn:
            self.settings_btn.setIcon(self.se_icon_black)
        
        

        # 3. به‌روزرسانی دکمه فعال
        self.active_button = button

    ##
    def resizeEvent(self, event):
        """به‌روزرسانی ابعاد پنل هنگام تغییر اندازه‌ی صفحه"""
        width = self.width()
        height = self.height()
        panel_x = width - self.panel_width  
        self.side_panel.setGeometry(panel_x, 0, self.panel_width, height)
        self.background_widget.setGeometry(0, 0, self.panel_width, height)
        self.stack.setGeometry(0, 0, width - self.panel_width, height)  
        super().resizeEvent(event)
    #
    ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None

if __name__== "__main__":
    app = QApplication(sys.argv)
    window = mainwindow()
    window.show()
    sys.exit(app.exec())
