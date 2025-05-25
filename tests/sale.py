from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import sys

class SalesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("پنل فروش")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("background-color: #F6E8D7;")

        self.invoice_counter = 1
        self.invoices = {}

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # بالا: نوار جستجو
        top_bar = QHBoxLayout()

        date_label = QLabel("1401/01/10")
        date_label.setFont(QFont("Arial", 14))
        date_label.setStyleSheet("color: black;")

        search_btn = QPushButton("جستجو")
        search_btn.setStyleSheet("background-color: #2A64C5; color: white; padding: 8px 16px; border-radius: 4px;")

        search_input = QLineEdit()
        search_input.setPlaceholderText("...جستجوی محصولات")
        search_input.setFixedHeight(30)
        search_input.setStyleSheet("color: black;")

        title = QLabel("فروشات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: black;")

        top_bar.addWidget(date_label)
        top_bar.addWidget(search_btn)
        top_bar.addWidget(search_input, 1)
        top_bar.addWidget(title)
        top_bar.setSpacing(10)

        main_layout.addLayout(top_bar)

        # میانی: جدول و فرم
        middle_layout = QHBoxLayout()

        # جدول فروش
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        table_layout = QVBoxLayout(table_frame)

        table_title = QLabel("بل فروشات")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        table_title.setStyleSheet("color: black;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["اقلام فروخته شده","نمبر فاکتور","قیمت کل", "قیمت واحد", "نام محصول"])
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { border: 1px solid gray; color: black; } QHeaderView::section { background-color: transparent; border: 1px solid gray; color: black; border-radius: 7px; }")
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.table)

        # فرم فروش
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        form_layout = QVBoxLayout(form_frame)

        form_title = QLabel("فرم فروشات")
        form_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        form_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_title.setStyleSheet("color: black;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام محصول")
        self.name_input.setFixedHeight(35)
        self.name_input.setStyleSheet("color: black;")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("مقدار")
        self.qty_input.setFixedHeight(35)
        self.qty_input.setStyleSheet("color: black;")
        self.qty_input.textChanged.connect(self.update_total_price)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("قیمت واحد")
        self.unit_price_input.setFixedHeight(35)
        self.unit_price_input.setStyleSheet("color: black;")
        self.unit_price_input.textChanged.connect(self.update_total_price)

        self.total_price_input = QLineEdit()
        self.total_price_input.setPlaceholderText("قیمت کل")
        self.total_price_input.setFixedHeight(35)
        self.total_price_input.setStyleSheet("color: black;")
        self.total_price_input.setReadOnly(True)

        add_button = QPushButton("اضافه کردن")
        add_button.setStyleSheet("background-color: #2A64C5; color: white; padding: 10px; border-radius: 6px;")
        add_button.clicked.connect(self.add_product)

        form_layout.addWidget(form_title)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.unit_price_input)
        form_layout.addWidget(self.total_price_input)
        form_layout.addWidget(add_button)

        middle_layout.addWidget(table_frame, 2)
        middle_layout.addWidget(form_frame, 1)
        middle_layout.setSpacing(20)

        main_layout.addLayout(middle_layout,3)

        # پایین: فاکتورها
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        bottom_frame.setMinimumHeight(150)
        bottom_layout = QVBoxLayout(bottom_frame)

        label_layout = QHBoxLayout()
        faktur_label = QLabel("فاکتورها")
        faktur_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        faktur_label.setStyleSheet("color: black;")

        print_button = QPushButton("پرینت")
        print_button.setStyleSheet("background-color: #f2f2f2; padding: 8px 20px; border-radius: 6px; color: black;")
        print_button.clicked.connect(self.print_invoice)

        label_layout.addWidget(faktur_label)
        label_layout.addStretch()
        label_layout.addWidget(print_button)

        self.invoice_list = QListWidget()
        self.invoice_list.setStyleSheet("color: black;")
        self.invoice_list.itemClicked.connect(self.load_invoice)

        bottom_layout.addLayout(label_layout)
        bottom_layout.addWidget(self.invoice_list)

        main_layout.addWidget(bottom_frame,2)

    def add_product(self):
        name = self.name_input.text()
        qty = self.qty_input.text()
        unit_price = self.unit_price_input.text()
        total_price = self.total_price_input.text()

        if name and qty and unit_price and total_price:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(total_price))
            self.table.setItem(row, 1, QTableWidgetItem(unit_price))
            self.table.setItem(row, 2, QTableWidgetItem(name))

            for col in range(3):
                self.table.item(row, col).setForeground(Qt.GlobalColor.black)

            self.name_input.clear()
            self.qty_input.clear()
            self.unit_price_input.clear()
            self.total_price_input.clear()

    def update_total_price(self):
        try:
            qty = float(self.qty_input.text())
            unit_price = float(self.unit_price_input.text())
            total = qty * unit_price
            self.total_price_input.setText(str(round(total, 2)))
        except ValueError:
            self.total_price_input.clear()

    def print_invoice(self):
        items = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 2).text()
            unit = self.table.item(row, 1).text()
            total = self.table.item(row, 0).text()
            items.append((name, unit, total))

        invoice_number = f"فاکتور {self.invoice_counter}"
        self.invoices[invoice_number] = items
        self.invoice_list.addItem(invoice_number)
        self.invoice_counter += 1

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            html = "<h2 align='center'>فاکتور فروش</h2><table border='1' width='100%' cellspacing='0' cellpadding='4'><tr><th>نام محصول</th><th>قیمت واحد</th><th>قیمت کل</th></tr>"
            for name, unit, total in items:
                html += f"<tr><td>{name}</td><td>{unit}</td><td>{total}</td></tr>"
            html += "</table>"
            doc.setHtml(html)
            doc.print(printer)
            self.table.clear()

    def load_invoice(self, item):
        invoice_name = item.text()
        if invoice_name in self.invoices:
            self.table.setRowCount(0)
            for name, unit, total in self.invoices[invoice_name]:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(total))
                self.table.setItem(row, 1, QTableWidgetItem(unit))
                self.table.setItem(row, 2, QTableWidgetItem(name))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesPanel()
    window.show()
    sys.exit(app.exec())
