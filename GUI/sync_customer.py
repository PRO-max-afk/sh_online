from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import requests
import sqlite3
import os
from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
import sqlite3
import jdatetime
from datetime import datetime
import datetime
from message_b import MessageBox
import os
from db_connection import Connection

class CustomerThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            self.synced_customer_to_server()
    ##
    def synced_customer_to_server(self):
        data= Connection().get_connection()
        if not data:
            print("no connection to the server to send info")
            return
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not db_path:
            print("no offline connection!")
            return
        conn_sq= sqlite3.connect(db_path)
        cursor_sq= conn_sq.cursor()
        cursor_sq.execute('''
        SELECT id,name,last_name,phone,email,register_date,user_id FROM customers WHERE is_synced= 0
        ''')
        un_synced= cursor_sq.fetchall()
        try:
            
            cursor= data.cursor()
            for row in un_synced:
                (id_e, name, last_name, phone, email, register_date, user_id) = row

                cursor.execute(
                    "INSERT INTO customer (id,name,last_name,phone,email,register_date,user_id) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (id_e, name, last_name, phone, email, register_date, user_id)
                )
                print(f"Customer {id_e} synced to server ✅")
                data.commit()

                cursor_sq.execute('UPDATE customers SET is_synced = 1 WHERE id = ?', (id_e,))
                conn_sq.commit()

        except pymysql.Error as e:
            print(f"{e} : online db error") 
        finally: 
            if conn_sq:
                conn_sq.close()
    