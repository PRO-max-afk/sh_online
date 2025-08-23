import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("update products set is_synced=0 where name= 'روغن' ")
conn.commit()