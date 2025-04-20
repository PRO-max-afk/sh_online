from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGraphicsDropShadowEffect, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, QRect, Qt, QSize
from PyQt6.QtGui import QColor, QIcon
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.x(), screen.y(), screen.width(), screen.height())
        self.setWindowTitle("برنامه فروشگاه")
        self.setStyleSheet("background-color:#D9D9D9;")

        self.panel_width = 90
        panel_x = screen.width() - self.panel_width

        self.side_panel = QWidget(self)
        self.side_panel.setGeometry(panel_x, 0, self.panel_width, screen.height())
        self.side_panel.setStyleSheet("background-color: white; border-radius: 44px;")

        self.animation = QPropertyAnimation(self.side_panel, b"geometry")
        self.animation.setDuration(400)
        self.animation.setStartValue(QRect(screen.width(), 0, self.panel_width, screen.height()))
        self.animation.setEndValue(QRect(panel_x, 0, self.panel_width, screen.height()))
        self.animation.start()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.panel_width)
        shadow.setOffset(-10, 0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.side_panel.setGraphicsEffect(shadow)

        # Create and position buttons directly without layout
        icon_paths = ["home.png", "notification.png", "dashboard.png", "order.png", "finance.png", "inventory.png", "settings.png"]
        self.buttons = []
        spacing = 30
        top_margin = 50

        for i, path in enumerate(icon_paths):
            btn = QPushButton(self.side_panel)
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(35, 35))
            btn.setGeometry(20, top_margin + i * (45 + spacing), 50, 50)
            btn.setStyleSheet(self.get_btn_style())
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.buttons.append(btn)

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        panel_x = width - self.panel_width
        self.side_panel.setGeometry(panel_x, 0, self.panel_width, height)
        super().resizeEvent(event)

    def get_btn_style(self):
        return '''
            QPushButton {
                background-color: white;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
