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
import requests

class YearThread(QThread):
    year_data= pyqtSignal()
    full_info= pyqtSignal(dict)
    full_chart= pyqtSignal(float)
    chart_data= pyqtSignal(list)
    def __init__(self):
        super().__init__()
        #self.year_selected= year_selected

    def run(self):
        self.full_data()
        self.year_data()
    
    def year_data(self):
        pass
    def full_data(self):
        data= self.get_db_config()
        if not data:
            print("خطا در اتصال به سرور")
            return
        ##ofline
        base_dir= os.path.dirname(os.path.abspath(__file__))
        root_dir= os.path.dirname(base_dir)
        db_path= os.path.join(root_dir, 'Data', 'sh_online.db')
        if not os.path.exists(db_path):
            MessageBox(text="مسیر دیتابیس آفلاین پیدا نشد",title="ناموفق",type="error").show()
       ##offline db
        try:
            conn_sq= sqlite3.connect(db_path)
            cursor_sq= conn_sq.cursor()
            cursor_sq.execute('select id from users LIMIT 1')
            id_result= cursor_sq.fetchone()
            if id_result:
                id_user= id_result[0]
            else:
                print("آیدی پیدا نشد")
        except sqlite3.Error as e:
            print(f"{e}: خطا در دیتابیس آفلاین")
        
        ##online db
        try:
            conn= pymysql.connect(
                host= data["host"],
                user= data["user"],
                password= data["password"],
                database= data["database"])
            cursor= conn.cursor()
            
            cursor.execute('''
            SELECT SUM(total) FROM sale_factor WHERE user_id = %s
            ''',(id_user,))
            sale_result= cursor.fetchone()
            total_sale_f=0
            if sale_result:
                total_sale_f += float(sale_result[0]) if sale_result[0] else 0
                print(f" total sale off :{total_sale_f}")
            
            ##online sale
            cursor.execute('''
            SELECT SUM(price) FROM orders WHERE user_id = %s
            ''',(id_user,))
            online_result= cursor.fetchone()
            total_sale_on=0
            if sale_result:
                    total_sale_on += float(online_result[0]) if online_result[0] else 0
                    print(f" total sale online :{total_sale_on}")
            ##
            total_sale= total_sale_f + total_sale_on
            ##
            cursor.execute("SELECT SUM(total) FROM inventories WHERE user_id= %s",(id_user,))
            buy_result= cursor.fetchone()
            total_buy=0
            if buy_result:
                    total_buy += float(buy_result[0]) if buy_result[0] else 0
                    print(f"{total_buy} :  total buy")
            ###
            cursor.execute("SELECT SUM(profit) FROM sale_factor WHERE user_id= %s",(id_user,))
            profit_result= cursor.fetchone()
            total_profit=0
            if profit_result:
                    total_profit += float(profit_result[0]) if profit_result[0] else 0
                    print(f"{total_profit} :  total profit")
            ##
            box_stats={
                "total_buy" : total_buy,
                "total_sale" : total_sale,
                "profit" :total_profit,
                "harvest" : 0,
                "total_barrow" : 0,
                "current_capital" : 0,
                "total_cush" : total_profit, 
            }
            self.full_info.emit(box_stats)
            
            ### chart_info
            # ارسال مقادیر به عنوان لیست برای چارت
            chart_values = [
                box_stats["total_buy"],
                box_stats["total_sale"],
                box_stats["profit"],
                box_stats["harvest"],
                box_stats["total_barrow"],
                box_stats["current_capital"],
                box_stats["total_cush"],
            ]
            self.chart_data.emit(chart_values)

        except pymysql.Error as e:
            print(f"{e}: online db error")
    
    ##
    def get_db_config(self):

        url = "https://aryaict.com/connect.php"

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        cookies = {
            'humans_21909': '1'
        }

        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=60)

            if response.status_code != 200:
                print("⚠️ خطای ارتباطی:", response.status_code, response.text)
                response.raise_for_status()

            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست! محتوای پاسخ:\n" + response.text)

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است:\n" + str(data))

            return data

        except Exception as e:
            print("❌ خطا در دریافت کانفیگ:", e)
            return None


