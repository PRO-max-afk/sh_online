from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QFrame,
    QLineEdit, QTextEdit, QComboBox, QFormLayout, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys


class FoodFormUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Food Menu Management")
        self.setMinimumSize(900, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # --- Food Form ---
        form_group = QGroupBox("Add New Food")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["Starter", "Main Course", "Dessert", "Drink"])
        self.description_input = QTextEdit()

        self.add_button = QPushButton("Add to Menu")
        self.add_button.clicked.connect(self.add_food_to_table)

        form_layout.addRow("Food Name:", self.name_input)
        form_layout.addRow("Price:", self.price_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow(self.add_button)

        form_group.setLayout(form_layout)

        # --- Menu Table ---
        table_layout = QVBoxLayout()
        self.menu_label = QLabel("Current Menu")
        self.menu_label.setFont(QFont("Arial", 16))

        self.menu_table = QTableWidget(0, 4)
        self.menu_table.setHorizontalHeaderLabels(["Name", "Price", "Category", "Description"])

        table_layout.addWidget(self.menu_label)
        table_layout.addWidget(self.menu_table)

        main_layout.addWidget(form_group, 2)
        main_layout.addLayout(table_layout, 3)

        self.setLayout(main_layout)

    def add_food_to_table(self):
        name = self.name_input.text()
        price = self.price_input.text()
        category = self.category_input.currentText()
        description = self.description_input.toPlainText()

        if name and price:
            row_position = self.menu_table.rowCount()
            self.menu_table.insertRow(row_position)
            self.menu_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.menu_table.setItem(row_position, 1, QTableWidgetItem(price))
            self.menu_table.setItem(row_position, 2, QTableWidgetItem(category))
            self.menu_table.setItem(row_position, 3, QTableWidgetItem(description))

            # Clear inputs
            self.name_input.clear()
            self.price_input.clear()
            self.description_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FoodFormUI()
    window.show()
    sys.exit(app.exec())