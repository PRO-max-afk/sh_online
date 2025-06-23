import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen

class CircularSpinner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circular Spinner Loop")
        self.resize(300, 300)
        self.angle = 0  # زاویه اولیه
        self.running = True  # شرط حلقه: تا زمانی که این True باشد، ادامه بده
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(20)  # هر 20ms چرخش انجام شود

    def rotate(self):
        if self.running:
            self.angle += 5
            if self.angle >= 360:
                self.angle = 0
            self.update()
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(30, 30, -30, -30)
        pen = QPen(Qt.GlobalColor.darkCyan, 10)
        painter.setPen(pen)

        # رسم یک کمان ۹۰ درجه که به صورت چرخشی نمایش داده می‌شود
        painter.drawArc(rect, int((90 - self.angle) * 16), -90 * 16)

