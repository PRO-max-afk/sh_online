import sqlite3
import csv

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

file_path= "Data\\fixeds (2).csv"
with open (file_path, newline='', encoding='utf-8') as csvfile:
    reader= csv.reader(csvfile)

    for row in reader:
        cursor.execute('''
            INSERT INTO fixeds( barcode, product_name, categorie, sub_categorie, product_image,
            weight, production_date, brand, production_place, product_state,
            more_detail, keep_place, big_price, buy_price, sell_price,
            big_category, sale_unit, big_quantity, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?)
            ''',(row))

conn.commit()
conn.close()