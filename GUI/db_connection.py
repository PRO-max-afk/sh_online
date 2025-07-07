import pymysql

class Connection:
    def __init__(self):
        self.conn = None
        try:
            self.conn = pymysql.connect(
                host="50.6.154.40",
                user="ihrblgmy_shop_login",
                password="jm=BNOpE)^;_",
                database="ihrblgmy_shop",
                port=3306,  # ⬅️ اضافه کردن پورت به‌صورت صریح
                connect_timeout=10  # ⏱ کاهش تایم‌اوت برای تشخیص سریع‌تر
            )
            #print("✅ connected to server successfully")
        except pymysql.MySQLError as e:
            print(f"❌ no db connection online: {e}")

    def get_connection(self):
        return self.conn
