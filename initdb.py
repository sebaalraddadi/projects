import sqlite3

conn = sqlite3.connect('tasks.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        date TEXT NOT NULL,
        attachment TEXT
    )
''')

conn.commit()
conn.close()

print("✔️ تم إنشاء قاعدة البيانات والجدول بنجاح.")