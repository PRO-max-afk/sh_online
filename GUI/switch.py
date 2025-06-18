from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QRectF, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)  # ✅ سیگنال برای وصل شدن به تابع بیرونی

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._checked = False
        self._thumb_pos = 2
        self.animation = QPropertyAnimation(self, b"thumb_pos", self)
        self.animation.setDuration(200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            self.animate()
            self.toggled.emit(self._checked)  # ✅ سیگنال زمانی‌که تغییر کرد

    def toggle(self):
        self.setChecked(not self._checked)

    def mousePressEvent(self, event):
        self.toggle()

    def animate(self):
        if self._checked:
            self.animation.setStartValue(2)
            self.animation.setEndValue(self.width() - 28)
        else:
            self.animation.setStartValue(self.width() - 28)
            self.animation.setEndValue(2)
        self.animation.start()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_color = QColor("#344be3") if self._checked else QColor("#cccccc")
        p.setBrush(QBrush(bg_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 15, 15)

        # Thumb (circle)
        thumb_color = QColor("white")
        p.setBrush(QBrush(thumb_color))
        p.drawEllipse(QRectF(self._thumb_pos, 2, 26, 26))

    @pyqtProperty(int)
    def thumb_pos(self):
        return self._thumb_pos

    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()
