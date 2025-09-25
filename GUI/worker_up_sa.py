import sqlite3
from PyQt6.QtCore import QThread
import os
import jdatetime  # pip install jdatetime

class Salary_worker(QThread):
    def __init__(self, db_path=None):
        super().__init__()
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            self.db_path = os.path.join(root_dir, "Data", "sh_online.db")
        else:
            self.db_path = db_path

    def run(self):
        if not os.path.exists(self.db_path):
            print("⚠ Database not found!")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # امروز شمسی
            today_j = jdatetime.date.today()

            # دریافت همه کارمندان و حقوق فعلی
            cursor.execute("SELECT employee_id, salary FROM employees")
            employees = cursor.fetchall()

            for emp_id, current_salary in employees:
                # آخرین پرداخت از جدول salaries
                cursor.execute("""
                    SELECT pay_date, amount FROM salaries 
                    WHERE employee_id=? 
                    ORDER BY pay_date DESC LIMIT 1
                """, (emp_id,))
                last_pay = cursor.fetchone()

                if last_pay:
                    last_pay_date_str, last_amount = last_pay
                    # تبدیل رشته yyyy/mm/dd به jdatetime.date
                    year, month, day = map(int, last_pay_date_str.split("/"))
                    last_pay_date = jdatetime.date(year, month, day)
                else:
                    # اگر پرداختی نبود، فرض: تاریخ استخدام
                    cursor.execute("SELECT hire_date FROM employees WHERE employee_id=?", (emp_id,))
                    hire_date_str = cursor.fetchone()[0]
                    year, month, day = map(int, hire_date_str.split("/"))
                    last_pay_date = jdatetime.date(year, month, day)

                # بررسی اینکه آیا یک ماه گذشته (حدود 30 روز)
                delta_days = (today_j.togregorian() - last_pay_date.togregorian()).days
                if delta_days >= 30:
                    # آپدیت حقوق کارمند
                    # می‌توانید اینجا محاسبه دلخواه داشته باشید، مثلا افزایش حقوق ماهانه
                    new_salary = current_salary  # یا current_salary + X
                    cursor.execute("UPDATE employees SET salary=? WHERE employee_id=?", (new_salary, emp_id))
                    print(f"حقوق کارمند {emp_id} بروزرسانی شد: {new_salary}")

            conn.commit()

        except sqlite3.Error as e:
            print(f"DB error: {e}")

        finally:
            conn.close()
