import ntplib
from datetime import datetime, timezone
import jdatetime
import pytz  # نیاز به نصب دارد: pip install pytz

def get_jalali_time_from_ntp(server="pool.ntp.org"):
    try:
        # گرفتن زمان UTC از سرور NTP
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)

        # تنظیم منطقه زمانی هرات (Asia/Kabul)
        herat_tz = pytz.timezone("Asia/Kabul")
        local_time = utc_time.astimezone(herat_tz)

        # تبدیل زمان محلی به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=local_time)
        
        return jalali_date.strftime("%Y/%m/%d - %H:%M:%S")
    
    except Exception as e:
        return f"خطا در دریافت زمان: {e}"

# نمایش تاریخ شمسی
print("تاریخ جلالی از سرور NTP:")
print(get_jalali_time_from_ntp())
