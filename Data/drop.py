import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("delete from sale_factor")
conn.commit()