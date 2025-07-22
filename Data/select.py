import sqlite3


conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
SELECT *
FROM products
WHERE is_synced=0;

''')
rows = cursor.fetchall()
for row in rows:
    print(row)