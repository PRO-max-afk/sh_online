import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen

class CircularSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(20)
        self.setFixedSize(100, 100)  # اندازه ثابت

    def rotate(self):
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        pen = QPen(Qt.GlobalColor.darkCyan, 10)
        painter.setPen(pen)
        painter.drawArc(rect, int((90 - self.angle) * 16), -90 * 16)

    def stop(self):
        # توقف تایمر برای متوقف کردن انیمیشن
        self.timer.stop()
        self.update()  # اطمینان از به‌روز شدن نمایشگر بعد از توقف
        self.hide()