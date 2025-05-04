import sys
import ctypes
from ctypes import c_char_p, c_int, c_void_p, byref
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from mes.message_ui import CustomMessageBox

class FingerprintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZKTeco 9500 - اسکن اثر انگشت")
        self.setGeometry(300, 200, 400, 200)
        self.zkfp = None  # برای نگهداری DLL
        self.devHandle = None  # هندل دستگاه

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("برای شروع، روی دکمه زیر کلیک کنید")
        self.scan_btn = QPushButton("شروع اسکن اثر انگشت")
        self.scan_btn.clicked.connect(self.start_scan)

        layout.addWidget(self.status_label)
        layout.addWidget(self.scan_btn)

        self.setLayout(layout)

    def start_scan(self):
        try:
            self.zkfp = ctypes.cdll.LoadLibrary("D:\\projects\\sh_online\\tests\\zkfputil.dll")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"لود کردن DLL شکست خورد:\n{str(e)}")
            return

        # مقداردهی اولیه به دستگاه
        init_result = self.zkfp.ZKFPM_Init()
        if init_result != 0:
            QMessageBox.critical(self, "خطا", f"خطا در مقداردهی اولیه: {init_result}")
            return

        # باز کردن اولین دستگاه متصل
        self.devHandle = self.zkfp.ZKFPM_OpenDevice(0)
        if not self.devHandle:
            QMessageBox.critical(self, "خطا", "اتصال به دستگاه شکست خورد")
            return

        # گرفتن نسخه SDK
        self.zkfp.ZKFPM_GetVersion.restype = c_char_p
        version = self.zkfp.ZKFPM_GetVersion()
        version_text = version.decode("utf-8")

        self.status_label.setText(f"دستگاه متصل شد ✅\nنسخه SDK: {version_text}")

    def closeEvent(self, event):
        if self.zkfp and self.devHandle:
            self.zkfp.ZKFPM_CloseDevice(self.devHandle)
            self.zkfp.ZKFPM_Terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintApp()
    window.show()
    sys.exit(app.exec())
