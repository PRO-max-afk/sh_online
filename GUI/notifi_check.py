from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import time
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import datetime
import time
import os
from message_b import MessageBox
from db_connection import Connection

class NotificationChecker(QThread):
    new_message = pyqtSignal(str, str)  # ارسال همزمان product_name و message
    new_count = pyqtSignal(int)
    exp_msg= pyqtSignal(list)
    disc_msgs= pyqtSignal(list)
    qua_msg= pyqtSignal(list)
    
    

    def __init__(self):
        super().__init__()
        self.running = True
        self.shown_messages = set()
        self.count_ms = set()
        self.last_expired_products = []  # لیست آخرین محصولات انقضاشده‌ای که نمایش داده شده‌اند
        self.last_dics_exp_products=[]
        self.last_quantity_products= []
        self.last_total_count= None


    def run(self):
        self.db_info= Connection().get_connection()
        if self.db_info:
            self.count_notification()
        else:
            self.count_offline_notification()
    def count_notification(self):
        while self.running:
            db_config = Connection().get_connection()
            if not db_config:
                time.sleep(5)
                continue

            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            try:
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users;")
                res_id = cursor_sq.fetchone()
                id_user = res_id[0]
            except Exception as e:
                print(f"{e}: خطا در دیتابیس لوکال")
                return

            try:
                cursor = db_config.cursor()

                # پیام محصول
                cursor.execute("""
                    SELECT product_name, product_message 
                    FROM inventories 
                    WHERE denied=1 AND user_id=%s 
                    ORDER BY user_id DESC 
                    LIMIT 1;
                """, (id_user,))
                result = cursor.fetchone()

                # تعداد پیام‌ها
                cursor.execute("""
                    SELECT COUNT(product_message) 
                    FROM inventories 
                    WHERE denied=1 AND user_id=%s;
                """, (id_user,))
                m_count = cursor.fetchone()[0]
                ##
                # تعداد تاریخ‌های انقضا معتبر
                jalali_date = datetime.date.today().strftime("%Y/%m/%d")
                cursor.execute('''
                    SELECT product_name from inventories 
                        WHERE expiration_dates < %s AND user_id = %s
                ''',(jalali_date,id_user))
                exp_message= cursor.fetchall()
                #
                if exp_message:
                    exp_data = [row[0] for row in exp_message]

                    # فقط زمانی سیگنال ارسال شود که لیست جدید با قبلی فرق داشته باشد
                    if exp_data != self.last_expired_products:
                        self.last_expired_products = exp_data.copy()
                        self.exp_msg.emit(exp_data)
                        print(exp_data)
                
                #
                cursor.execute("""
                    SELECT COUNT(expiration_dates) 
                    FROM inventories 
                    WHERE expiration_dates < %s AND user_id=%s;
                """, (jalali_date, id_user))
                e_count = cursor.fetchone()[0]
                ###
                cursor.execute('''
                SELECT product_name from inventories
                    WHERE expir_discount=0 AND user_id= %s
                ''',(id_user,))
                disc_result= cursor.fetchall()
                if disc_result:
                    disc_message= [rows[0] for rows in disc_result]
                    if disc_message != self.last_dics_exp_products:
                        self.last_dics_exp_products= disc_message.copy()
                        self.disc_msgs.emit(disc_message)
                ##
                cursor.execute('''
                    SELECT COUNT(discount_percent) FROM inventories 
                    WHERE user_id= %s AND expir_discount= 0
                ''',(id_user,))
                expire_disc_result= cursor.fetchone()
                if expire_disc_result:
                    exp_count= expire_disc_result[0]
                
                ##
                cursor.execute('''
                    SELECT product_name from inventories 
                        WHERE quantity <= 20 and user_id= %s
                ''',(id_user,))
                qua_msg= cursor.fetchall()
                if qua_msg:
                    quantity_message= [row[0] for row in qua_msg]
                    if quantity_message != self.last_quantity_products:
                        self.last_quantity_products= quantity_message.copy()
                        self.qua_msg.emit(quantity_message)
                cursor.execute('''
                    SELECT COUNT(quantity) as quanity from inventories WHERE quantity <= 20  and user_id= %s
                    ''',(id_user,))
                empty_result= cursor.fetchone()
                if empty_result:
                    empty_count= empty_result[0]

                ##
                total_count = m_count + e_count + empty_count + exp_count

                if total_count != self.last_total_count:
                    self.last_total_count = total_count
                    self.new_count.emit(total_count)
                    print(self.last_total_count)



                if result:
                    pro_name, message = result
                    unique_key = f"{pro_name}::{message}"
                    if unique_key not in self.shown_messages:
                        self.shown_messages.add(unique_key)
                        self.new_message.emit(pro_name, message)
                

                db_config.close()
            except pymysql.MySQLError as e:
                print(f"{e} : خطا در اتصال یا کوئری به دیتابیس")

            time.sleep(2)

    ##offilne:
    def count_offline_notification(self):
        while self.running:
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # رفتن یک سطح بالاتر از پوشه GUI
            root_dir = os.path.dirname(base_dir)
            db_path = os.path.join(root_dir, 'Data', 'sh_online.db')

            if not os.path.exists(db_path):
                MessageBox(text="فایل دیتابیس محلی یافت نشد!", title="❌ خطا", type="error").show()
                return

            try:
                conn_sq = sqlite3.connect(db_path)
                cursor_sq = conn_sq.cursor()
                cursor_sq.execute("SELECT id FROM users;")
                res_id = cursor_sq.fetchone()
                id_user = res_id[0]
            except Exception as e:
                print(f"{e}: خطا در دیتابیس لوکال")
                return

            try:
                # تعداد تاریخ‌های انقضا معتبر
                jalali_date = datetime.date.today().strftime("%Y/%m/%d")
                cursor_sq.execute('''
                    SELECT name from products 
                        WHERE expire_date < ?
                ''',(jalali_date,))
                exp_msg= cursor_sq.fetchall()
                #
                if exp_msg:
                    exp_info= [row[0] for row in exp_msg]
                    if exp_info != self.last_expired_products:
                        self.last_expired_products= exp_info.copy()
                        self.exp_msg.emit(exp_info)
                        print(exp_info)

                cursor_sq.execute("""
                    SELECT COUNT(expire_date) 
                    FROM products 
                    WHERE expire_date < ? AND user_id=?;
                """, (jalali_date, id_user))
                e_count = cursor_sq.fetchone()[0]
                ##
                cursor_sq.execute('''
                SELECT name from products where expire_discount=0
                ''')
                disc_data= cursor_sq.fetchall()
                if disc_data:
                    disc_info= [row[0] for row in disc_data]
                    if disc_info != self.last_dics_exp_products:
                        self.last_dics_exp_products= disc_info.copy()
                        self.disc_msgs.emit(disc_info)
                cursor_sq.execute('''
                    SELECT COUNT(discount_percent) FROM products 
                    WHERE user_id= ? AND expire_discount= 0
                ''',(id_user,))
                expire_disc_result= cursor_sq.fetchone()
                if expire_disc_result:
                    exp_count= expire_disc_result[0]
                
                ##
                cursor_sq.execute('''
                    SELECT name from products
                        WHERE quantity <= 20 
                ''')
                qua_msg= cursor_sq.fetchall()
                if qua_msg:
                    qua_info= [row[0] for row in qua_msg]
                    if qua_info != self.last_quantity_products:
                        self.last_quantity_products= qua_info.copy()
                        self.qua_msg.emit(qua_info)

                cursor_sq.execute('''
                    SELECT COUNT(quantity) as quanity from products WHERE quantity <= 20  and user_id= ?
                    ''',(id_user,))
                empty_result= cursor_sq.fetchone()
                if empty_result:
                    empty_count= empty_result[0]
                
                


                total_count = e_count + empty_count + exp_count

                if total_count not in self.count_ms:
                    self.count_ms.add(total_count)
                    self.new_count.emit(total_count)  # ارسال مقدار عددی
                time.sleep(2)
                

                
            except sqlite3.Error as e:
                print(f"{e} : خطا در اتصال یا کوئری به دیتابیس")
            finally:
                if conn_sq:
                    conn_sq.close()
    



