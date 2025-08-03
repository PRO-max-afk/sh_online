import sqlite3


conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()


cursor.execute('''
SELECT buy_date, final_total FROM products WHERE user_id = 1

''')
rows = cursor.fetchall()
for row in rows:
    print(row)