import sqlite3

conn = sqlite3.connect('app.db')  # replace with your actual DB file name if different
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(chat_message);")
columns = cursor.fetchall()

print("Columns in chat_message table:")
for col in columns:
    print(col)

conn.close()
