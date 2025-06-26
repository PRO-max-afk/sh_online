# app_signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    logo_updated = pyqtSignal()

# این شی را برای استفاده عمومی ایجاد می‌کنیم
global_signals = AppSignals()
