import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table products add column is_deleted INTEGER DEFAULT 0;")
conn.commit()
conn.close()