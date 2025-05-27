import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table sale_factor add column total REAL NOT NULL ;")
conn.commit()
conn.close()