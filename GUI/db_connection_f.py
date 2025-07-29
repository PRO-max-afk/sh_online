import pymysql
import requests

class Connection:
    def __init__(self):
        self.conn = None
        try:
            config = self.get_db_config()  # ← دریافت پیکربندی آنلاین

            if not config:
                raise Exception("پیکربندی دریافت نشد")

            self.conn = pymysql.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                port=int(config.get('port', 3306)),  # اگر port داده نشده، از 3306 استفاده شود
                connect_timeout=10
            )
            print("✅ اتصال موفق به دیتابیس")

        except Exception as e:
            print(f"❌ خطا در اتصال به دیتابیس: {e}")
            self.conn = None

    def get_connection(self):
        return self.conn

    def get_db_config(self):
        try:
            url = "https://aryaict.com/connect.php"
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            cookies = {'humans_21909': '1'}
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

            if response.status_code != 200:
                print("⚠️ خطای ارتباطی:", response.status_code, response.text)
                return None

            if "application/json" not in response.headers.get('Content-Type', ''):
                print("⚠️ پاسخ JSON نبود:", response.text)
                return None

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                print("⚠️ پیکربندی ناقص:", data)
                return None

            return data

        except Exception as e:
            print(f"❌ خطا در دریافت کانفیگ: {e}")
            return None
