from PyQt6.QtWidgets import QMessageBox

class MessageBox:
    def __init__(self, text, title="پیام", type="info", buttons=QMessageBox.StandardButton.Ok):
        self.msg = QMessageBox()
        self.msg.setWindowTitle(title)
        self.msg.setText(text)
        self.msg.setStandardButtons(buttons)

        if type == "info":
            self.msg.setIcon(QMessageBox.Icon.Information)
        elif type == "warning":
            self.msg.setIcon(QMessageBox.Icon.Warning)
        elif type == "error":
            self.msg.setIcon(QMessageBox.Icon.Critical)
        elif type == "question":
            self.msg.setIcon(QMessageBox.Icon.Question)
        else:
            self.msg.setIcon(QMessageBox.Icon.NoIcon)

        self.message_UI()

    def show(self):
        return self.msg.exec()
    
    def message_UI(self):
        self.msg.setStyleSheet('''
            QMessageBox {
                background-color: #d9d9d9;
                font-family: B Nazanin, "Mirza";
                font-size: 18px;
                font-weight: bold;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-family: PoetsenOne;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
