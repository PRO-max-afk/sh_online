from PyQt6.QtCore import QThread
import pymysql
import sqlite3
import os
from PyQt6.QtCore import QThread
import pymysql
import sqlite3
import os
from db_connection import Connection

class WorkerThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db_connect= Connection().get_connection()
        if self.db_connect:
            self.synced_worker_to_server()
            self.synced_salaries_to_server()
    ##
    def synced_worker_to_server(self):
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
        SELECT employee_id,first_name,last_name,phone,email,hire_date,address,position,salary,status,user_id FROM employees WHERE is_synced= 0
        ''')
        un_synced= cursor_sq.fetchall()
        try:
            
            cursor= data.cursor()
            for row in un_synced:
                (employee_id,first_name,last_name,phone,email,hire_date,address,position,salary,status,user_id) = row

                cursor.execute(
                    "INSERT INTO employees (employee_id,first_name,last_name,phone,email,hire_date,address,position,salary,status,user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (employee_id,first_name,last_name,phone,email,hire_date,address,position,salary,status,user_id)
                )
                print(f"employee {employee_id} synced to server ✅")
                data.commit()

                cursor_sq.execute('UPDATE employees SET is_synced = 1 WHERE employee_id = ?', (employee_id,))
                conn_sq.commit()

        except pymysql.Error as e:
            print(f"{e} : online db error") 
        finally: 
            if conn_sq:
                conn_sq.close()
    ##woker salary
    def synced_salaries_to_server(self):
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
        SELECT employee_id,salary_id,pay_date,amount,note FROM salaries WHERE is_synced= 0
        ''')
        un_synced= cursor_sq.fetchall()
        try:
            
            cursor= data.cursor()
            for row in un_synced:
                (employee_id,salary_id,pay_date,amount,note) = row

                cursor.execute(
                    "INSERT INTO employees (employee_id,first_name,last_name,phone,email,hire_date,address,position,salary,status,user_id) VALUES(%s,%s,%s,%s,%s)",
                    (employee_id,salary_id,pay_date,amount,note)
                )
                print(f"salary {salary_id} synced to server ✅")
                data.commit()

                cursor_sq.execute('UPDATE salaries SET is_synced = 1 WHERE employee_id = ?', (employee_id,))
                conn_sq.commit()

        except pymysql.Error as e:
            print(f"{e} : online db error") 
        finally: 
            if conn_sq:
                conn_sq.close()
    