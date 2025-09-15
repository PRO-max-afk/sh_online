import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            last_name TEXT,
            phone TEXT not null,
            email TEXT,
            register_date TEXT,
            user_id INTEGER
             
               );
''')

cursor.execute('''
CREATE TABLE  IF NOT EXISTS employees (
    employee_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    phone        TEXT UNIQUE,
    email        TEXT UNIQUE,
    address      TEXT,
    city         TEXT,
    position     TEXT NOT NULL,
    salary       REAL DEFAULT 0.0,
    hire_date    TEXT DEFAULT (datetime('now','localtime')),
    status       TEXT DEFAULT 'active',
    picture TEXT
);

''')