import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table customers add column is_synced INTEGER default 0")
conn.commit()
conn.close()