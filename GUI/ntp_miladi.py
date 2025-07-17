# ntp_thread_gregorian.py
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime, timezone

class GregorianNTPThread(QThread):
    finished = pyqtSignal(datetime)

    def run(self):
        try:
            import ntplib
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3, timeout=5)
            utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc).astimezone()
        except Exception as e:
            print("⚠ Error fetching time from NTP:", e)
            utc_time = datetime.now().astimezone()
        self.finished.emit(utc_time)
