import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            invent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT,
            buy_price REAL,
            sale_price REAL,
            quantity INTEGER,
            expire_date TEXT,
            image_path TEXT,
            user_id INTEGER
        );
    ''')
