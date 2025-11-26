import mysql.connector
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

conn = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM BOOK;")
print("Books:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM AUTHORS;")
print("Authors:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM BOOK_AUTHORS;")
print("Book ⇄ Author Links:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM BORROWER;")
print("Borrowers:", cursor.fetchone()[0])
