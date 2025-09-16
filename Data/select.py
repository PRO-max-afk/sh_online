import sqlite3


conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
select * from customers where is_synced=0

''')
rows = cursor.fetchall()
for row in rows:
    print(row)