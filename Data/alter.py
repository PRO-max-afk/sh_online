import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table product_details add column keep_place TEXT")
conn.commit()
conn.close()