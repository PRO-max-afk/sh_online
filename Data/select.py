import sqlite3


conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
SELECT product_name FROM sale_factor WHERE factor_number = 109

''')
rows = cursor.fetchall()
for row in rows:
    print(row)