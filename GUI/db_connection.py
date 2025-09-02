import pymysql

class Connection:
    def __init__(self):
        self.conn = None
        self.online = False  # فلگ وضعیت اتصال

    def connect(self):
        """تلاش برای اتصال به سرور آنلاین"""
        try:
            self.conn = pymysql.connect(
                host="50.6.154.40",
                user="ihrblgmy_shop_login",
                password="jm=BNOpE)^;_",
                database="ihrblgmy_shop",
                port=3306,
                connect_timeout=5  # ⏱ تایم اوت کوتاه‌تر
            )
            self.online = True
            # print("✅ connected to server successfully")
        except pymysql.MySQLError as e:
            self.conn = None
            self.online = False
            # print(f"❌ no db connection online: {e}")

    def get_connection(self):
        """برگشت اتصال فعال یا None"""
        if self.conn is None or not self.online:
            self.connect()
        return self.conn
