from PyQt6.QtWidgets import QLabel,QFileDialog
from PyQt6.QtCore import  Qt
from PyQt6.QtGui import QPixmap,QPainter,QPainterPath
import os

class ProfileImage(QLabel):
    def __init__(self, image_path, size=80, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background-color: transparent;")
        self.update_image(image_path)

    def update_image(self, image_path):
        if not image_path or not os.path.exists(image_path):
            print("📛 تصویر یافت نشد:", image_path)
            return

        pixmap = QPixmap(image_path).scaled(self.size, self.size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        rounded = QPixmap(self.size, self.size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self.size, self.size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.setPixmap(rounded)

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب تصویر پروفایل", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.update_image(file_path)
