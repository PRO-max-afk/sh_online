import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
CREATE TRIGGER IF NOT EXISTS after_sale_insert
AFTER INSERT ON sale_factor

BEGIN
  UPDATE products
  SET quantity = quantity - NEW.quantity
  WHERE barcode = NEW.barcode;
END;

''')
cursor.execute('''
CREATE TRIGGER trg_update_big_sub
AFTER UPDATE ON products
FOR EACH ROW
WHEN OLD.quantity > 0 AND NEW.big_quantity > 0
BEGIN
    UPDATE products
    SET big_sub = ROUND(OLD.quantity / NEW.big_quantity, 1)
    WHERE invent_id = NEW.invent_id;
END;



''')
cursor.execute('''
CREATE TRIGGER trg_update_quantity
AFTER UPDATE ON products
FOR EACH ROW
WHEN OLD.quantity > 0 AND NEW.big_quantity > 0 AND NEW.big_sub > 0
BEGIN
    UPDATE products
    SET quantity = OLD.quantity - (NEW.big_quantity * NEW.big_sub)
    WHERE invent_id = NEW.invent_id;
END;



''')
conn.commit()