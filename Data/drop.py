import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("drop table sale_factor")
conn.commit()
#DROP TRIGGER IF EXISTS trg_update_big_sub;
#DROP TRIGGER IF EXISTS trg_update_quantity;
#DROP TRIGGER IF EXISTS update_big_sub_on_quantity;

