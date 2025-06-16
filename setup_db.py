import sqlite3

conn = sqlite3.connect('files.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    description TEXT,
    filename TEXT,
    downloads INTEGER DEFAULT 0
)
''')
conn.commit()
conn.close()
print("Database initialized.")