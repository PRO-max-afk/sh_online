import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
Create TABLE IF NOT EXISTS sale_factor(
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            barcode TEXT Not NULL,
            factor_number INTEGER,
            sale_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            quantity REAL NOT NULL,
            product_type TEXT,
            sale_type TEXT,
            discount REAL DEFAULT 0,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_synced INTEGER DEFAULT 0
               )
''')

cursor.execute('''
Create TABLE IF NOT EXISTS factor_number(
            sale_id INTEGER );
''')