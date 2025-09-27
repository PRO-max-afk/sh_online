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
            profit real default 0,
            product_type TEXT,
            sale_type TEXT,
            discount REAL DEFAULT 0,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            choise_type TEXT,
            created_at TEXT,
            updated_at TEXT,
            sync INTEGER,
            is_synced INTEGER DEFAULT 0,
            cus_id INTEGER,
            foreign key(cus_id) references customers(id) ON DELETE set null
            
               );
''')

cursor.execute('''
Create TABLE IF NOT EXISTS factor_number(
            sale_id INTEGER );
''')

cursor.execute('''
Create TABLE IF NOT EXISTS sale_number(
            sale_id INTEGER );
''')

cursor.execute('''
Create TABLE IF NOT EXISTS order_number(
            order_id INTEGER );
''')

cursor.execute('''
Create TABLE IF NOT EXISTS logo(
            image text,
            store_name text );
''')

cursor.execute('''
Create TABLE IF NOT EXISTS printer(
            address Text,
            phone Text );
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    home_number TEXT NOT NULL,
    area TEXT NOT NULL,
    phone TEXT NOT NULL,
    invent_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    profit REAL,
    sale_number INTEGER NOT NULL,
    product_unit TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    approve INTEGER NOT NULL DEFAULT 0,
    denied INTEGER NOT NULL DEFAULT 0,
    message TEXT NOT NULL DEFAULT 'جنس که سفارش داده اید به زودی به دسترس شما قرار خواهد گرفت<',
    created_at TEXT DEFAULT NULL,
    updated_at TEXT DEFAULT NULL,
    customer_name TEXT NOT NULL,
    FOREIGN KEY (invent_id) REFERENCES products(invent_id) ON DELETE CASCADE
);

''')

