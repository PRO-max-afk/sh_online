from PyQt6.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import sys

class CustomMessageBox(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("پیام")
        self.setFixedSize(400, 220)
        self.setStyleSheet("background-color: #f7f9fc; border-radius: 15px;")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)  # حذف علامت سوال
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.init_ui()

    def init_ui(self):
        # عنوان
        title_label = QLabel("پیام")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setFont(QFont("B Mitra", 18))

        # بدنه متن + آیکون
        icon_label = QLabel()
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.GlobalColor.transparent)
        icon_label.setPixmap(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation).pixmap(48, 48))

        text_label = QLabel("عملیات با موفقیت انجام شد")
        text_label.setStyleSheet("font-size: 18px; color: #2c3e50;")
        text_label.setFont(QFont("B Mitra", 16))
        text_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        text_layout = QHBoxLayout()
        text_layout.addWidget(text_label)
        text_layout.addWidget(icon_label)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # دکمه‌ها
        btn_ok = QPushButton("باشه")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedHeight(40)
        btn_ok.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-family: B Mitra;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')

        btn_cancel = QPushButton("لغو")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet('''
            QPushButton {
                background-color: #ecf0f1;
                color: #7f8c8d;
                border-radius: 10px;
                font-size: 16px;
                font-family: B Mitra;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        ''')

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_ok)
        buttons_layout.addStretch()

        # کل چیدمان
        main_layout = QVBoxLayout(self)
        main_layout.addSpacing(10)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(text_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        main_layout.addSpacing(20)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomMessageBox()
    if window.exec():
        print("تأیید شد")
    else:
        print("لغو شد")
    sys.exit(app.exec())
