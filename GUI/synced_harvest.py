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

class HarvestThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            self.synced_harvest_to_server()
    ##
    def synced_harvest_to_server(self):
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
        SELECT name,amount,har_type,date,description,user_id FROM harvest WHERE is_synced= 0
        ''')
        un_synced= cursor_sq.fetchall()
        try:
            cursor= data.cursor()
            for row in un_synced:
                (name,amount,har_type,date,description,user_id)= row

                cursor.execute("INSERT INTO harvest (name,amount,har_type,date,description,user_id) VALUES(%s,%s,%s,%s,%s,%s)",
                               (name,amount,har_type,date,description,user_id))
                print("info harvest successfully entered to server ✅")
                data.commit()

                cursor_sq.execute('UPDATE harvest set is_synced = 1 WHERE is_synced=0')
                conn_sq.commit()
        except pymysql.Error as e:
            print(f"{e} : online db error") 
        finally: 
            if conn_sq:
                conn_sq.close()