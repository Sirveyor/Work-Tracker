import sqlite3

def create_connection():
    conn = sqlite3.connect('work_tracker.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_entries (
            project_number TEXT NOT NULL,
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
