import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            invent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT Not NULL,
            name TEXT,
            category TEXT,
            sub_category TEXT,
            buy_date TEXT,
            buy_price REAL,
            sale_price REAL,
            big_price REAL,
            big_sub REAL,
            big_category TEXT,
            quantity REAL,
            new_quantity REAL,
            update_date TEXT,
            discount_percent,
            new_price REAL,
            store_name TEXT,
            total REAL,
            big_quantity INTEGER,
            is_synced INTEGER DEFAULT 0,
            expire_date TEXT,
            image_path TEXT,
            big_sub_display TEXT,
            user_id INTEGER
        );
    ''')


cursor.execute('''
    Create TABLE IF NOT EXISTS product_details(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight TEXT,
            production_date TEXT,
            brand TEXT,
            production_place TEXT,
            product_state TEXT,
            more_details TEXT,
            invent_id INTEGER,
            keep_place TEXT,
            is_synced INTEGER DEFAULT 0,
            foreign key(invent_id) references products(invent_id) on delete cascade
               );
''')

cursor.execute('''
    Create TABLE IF NOT EXISTS details(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight TEXT,
            production_date TEXT,
            brand TEXT,
            production_place TEXT,
            product_state TEXT,
            more_details TEXT,
            invent_id INTEGER,
            keep_place TEXT
               );
''')