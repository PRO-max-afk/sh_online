import sqlite3

conn= sqlite3.connect('D:\\projects\\sh_online\\Data\\sh_online.db')
cursor= conn.cursor()

cursor.execute('''
CREATE TRIGGER IF NOT EXISTS after_sale_insert
AFTER INSERT ON sale_factor
BEGIN
  -- کم کردن تعداد محصول و total
  UPDATE products
  SET quantity = quantity - NEW.quantity,
      total    = total - NEW.total
  WHERE barcode = NEW.barcode;

  -- محاسبه big_sub با توجه به big_quantity در products
  UPDATE products
  SET big_sub = NEW.quantity  / big_quantity
  WHERE barcode = NEW.barcode
    AND big_quantity > 0
    AND NEW.quantity > 0;
               
 -- به‌روزرسانی big_sub_display = ترکیب big_sub + big_category
  UPDATE products
  SET big_sub_display = CAST(big_sub AS TEXT) || ' ' || big_category
  WHERE barcode = NEW.barcode;
END;    

''')
cursor.execute('''
CREATE TRIGGER IF NOT EXISTS trg_update_big_sub
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
CREATE TRIGGER IF NOT EXISTS trg_update_quantity
BEFORE UPDATE ON products
FOR EACH ROW
WHEN OLD.quantity > 0 AND NEW.big_quantity > 0 AND NEW.big_sub > 0
BEGIN
    SELECT NEW.quantity = OLD.quantity - (NEW.big_quantity * NEW.big_sub);
END;

''')


cursor.execute('''
CREATE TRIGGER IF NOT EXISTS after_insert_products
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO products_log (
        name, category, sub_category, sale_unit,buy_date,
        buy_price, sale_price, quantity, big_category, big_sub, big_quantity,
        barcode, image_path, final_total,update_at,is_synced
    )
    VALUES (
        NEW.name, NEW.category, NEW.sub_category, NEW.sale_unit, NEW.buy_date,
        NEW.buy_price, NEW.sale_price, NEW.quantity, NEW.big_category, NEW.big_sub, NEW.big_quantity,
        NEW.barcode, NEW.image_path, NEW.final_total,datetime('now'), 0
    );
END;

''')
cursor.execute('''
CREATE TRIGGER IF NOT EXISTS after_update_products
AFTER UPDATE ON products
FOR EACH ROW
WHEN 
    (NEW.new_quantity <> OLD.new_quantity OR NEW.new_sub <> OLD.new_sub)
BEGIN
    INSERT INTO products_log (
        name, category, sub_category, sale_unit,buy_date,
        buy_price, sale_price, quantity, big_category, big_sub, big_quantity,
        barcode, image_path, final_total, update_at, is_synced
    )
    VALUES (
        NEW.name, NEW.category, NEW.sub_category, NEW.sale_unit,NEW.buy_date,
        NEW.buy_price, NEW.sale_price, NEW.new_quantity, NEW.big_category, NEW.new_sub, NEW.big_quantity,
        NEW.barcode, NEW.image_path, NEW.final_total, datetime('now'), 0
    );
END;

''')


conn.commit()