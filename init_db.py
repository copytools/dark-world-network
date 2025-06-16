import sqlite3

conn = sqlite3.connect('files.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS files')

c.execute('''
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    description TEXT,
    filename TEXT,
    downloads INTEGER
)
''')

conn.commit()
conn.close()

print("✅ Database initialized successfully.")