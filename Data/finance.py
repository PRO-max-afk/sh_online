import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS harvest(
               h_id INTEGER primary key AUTOINCREMENT,
               name TEXT NOT NULL,
               amount REAL NOT NULL,
               date TEXT NOT NULL,
               description TEXT,
               user_id INTEGER,
               is_synced INTEGER DEFAULT 0
               );
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS  barrow(
               b_id INTEGER primary key AUTOINCREMENT,
               name TEXT NOT NULL,
               amount REAL NOT NULL,
               date TEXT NOT NULL,
               type TEXT NOT NULL,
               description TEXT,
               user_id INTEGER,
               is_synced INTEGER DEFAULT 0
               );
    ''')