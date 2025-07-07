import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

try:
    #print(os.path.exists("tests\\aryaict.crt"))
    r = requests.get("https://aryaict.com/connects.php", headers=headers, verify="tests\\aryaict.crt",timeout=20)
    print("پاسخ:", r.status_code)
    print("محتوا:", r.text)
except Exception as e:
    print("❌ خطا:", e)
