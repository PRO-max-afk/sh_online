from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QFrame,QGraphicsDropShadowEffect,QComboBox,QGridLayout,QFileDialog,
    QLineEdit, QFileDialog, QHBoxLayout, QDialog,QWidget)
from PyQt6.QtGui import QPixmap, QFont,QColor,QIcon,QFontDatabase
import sys
from datetime import date
from profile_picture import ProfileImage
from message_b import MessageBox
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import os
import sqlite3
from calendars import JalaliCalendar

class Worker_Salary(QDialog):
    def __init__(self,worker_page=None):
        super().__init__()
        self.setWindowTitle("اجراء معاش")
        self.resize(520,230)
        self.setFixedSize(520,230)
        self.setStyleSheet("background-color: #E8E6E6;")
        self.load_all_fonts()
        self.center_window()
        self.worker_page= worker_page
        self.in_UI()
        self.Button_UI()
        self.input_UI()
        self.label_UI()
        self.worker_names()
        
        
    def in_UI(self):
        self.title_lb= QLabel("اجراء معاش",self)
        ##
        self.name_lb= QLabel("نام کارمند:",self)
        self.name_combo= QComboBox(self)
        ##
        self.date_lb= QLabel(" تاریخ اجراء:",self)
        self.date_line= QLineEdit(self)
        ##
        self.quantity_lb= QLabel(" مقدار معاش:",self)
        self.quantity_line= QLineEdit(self)
        ##
        #self.delete_btn= QPushButton(self)
    ##
    def Button_UI(self):
        self.save_btn = QPushButton("اجرای معاش", self)
        self.save_btn.setGeometry(200, 180, 120, 35)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2251DB;
                color: white;
                font-family: 'B Nazanin';
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #498bf5;  
            }
            QPushButton:pressed {
                background-color: #2251DB;
            }
        """)
        self.save_btn.clicked.connect(self.worker_salary)
        ##
        self.calendar_btn= QPushButton(self.date_line)
        self.calendar_btn.move(4,2)
        self.cale_icon= QIcon(self.get_asset_path("calendar_8265298.png"))
        self.calendar_btn.setIcon(self.cale_icon)
        self.calendar_btn.setIconSize(QtCore.QSize(20,20))
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                padding: 5px;
                border-radius: 7px; /* گردی برای همه حالت‌ها */
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* خاکستری ملایم هنگام کلیک */
            }
        ''')
        self.calendar_btn.clicked.connect(self.show_calendar)
    ##
    def input_UI(self):
        self.name_combo.setGeometry(280,70,150,35)
        self.name_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.name_combo.currentTextChanged.connect(self.select_info)
        self.name_combo.addItem("انتخاب")
        self.name_combo.setCurrentIndex(0)
        self.name_combo.setStyleSheet('''
            QComboBox {
                background-color: white;
                font-family: "B Nazanin";
                font-size: 16px;
                font-weight: bold;
                color: #000;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                text-align: right;
                padding: 6px 10px 6px 30px; /* فضای کافی برای فلش در سمت چپ */
                padding-left: 35px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top left; /* انتقال فلش به چپ */
                width: 30px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url(assets/Down Button.png);
                width: 20px;
                height: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: white;  /* پس‌زمینه سفید */
                color: black;             /* متن سیاه */
                text-align: left;        /* تراز متن به راست */
                font-family: "B Nazanin";
                font-size: 15px;
                border: 1px solid #bfbfbf;
                border-radius: 8px;
                selection-background-color: #f0f0f0;  /* رنگ انتخاب آیتم */
            }
            ''')
        ##
        self.date_line.setGeometry(260, 120, 170, 35)
        self.date_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            color: black;
            padding: 7px;
        ''')
        ##
        self.quantity_line.setGeometry(10, 120, 170, 35)
        #self.quantity_line.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.quantity_line.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.quantity_line.setStyleSheet('''
            background-color: white;
            font-family: Roboto,'B Nazanin';
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #c2c2c2;
            border-radius: 7px;
            color: black;
            padding: 7px;
        ''')
    ##
    def label_UI(self):
        self.title_lb.setGeometry(190,15,90,20)
        self.title_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 18px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.name_lb.setGeometry(410,75,90,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
                ''')
        ##
        self.date_lb.setGeometry(420,125,85,20)
        self.date_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.quantity_lb.setGeometry(170,125,85,20)
        self.quantity_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
    ##
    def show_calendar(self):
        self.calendar_popup = JalaliCalendar(self)
        pos = self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomRight())
        self.calendar_popup.show_with_animation(pos)
    ##
    def set_selected_date(self, date_str):
        self.date_line.setText(date_str)
        self.date_line.setAlignment(Qt.AlignmentFlag.AlignRight)  
    ###functions
    def set_info(self,name,quantity):
            self.quantity_line.setText(str(quantity))
            self.name_combo.setCurrentText(name)
    ##
    def worker_names(self):
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no db path found!")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user= cursor.fetchone()[0]
            cursor.execute("select first_name || ' '|| last_name as full_name from employees where user_id=? ",(id_user,))
            result= cursor.fetchall()
            if result:
                self.name_combo.addItems([r[0] for r in result])
        except sqlite3.Error as e:
            print(f"db error found:{e}")
    ##
    def select_info(self):
        name= self.name_combo.currentText()
        if name == "انتخاب":
            #MessageBox(text="نام شخص را انتخاب کنید",title="هشدار",type="warning").show()
            pass
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no db path found!")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user= cursor.fetchone()[0]
            cursor.execute("select salary from employees where first_name || ' ' || last_name=? and user_id=?",(name,id_user))
            result= cursor.fetchone()
            if result:
                self.quantity_line.setText(str(result[0]))
        except sqlite3.Error as e:
            print(f"db offline error:{e}")
    
    def worker_salary(self):
        name = self.name_combo.currentText()
        pay_date = self.date_line.text().strip()
        amount = self.quantity_line.text().strip()

        if name == "انتخاب" or not amount:
            MessageBox(text="نام کارمند و مقدار معاش را وارد کنید", title="هشدار", type="warning").show()
            return
    
        try:
            amount = float(amount)
        except ValueError:
            MessageBox(text="مقدار معاش باید عددی باشد", title="خطا", type="error").show()
            return
        if amount == 0:
            MessageBox(text="معاش کارمند قبلاً اجراء شده", title="هشدار", type="warning").show()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        db_path = os.path.join(root_dir, "Data", "sh_online.db")

        if not os.path.exists(db_path):
            MessageBox(text="دیتابیس یافت نشد!", title="خطا", type="error").show()
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # پیدا کردن id کارمند از روی نام
            cursor.execute("""
                SELECT employee_id,salary FROM employees 
                WHERE first_name || ' ' || last_name = ?
            """, (name,))
            emp = cursor.fetchone()
            if not emp:
                MessageBox(text="کارمند یافت نشد!", title="خطا", type="error").show()
                return

            emp_id = emp[0]
            salary= emp[1]

            # درج رکورد در جدول salaries
            final_amount= 0
            final_amount= amount - salary
            cursor.execute("""
                INSERT INTO salaries (employee_id, pay_date, amount)
                VALUES (?, ?, ?)
            """, (emp_id, pay_date if pay_date else None, amount))
            cursor.execute("UPDATE employees SET salary=? where employee_id=?",(final_amount,emp_id))

            conn.commit()
            MessageBox(text="معاش با موفقیت اجرا شد ", title="موفق", type="info").show()
            self.quantity_line.clear()
            self.date_line.clear()
            self.name_combo.setCurrentIndex(0)

        except sqlite3.Error as e:
            print(f"db error: {e}")
            MessageBox(text="خطا در ثبت معاش", title="خطا", type="error").show()
        finally:
            conn.close()
      ##images
    def get_asset_path(self, filename):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "assets", filename)
        if os.path.exists(image_path):
            return image_path
        else:
            print(f"⚠ فایل یافت نشد: {image_path}")
            return None
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
    def closeEvent(self, event):
        if self.worker_page:
            self.worker_page.show_wk_info()
        event.accept()
    ##
    def center_window(self):
        screen= self.screen().availableGeometry()
        size= self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window= Worker_Salary()
    window.show()
    sys.exit(app.exec())
