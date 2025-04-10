from twilio.rest import Client
import random

# دیتابیس فرضی
users = {
    "user1": {"phone": "+93770111222", "password": "1234"}
}

# تنظیمات Twilio (مشخصات خودتان را وارد کنید)
account_sid = 'ACxxxxxxxxxxxxxxxxxxxx'
auth_token = 'your_auth_token'
twilio_number = '+93791336750'

client = Client(account_sid, auth_token)

# ارسال کد
def send_otp(phone_number):
    code = str(random.randint(1000, 9999))
    client.messages.create(
        body=f"کد تایید شما: {code}",
        from_=twilio_number,
        to=phone_number
    )
    return code
