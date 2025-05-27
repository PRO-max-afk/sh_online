import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
CREATE TRIGGER after_sale_insert
AFTER INSERT ON sale_factor
-- این خط شرط را مشخص می‌کند:
WHEN (SELECT quantity FROM products WHERE barcode = NEW.barcode) >= NEW.quantity
BEGIN
  UPDATE products
  SET quantity = quantity - NEW.quantity
  WHERE barcode = NEW.barcode;
END;

''')
conn.commit()