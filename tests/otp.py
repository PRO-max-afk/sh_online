import tkinter as tk
from tkinter import messagebox
import random

# دیتابیس فرضی کاربران
users = {
    "09370000000": {"password": "oldpass"}
}

otp_code = ""  # برای ذخیره کد OTP

# مرحله ۱: ارسال OTP
def send_otp():
    global otp_code
    phone = entry_phone.get()

    if phone in users:
        otp_code = str(random.randint(1000, 9999))
        lbl_otp_display.config(text=f"(کد برای تست: {otp_code})")  # شبیه‌سازی ارسال OTP
        messagebox.showinfo("OTP ارسال شد", "کد تأیید ارسال شد. لطفاً وارد کنید.")
        show_otp_section()
    else:
        messagebox.showerror("خطا", "شماره یافت نشد!")

# مرحله ۲: بررسی OTP و تغییر رمز
def verify_and_reset():
    entered_code = entry_otp.get()
    new_pass = entry_new_pass.get()
    phone = entry_phone.get()

    if entered_code == otp_code:
        users[phone]["password"] = new_pass
        messagebox.showinfo("موفقیت", "رمز عبور با موفقیت تغییر کرد!")
        window.destroy()
    else:
        messagebox.showerror("خطا", "کد OTP اشتباه است!")

# رابط گرافیکی
window = tk.Tk()
window.title("بازیابی رمز عبور با OTP")
window.geometry("300x400")

# فریم ورودی شماره
tk.Label(window, text="شماره تلفن خود را وارد کنید:").pack(pady=10)
entry_phone = tk.Entry(window)
entry_phone.pack()

tk.Button(window, text="ارسال OTP", command=send_otp).pack(pady=10)

lbl_otp_display = tk.Label(window, text="", fg="gray")
lbl_otp_display.pack()

# فریم وارد کردن کد و رمز جدید
otp_frame = tk.Frame(window)

tk.Label(otp_frame, text="کد ارسال‌شده را وارد کنید:").pack(pady=5)
entry_otp = tk.Entry(otp_frame)
entry_otp.pack()

tk.Label(otp_frame, text="رمز عبور جدید را وارد کنید:").pack(pady=5)
entry_new_pass = tk.Entry(otp_frame, show="*")
entry_new_pass.pack()

tk.Button(otp_frame, text="تغییر رمز عبور", command=verify_and_reset).pack(pady=10)

def show_otp_section():
    otp_frame.pack(pady=20)

window.mainloop()
