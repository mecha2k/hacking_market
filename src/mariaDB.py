import pymysql
import os

from dotenv import load_dotenv


load_dotenv(verbose=True)
db_name = os.getenv("MARIADB_NAME")
db_port = int(os.getenv("MARIADB_PORT"))
db_passwd = os.getenv("MARIADB_PASSWD")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password=db_passwd,
    db=db_name,
    port=db_port,
    charset="utf8",
)

cursor = conn.cursor()
cursor.execute("select version();")
result = cursor.fetchone()

print(f"MariaDB version : {result}")

conn.close()
