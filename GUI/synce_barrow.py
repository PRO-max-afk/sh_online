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

class BarrowThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            self.synced_barrow_to_server()
    ##
    def synced_barrow_to_server(self):
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
        SELECT b_id,name,amount,type,phone,date,description,user_id,cus_id FROM barrow WHERE is_synced= 0
        ''')
        un_synced= cursor_sq.fetchall()
        try:
            
            cursor= data.cursor()
            for row in un_synced:
                (b_id,name,amount,b_type,phone,date,description,user_id,cus_id)= row

                cursor.execute("INSERT INTO barrow (b_id,name,amount,type,phone,date,description,user_id,cus_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                               (b_id,name,amount,b_type,phone,date,description,user_id,cus_id))
                print("info barrow successfully entered to server ✅")
                data.commit()

                cursor_sq.execute('UPDATE barrow set is_synced = 1 WHERE is_synced=0')
                conn_sq.commit()
        except pymysql.Error as e:
            print(f"{e} : online db error") 
        finally: 
            if conn_sq:
                conn_sq.close()
    