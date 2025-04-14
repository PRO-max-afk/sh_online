from PyQt6.QtWidgets import QWidget, QStackedWidget, QFrame, QLabel, QVBoxLayout, QPushButton, QLineEdit, QTextEdit,QLayout
from PyQt6.QtCore import Qt
from notification import Frame2

class WidgetManager:
    def __init__(self, parent):
        self.parent = parent
        self.stack = QStackedWidget(parent)
        self.frames = {}

        self.create_frame1()
        self.frame2 = None  # در ابتدا فریم ۲ ایجاد نمی‌شود

    def create_frame1(self):
        frame1 = QFrame()
        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout1.setContentsMargins(50, 20, 50, 20)

        label1 = QLabel("🏠 Home", frame1)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label1.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")

        entry1 = QLineEdit(frame1)
        entry1.setPlaceholderText("Enter text here...")
        entry1.setFixedSize(150, 30)
        entry1.setStyleSheet("""
            background-color: white;
            color: black;
        """)

        button1 = QPushButton("Click Me", frame1)
        button1.setFixedSize(100, 30)
        button1.setStyleSheet("""
            QPushButton{
                background-color: #008CBA;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px;}
            QPushButton:hover{
                background-color:#66cced;
            }
            QPushButton:pressed{
                background-color:#008CBA;}
        """)

        layout1.addWidget(label1)
        layout1.addWidget(entry1)
        layout1.addWidget(button1)
        frame1.setLayout(layout1)
        frame1.setStyleSheet("background-color: #D9D9D9;")

        self.frames["frame1"] = frame1
        self.stack.addWidget(frame1)

    def get_stack(self):
        return self.stack

    def switch_frame(self, frame_name):
        if frame_name == "frame2":
            if not self.frame2:
                self.frame2 = Frame2()
                self.frames["frame2"] = self.frame2
                self.stack.addWidget(self.frame2)
        if frame_name in self.frames:
            self.stack.setCurrentWidget(self.frames[frame_name])


