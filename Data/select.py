import sqlite3


conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
SELECT image_path
FROM products

''')
rows = cursor.fetchall()
for row in rows:
    print(row)