from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGraphicsBlurEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QRect, Qt
from PyQt6.QtGui import QColor
import sys
from home import WidgetManager  


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

        # ایجاد و مدیریت فریم‌ها
        self.widget_manager = WidgetManager(self)
        self.stack = self.widget_manager.get_stack()
        self.stack.setGeometry(0, 0, screen.width() - self.panel_width, screen.height())  # فریم‌ها باید کل فضای چپ را بگیرند

        # چینش دکمه‌های پنل
        panel_layout = QVBoxLayout(self.side_panel)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # 🔹 دکمه‌ها در بالا و وسط چین شوند
        panel_layout.setSpacing(10)  # 🔹 فاصله بین دکمه‌ها


        #panel_layout.addWidget(self.btn1)
        #panel_layout.addWidget(self.btn2)
        panel_layout.addStretch()
        self.side_panel.setLayout(panel_layout)

        self.iniUI()

    def iniUI(self):
        """تنظیمات اولیه‌ی دکمه‌ها"""
        #self.btn1.setFixedSize(100, 30)
        #self.btn2.setFixedSize(100, 30)

    def resizeEvent(self, event):
        """به‌روزرسانی ابعاد پنل هنگام تغییر اندازه‌ی صفحه"""
        width = self.width()
        height = self.height()
        panel_x = width - self.panel_width  
        self.side_panel.setGeometry(panel_x, 0, self.panel_width, height)
        self.background_widget.setGeometry(0, 0, self.panel_width, height)
        self.stack.setGeometry(0, 0, width - self.panel_width, height)  
        super().resizeEvent(event)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.setFixedSize(100, 30)
        self.default_geometry = None

        # افکت سایه
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(5)
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setColor(QColor("gray"))  
        self.setGraphicsEffect(self.shadow_effect)

        # انیمیشن تغییر اندازه دکمه
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)

    def enterEvent(self, event):
        """زمانی که ماوس روی دکمه می‌رود، دکمه برجسته شود (بزرگ‌تر شده و سایه‌ی بیشتری بگیرد)"""
        if self.default_geometry is None:
            self.default_geometry = self.geometry()
        new_geometry = QRect(self.default_geometry.x() - 2, self.default_geometry.y() - 3, self.width() + 4, self.height() + 6)
        self.animate_button(new_geometry)

        # افزایش سایه
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor("black"))  

        super().enterEvent(event)

    def leaveEvent(self, event):
        """زمانی که ماوس از روی دکمه خارج می‌شود، دکمه به حالت اولیه برگردد"""
        if self.default_geometry:
            self.animate_button(self.default_geometry)

        # کاهش سایه
        self.shadow_effect.setBlurRadius(5)
        self.shadow_effect.setColor(QColor("gray"))  

        super().leaveEvent(event)

    def animate_button(self, new_geometry):
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(new_geometry)
        self.animation.start()
if __name__== "__main__":
    app = QApplication(sys.argv)
    window = mainwindow()
    window.show()
    sys.exit(app.exec())
