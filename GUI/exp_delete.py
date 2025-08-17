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

class Delete_Exp(QDialog):
    def __init__(self,):
        super().__init__()
        self.setWindowTitle("حذف محصول")
        self.resize(400,185)
        self.setFixedSize(400,185)
        self.setStyleSheet("background-color: #E8E6E6;")
        self.load_all_fonts()
        self.center_window()
        
        self.in_UI()
        self.Button_UI()
        self.input_UI()
        self.label_UI()
        
        
    def in_UI(self):
        self.title_lb= QLabel("حذف محصول",self)
        ##
        self.name_lb= QLabel("نام محصول:",self)
        self.name_line= QLineEdit(self)
        ##
        self.quantity_lb= QLabel("تعداد محصول:",self)
        self.quantity_line= QLineEdit(self)
        ##
        self.delete_btn= QPushButton(self)
    ##
    def Button_UI(self):
        self.delete_btn.setGeometry(10,140,95,38)
        self.delete_btn.setText("حذف")
        self.delete_btn.setStyleSheet('''
            QPushButton{
                background-color: red;
                color: white;
                font-family: Vazir;
                font-size: 15px;
                font-weight: bold;
                border-radius: 15px;
                                      }
            QPushButton:hover{
                    background-color: #f55d76;
                    border-radius: 7px;
                                      }
            QPushButton:Pressed{
                    background-color: red;
                    border-radius: 15px;
                                      }
                                    
            ''')
        self.delete_btn.clicked.connect(self.delete_info)
    ##
    def input_UI(self):
        self.name_line.setGeometry(130, 45, 170, 35)
        self.name_line.setStyleSheet('''
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
        self.quantity_line.setGeometry(130, 110, 170, 35)
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
        self.title_lb.setGeometry(140,15,90,20)
        self.title_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 18px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.name_lb.setGeometry(300,50,85,20)
        self.name_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
        ##
        self.quantity_lb.setGeometry(302,115,85,20)
        self.quantity_lb.setStyleSheet('''
            font-family: B Nazanin;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ''')
    ###
    def set_info(self, name, quantity):
            self.name_line.setText(name)
            self.quantity_line.setText(str(quantity))
    ##
    def delete_info(self):
        name= self.name_line.text()
        quantity= self.quantity_line.text()
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, "Data","sh_online.db")
        if not os.path.exists(db_path):
            print("no db found!")
            return
        try:
            conn= sqlite3.connect(db_path)
            cursor= conn.cursor()
            cursor.execute("select id from users limit 1")
            id_user= cursor.fetchone()[0]
            cursor.execute("delete from products  where name=? and quantity=? and user_id=?",(name,quantity,id_user))
            conn.commit()
            MessageBox(text="محصول موفقانه حذف شد",title="موفقانه",type="info").show()
            self.name_line.clear()
            self.quantity_line.clear()
        except sqlite3.Error as e:
            print(f"{e}: offline db problem")
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
    def center_window(self):
        screen= self.screen().availableGeometry()
        size= self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window= Delete_Exp()
    window.show()
    sys.exit(app.exec())
