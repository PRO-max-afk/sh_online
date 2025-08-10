# globals.py
# وضعیت هشدارهای نمایش داده‌شده به صورت مجموعه
shown_notifications = set()

# اگر خواستی هشدارها فقط یکبار در روز نمایش داده شوند، می‌توانی تاریخ آخرین پاک‌سازی را نیز ذخیره کنی:
import datetime
last_cleared_date = None

def reset_notifications_daily():
    """
    اگر روز جدیدی شروع شده باشد، هشدارهای نمایش‌داده‌شده را پاک می‌کند.
    """
    global last_cleared_date
    today = datetime.date.today()
    if last_cleared_date != today:
        shown_notifications.clear()
        last_cleared_date = today
