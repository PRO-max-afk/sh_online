from PyQt6.QtWidgets import QFrame, QListWidget, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QFontDatabase
import sqlite3
import os

class ProductListPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(None, Qt.WindowType.Popup)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.load_all_fonts()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #aaa;
            }
            QListWidget {
                border: none;
                padding: 4px;
                font-size: 14px;
                color: black;
                font-family: B Nazanin;
            }
            QLineEdit {
                border: none;
                padding: 6px;
                border-bottom: 1px solid #ccc;
                font-size: 14px;
                font-family: B Nazanin;
                font-weight: bold;
                
            }
        """)
        self.setFixedWidth(220)

        self.db_path = r"D:\\projects\\sh_online\\Data\\sh_online.db"
        self.all_items = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("جستجوی محصول...")
        self.search_field.textChanged.connect(self.filter_list)

        self.list_widget = QListWidget()
        self.list_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.list_widget.setFocus()


        self.layout.addWidget(self.search_field)
        self.layout.addWidget(self.list_widget)
        

        self.animation = QPropertyAnimation(self, b"geometry")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            current_row = self.list_widget.currentRow()
            self.list_widget.setCurrentRow(current_row + 1)
        elif event.key() == Qt.Key.Key_Up:
            current_row = self.list_widget.currentRow()
            self.list_widget.setCurrentRow(current_row - 1)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            item = self.list_widget.currentItem()
            if item:
                self.list_widget.itemClicked.emit(item)
                self.close()

    def fetch_products(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("select id from users LIMIT 1")
            result= cur.fetchone()
            id_user= result[0]
            cur.execute("SELECT name FROM products where user_id=? ORDER BY name",(id_user,))
            rows = cur.fetchall()
            self.all_items = [r[0] for r in rows]
        except Exception as e:
            print("Database error:", e)
            self.all_items = []
        finally:
            conn.close()

    def show_with_animation(self, position):
        self.fetch_products()
        self.filter_list("")  # نمایش همه موارد در ابتدا
        self.setGeometry(position.x(), position.y(), self.width(), 0)
        self.animation.setDuration(200)
        self.animation.setStartValue(QRect(position.x(), position.y(), self.width(), 0))
        target_height = min(300, 50 + len(self.all_items) * 28)
        self.animation.setEndValue(QRect(position.x(), position.y(), self.width(), target_height))
        self.animation.start()
        self.show()

    def filter_list(self, text):
        filtered = [item for item in self.all_items if text.strip().lower() in item.lower()]
        self.list_widget.clear()
        self.list_widget.addItems(filtered)
        target_height = 50 + len(filtered) * 28
        self.setFixedHeight(min(300, target_height))
    ##
    ##fonts
    def load_all_fonts(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_folder = os.path.join(project_root, "fonts")

        if not os.path.exists(fonts_folder):
            print(f"⚠ پوشه فونت‌ها یافت نشد: {fonts_folder}")
            return

        for filename in os.listdir(fonts_folder):
            if filename.lower().endswith((".ttf", ".otf",".TTF")):
                font_path = os.path.join(fonts_folder, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"⚠ خطا در بارگذاری فونت: {filename}")
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        pass
    ##