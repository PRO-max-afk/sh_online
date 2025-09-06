import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute("alter table product_details add foriegn key(pro_id) references products(invent_id) on delete cascade;")
conn.commit()
conn.close()