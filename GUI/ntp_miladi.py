from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime, timezone

class GregorianNTPThread(QThread):
    finished = pyqtSignal(datetime)

    def run(self):
        try:
            import ntplib
            client = ntplib.NTPClient()
            # تست چند سرور مختلف برای افزایش احتمال موفقیت
            servers = ["pool.ntp.org", "time.google.com", "time.windows.com"]
            for server in servers:
                try:
                    response = client.request(server, version=3, timeout=5)
                    utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc).astimezone()
                    self.finished.emit(utc_time)
                    return
                except Exception as inner_e:
                    print(f"⚠ Failed to get time from {server}: {inner_e}")
            raise Exception("All NTP servers failed")
        except Exception as e:
            print("⚠ Error fetching time from NTP:", e)
            utc_time = datetime.now().astimezone()
            self.finished.emit(utc_time)
