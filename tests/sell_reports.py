from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QFrame, QSizePolicy)
from PyQt6.QtGui import QPainter,QFont,QColor
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis


class SalesDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("گزارش فروش فروشگاه")
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #D9D9D9;")

        main_layout = QVBoxLayout(self)

        # --- تاریخ و روز
        date_layout = QVBoxLayout()
        date_label = QLabel("تاریخ: 1404/03/22")
        weekday_label = QLabel("امروز پنج‌شنبه")
        for lbl in (date_label, weekday_label):
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin: 4px; font-family: B Nazanin;")
        date_layout.addWidget(date_label)
        date_layout.addWidget(weekday_label)
        main_layout.addLayout(date_layout)

        # --- تب‌ها: روزی، هفته، ماهانه
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #c7c9c8; border-radius: 10px;")
        tabs_layout = QHBoxLayout(tab_frame)
        tab_frame.setFixedSize(500, 50)

        self.tab_buttons = []  # لیستی برای نگهداری دکمه‌ها

        def handle_tab_click(clicked_btn):
            for btn in self.tab_buttons:
                btn.setStyleSheet('''
                    QPushButton {
                        padding: 6px 18px; font-size: 14px;
                        background-color: transparent;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #d0d6d5;
                    }
                ''')
            clicked_btn.setStyleSheet('''
                QPushButton {
                    padding: 6px 18px; font-size: 14px;
                    background-color: white;
                    color: black;
                }
            ''')

        for name in ["روزی", "هفته", "ماهانه"]:
            btn = QPushButton(name)
            btn.setStyleSheet('''
                QPushButton {
                    padding: 6px 18px; font-size: 14px;
                    background-color: transparent;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #d0d6d5;
                }
            ''')
            btn.clicked.connect(lambda checked, b=btn: handle_tab_click(b))
            self.tab_buttons.append(btn)
            tabs_layout.addWidget(btn)

        main_layout.addWidget(tab_frame, alignment=Qt.AlignmentFlag.AlignHCenter)


        # --- باکس‌های آماری
        stats_layout = QHBoxLayout()
        stats = [
            ("مقدار فروش", "300"),
            ("فروش ناخالص", "90,000,000 IRR"),
            ("تخفیف ها", "8,000,000 IRR"),
            ("فروش خالص", "81,000,000 IRR"),
            ("هزینه‌ها", "22,000,000 IRR"),
            ("سود عملیاتی", "59,000,000 IRR"),
        ]
        for title, value in stats:
            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 10px;
                    color:black;
                    font-family: B Nazanin;
                    font-weight: bold;
                    padding: 5px;
                }
                QLabel {
                    font-size: 14px;
                    margin: 4px;
                }
            """)
            box_layout = QVBoxLayout(box)
            box_layout.addWidget(QLabel(title))
            val_label = QLabel(value)
            val_label.setStyleSheet("font-weight: bold; font-size: 14px; font-family: arial;")
            box_layout.addWidget(val_label)
            stats_layout.addWidget(box)
        main_layout.addLayout(stats_layout)

        # --- نمودار QChartView
        chart_view = self.create_bar_chart()
        chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(chart_view)

    def create_bar_chart(self):
        months = ["فروردین", "بَحر", "مرداد", "شهریور", "مهر", "آبان", "بهمن", "اسفند"]
        values = [8000000, 10000000, 14000000, 20000000, 35000000, 50000000, 42000000, 25000000]

        bar_set = QBarSet("مقدار فروش")
        bar_set.append(values)
        bar_set.setLabelFont(QFont("B Nazanin", 12))
        bar_set.setLabelBrush(QColor("black"))

        # بزرگ‌ترین مقدار را بررسی کن و رنگ را انتخاب کن
        max_value = max(values)
        if max_value >= 30000000:
            color = QColor("#2ecc71")  # سبز
        else:
            color = QColor("#e74c3c")  # قرمز

        bar_set.setColor(color)

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(False)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("نمودارها و آمارها")
        chart.setTitleFont(QFont("B Nazanin", 14, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("B Nazanin", 12, QFont.Weight.Bold))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, 60000000)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SalesDashboard()
    window.show()
    sys.exit(app.exec())
