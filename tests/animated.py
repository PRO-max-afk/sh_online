import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QStackedWidget, QVBoxLayout, QLabel

class FirstModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightblue;")
        self.button = QPushButton("Go to Second Module", self)
        self.button.clicked.connect(self.show_second_module)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def show_second_module(self):
        self.parent().switch_to_second_module()

class SecondModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgreen;")
        self.label = QLabel("Welcome to the Second Module", self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Animation Example")
        self.setGeometry(100, 100, 400, 300)

        # Stacked widget to manage the modules
        self.stacked_widget = QStackedWidget(self)
        self.first_module = FirstModule()
        self.second_module = SecondModule()

        self.stacked_widget.addWidget(self.first_module)
        self.stacked_widget.addWidget(self.second_module)

        self.setCentralWidget(self.stacked_widget)

    def switch_to_second_module(self):
        # Apply the animation to simulate the book page turning effect
        animation = QPropertyAnimation(self.stacked_widget, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(QRect(0, 0, 400, 300))
        animation.setEndValue(QRect(0, 0, 0, 300))
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        animation.finished.connect(self.finish_animation)
        animation.start()

    def finish_animation(self):
        # After animation is done, switch to the second module and adjust geometry
        self.stacked_widget.setCurrentWidget(self.second_module)
        self.stacked_widget.setGeometry(0, 0, 400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
