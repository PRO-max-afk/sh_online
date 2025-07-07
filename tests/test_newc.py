import pymysql

connection = pymysql.connect(
    host="50.6.154.40",       # یا آی‌پی سرور
    user="ihrblgmy_shop_login",    # توجه کن باید کامل باشه
    password="jm=BNOpE)^;_",
    database="ihrblgmy_shop"
)

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM mobile_user LIMIT 5")
    results = cursor.fetchall()
    for row in results:
        print(row)

connection.close()
