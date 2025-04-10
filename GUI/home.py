from PyQt6.QtWidgets import QWidget, QStackedWidget, QFrame, QLabel, QVBoxLayout, QPushButton, QLineEdit, QTextEdit,QLayout
from PyQt6.QtCore import Qt


class WidgetManager:
    def __init__(self, parent):
        self.parent = parent
        self.stack = QStackedWidget(parent)
        self.frames = {}
        self.widgets = {}  # دیکشنری برای نگهداری ویجت‌ها
        self.create_frames()
        self.UI()  # اجرای تابع UI برای تنظیم استایل‌ها

    def create_frames(self):
        # 🟢 **ایجاد فریم اول**
        frame1 = QFrame()
        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout1.setContentsMargins(50, 20, 50, 20)

        label1 = QLabel("🏠 Home", frame1)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        entry1 = QLineEdit(frame1)
        entry1.setPlaceholderText("Enter text here...")
       

        button1 = QPushButton("Click Me", frame1)
        button1.setFixedSize(100, 30)

        


        layout1.addWidget(label1)
        layout1.addWidget(entry1)
        layout1.addWidget(button1)
        frame1.setLayout(layout1)

        # **ذخیره در دیکشنری**
        self.frames["frame1"] = frame1
        self.widgets["label1"] = label1
        self.widgets["entry1"] = entry1
        self.widgets["button1"] = button1

        # 🟠 **ایجاد فریم دوم**
        frame2 = QFrame()
        layout2 = QVBoxLayout(frame2)

        label2 = QLabel("ℹ️ About", frame2)
        label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_edit = QTextEdit(frame2)
        text_edit.setPlaceholderText("Write something...")

        layout2.addWidget(label2)
        layout2.addWidget(text_edit)
        frame2.setLayout(layout2)

        # **ذخیره در دیکشنری**
        self.frames["frame2"] = frame2
        self.widgets["label2"] = label2
        self.widgets["text_edit"] = text_edit

        # **اضافه کردن فریم‌ها به استک**
        self.stack.addWidget(frame1)
        self.stack.addWidget(frame2)

    def UI(self):
        """ تابعی برای تنظیم استایل فریم‌ها و ویجت‌ها """
        self.frames["frame1"].setStyleSheet("background-color: #D9D9D9;")
        self.frames["frame2"].setStyleSheet("background-color: #D9D9D9;")

        self.widgets["label1"].setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        self.widgets["label2"].setStyleSheet("font-size: 18px; font-weight: bold; color: black;")

        self.widgets["entry1"].setStyleSheet("""
            background-color: white;
            color:black;
        """)
        self.widgets["entry1"].setFixedSize(150, 30)
        
        self.widgets["button1"].setStyleSheet("""
        
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
            QPushButton:Pressed{
                    background-color:#008CBA;}
        """)

        self.widgets["text_edit"].setStyleSheet("""
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 5px;
            padding: 5px;
        """)

    def get_stack(self):
        return self.stack
    


    def switch_frame(self, frame_name):
        if frame_name in self.frames:
            self.stack.setCurrentWidget(self.frames[frame_name])
