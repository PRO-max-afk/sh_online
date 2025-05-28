import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table sale_factor add column factor_number INTEGER ;")
conn.commit()
conn.close()