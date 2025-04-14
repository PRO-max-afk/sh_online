from PyQt6.QtWidgets import QWidget, QStackedWidget, QFrame, QLabel, QVBoxLayout, QPushButton, QLineEdit, QTextEdit,QLayout
from PyQt6.QtCore import Qt

class Orders(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("ℹ️ orders", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")

        text_edit = QTextEdit(self)
        text_edit.setPlaceholderText("Write something...")
        text_edit.setStyleSheet("""
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 5px;
            padding: 5px;
        """)

        layout.addWidget(label)
        layout.addWidget(text_edit)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #D9D9D9;")
