from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime, timezone
import jdatetime

class NTPThread(QThread):
    finished = pyqtSignal(jdatetime.date)

    def run(self):
        try:
            import ntplib
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3, timeout=5)
            utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            jalali_date = jdatetime.datetime.fromgregorian(datetime=utc_time).date()
        except Exception as e:
            print("⚠ خطا در دریافت تاریخ از NTP:", e)
            local_time = datetime.now()
            jalali_date = jdatetime.datetime.fromgregorian(datetime=local_time).date()
        
        self.finished.emit(jalali_date)
