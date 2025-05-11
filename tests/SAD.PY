class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    ##
    def get_db_config(self):
        url = "https://aryaict.com/connect.php"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'MyApp/1.0',
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            if "application/json" not in response.headers.get('Content-Type', ''):
                raise ValueError("پاسخ سرور JSON نیست!")

            data = response.json()
            required_keys = ("host", "user", "password", "database")
            if not all(k in data for k in required_keys):
                raise ValueError("پاسخ JSON ناقص است")

            return data
        except Exception as e:
            print("خطا در دریافت config:", e)
            return None
        ## 
    ##
    def load_all_data(self):
        self.db_data = self.get_db_config()
        if not self.db_data:
            self.error_occurred.emit("لطفاً اینترنت خود را بررسی کنید❌ اتصال به سرور ناموفق بود")
            return

        conn = None
        conn_sq = None
        try:
            # اتصال به دیتابیس اصلی (MySQL)
            conn = pymysql.connect(
                host=self.db_data["host"],
                user=self.db_data["user"],
                password=self.db_data["password"],
                database=self.db_data["database"]
            )
            cursor = conn.cursor()

            # اتصال به SQLite برای دریافت user_id
            conn_sq = sqlite3.connect('Data\\sh_online.db')
            cursor_sq = conn_sq.cursor()
            cursor_sq.execute('SELECT id FROM users LIMIT 1')
            user_row = cursor_sq.fetchone()

            if not user_row:
                self.error_occurred.emit("شناسه کاربر در دیتابیس لوکال یافت نشد❌")
                return

            id_user = user_row[0]

            # بارگذاری محصولات فقط برای user_id خاص
            cursor.execute('''
                SELECT product_name, barcode,category,sub_category,buy_date,buy_price, sell_price,
                           big_category,quantity, expiration_dates, product_image,store_name, 
                           new_price, discount_percent, big_price, total
                FROM inventories
                WHERE user_id = %s
                ORDER BY invent_id DESC
            ''', (id_user,))
            products = cursor.fetchall()

            product_list = []
            for product in products:
                name, barcode,category, sub_category,buy_date,buy_price, sale_price,big_category,quantity, exp_date, image_path, store_name, new_price, discount_percent, big_price, total= product

                product_info = {
                    "name": name,
                    "barcode": barcode,
                    "category":category,
                    "sub_category": sub_category,
                    "buy_date": buy_date,
                    "buy_price": float(buy_price) if isinstance(buy_price, Decimal) else buy_price,
                    "sale_price": float(sale_price) if isinstance(sale_price, Decimal) else sale_price,
                    "big_category": big_category,
                    "quantity": float(quantity) if isinstance(quantity, Decimal) else quantity,
                    "expire_date": exp_date,
                    "image_path": image_path,
                    "user_id": id_user,
                    "store_name": store_name,
                    "new_price": float(new_price) if isinstance(new_price, Decimal) else new_price,
                    "discount_percent": float(discount_percent) if isinstance(discount_percent, Decimal) else discount_percent,
                    "big_price": float(big_price) if isinstance(big_price, Decimal) else big_price,
                    "total": float(total) if isinstance(total, Decimal) else total
                }
                product_list.append(product_info)

            # ذخیره یا آپدیت در SQLite
            self.store_in_local_db(product_list)

            self.data_loaded.emit(product_list)

        except Exception as e:
            self.error_occurred.emit(f"خطا در بارگذاری محصولات: {e}")

        finally:
            if conn:
                conn.close()
            if conn_sq:
                conn_sq.close()

    ##
    def store_in_local_db(self, product_list):
        conn = sqlite3.connect("Data\\sh_online.db")
        cursor = conn.cursor()

        for product in product_list:
            if all(key in product for key in ["barcode", "name", "category","sub_category","buy_date","buy_price", "sale_price","big_category","store_name", "new_price", "discount_percent", "big_price", "total", "quantity", "expire_date", "image_path", "user_id"]):
                
                # بررسی وجود محصول با barcode
                cursor.execute("SELECT COUNT(*) FROM products WHERE barcode = ?", (product["barcode"],))
                exists = cursor.fetchone()[0]

                if exists:
                    # اگر وجود داشت: آپدیت کن
                    cursor.execute('''
                        UPDATE products SET
                            barcode=?,name = ?, category=?,sub_category=?,buy_date=?,buy_price = ?, sale_price = ?, store_name = ?, new_price = ?, 
                            discount_percent = ?, big_price = ?, total = ?, quantity = ?, expire_date = ?, 
                            image_path = ?, user_id = ?
                        WHERE barcode = ?
                    ''', (
                        product["barcode"],
                        product["name"],
                        product["category"],
                        product["sub_category"],
                        product["buy_date"],
                        product["buy_price"],
                        product["sale_price"],
                        product["big_category"],
                        product["store_name"],
                        product["new_price"],
                        product["discount_percent"],
                        product["big_price"],
                        product["total"],
                        product["quantity"],
                        product["expire_date"],
                        product["image_path"],
                        product["user_id"]
                    ))
                else:
                    # اگر وجود نداشت: درج کن
                    cursor.execute('''
                        INSERT INTO products (barcode, name, category,sub_category,buy_date,
                                   buy_price, sale_price,big_category,store_name, new_price, discount_percent, big_price,
                                    total, quantity, expire_date, image_path, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)
                    ''', (
                        product["barcode"],
                        product["name"],
                        product["category"],
                        product["sub_category"],
                        product["buy_date"],
                        product["buy_price"],
                        product["sale_price"],
                        product["big_category"],
                        product["store_name"],
                        product["new_price"],
                        product["discount_percent"],
                        product["big_price"],
                        product["total"],
                        product["quantity"],
                        product["expire_date"],
                        product["image_path"],
                        product["user_id"]
                    ))

        conn.commit()
        conn.close()




    def run(self):
        self.load_all_data()
