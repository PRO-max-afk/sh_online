from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSpacerItem, QSizePolicy, QBoxLayout, QLabel, QLineEdit, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QSize
import sys

class ChangeItems(QWidget):
    def __init__(self):
         super().__init__()
         self.ini_UI()
         
    def ini_UI(self):
            self.setStyleSheet("background-color: #d9d9d9;")

            title_label = QLabel("تنظیمات محصولات")
            title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            back_button = QPushButton()
            back_button.setIcon(QIcon('images/back.png'))
            back_button.setIconSize(QSize(60, 60))
            back_button.setFixedSize(70, 70)
            back_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border-radius: 25px;
                }
                QPushButton:hover {
                    background-color: #f8faff;        
                }
            """)

            frame1 = QFrame()
            frame1.setFixedHeight(280)
            frame1.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                }
            """)

            frame1_layout = QVBoxLayout(frame1)
            frame1_layout.setContentsMargins(20, 2, 20, 15)
            frame1_layout.setSpacing(5)

            frame1_title = QLabel("تغییر محصولات")
            frame1_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            frame1_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            search_input = QLineEdit()
            search_input.setPlaceholderText("جستجوی محصولات ...")
            search_input.setFixedSize(200, 28)
            search_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; color: #222222; font-size: 12px;")
            search_input.setAlignment(Qt.AlignmentFlag.AlignLeft)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 70))

            search_input.setGraphicsEffect(shadow)

            label1 = QLabel("نام محصول: ")
            label1.setFont(QFont("Arial", 12))
            label2 = QLabel("بارکد محصول: ")
            label2.setFont(QFont("Arial", 12))
            label3 = QLabel("قیمت فروش: ")
            label3.setFont(QFont("Arial", 12))

            line_edit1 = QLineEdit()
            line_edit1.setFixedSize(180, 28)
            line_edit2 = QLineEdit()
            line_edit2.setFixedSize(180, 28)
            line_edit3 = QLineEdit()
            line_edit3.setFixedSize(180, 28)

            field_layout = QHBoxLayout()
            field_layout.addWidget(label1)
            field_layout.addWidget(line_edit1)
            field_layout.addWidget(label2)
            field_layout.addWidget(line_edit2)
            field_layout.addWidget(label3)
            field_layout.addWidget(line_edit3)

            spacer = QFrame()
            spacer.setFixedHeight(15)
            spacer.setStyleSheet("background-color: transparent; border: none;")

            frame2 = QFrame()
            frame2.setFixedHeight(150)
            frame2.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #ccc;
                }
            """)

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(20, 20, 40, 40)
            main_layout.setSpacing(20)

            top_bar_layout = QHBoxLayout()
            top_bar_layout.setContentsMargins(20, 10, 20, 10)
            top_bar_layout.setSpacing(10)
            
            top_bar_layout.addWidget(title_label)
            top_bar_layout.addStretch()
            top_bar_layout.addWidget(back_button)

            frame1_layout.addWidget(frame1_title)
            frame1_layout.addWidget(search_input, alignment=Qt.AlignmentFlag.AlignLeft)
            frame1_layout.addWidget(spacer)
            #frame1_layout.addLayout(field_layout, alignment = Qt.AlignmentFlag.AlignHCenter)
            frame1_layout.addStretch()

            main_layout.addLayout(top_bar_layout)

            main_layout.addWidget(frame1)
            main_layout.addWidget(frame2)

            main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChangeItems()
    window.show()
    sys.exit(app.exec())
