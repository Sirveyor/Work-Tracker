import sqlite3
from database import create_connection

class WorkEntry:
    def __init__(self, project_number, person, start_time, end_time, description):
        self.project_number = project_number
        self.person = person
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

class WorkTracker:
    def __init__(self):
        self.create_table()

    def create_table(self):
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

    def add_entry(self, project_number, person, start_time, end_time, description):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO work_entries (project_number, person, start_time, end_time, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_number, person, start_time, end_time, description))
        conn.commit()
        conn.close()

    def get_entries(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM work_entries')
        rows = cursor.fetchall()
        conn.close()
        return [WorkEntry(row[0], row[2], row[3], row[4], row[5]) for row in rows]

    def get_last_entry(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM work_entries ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return [WorkEntry(row[0], row[2], row[3], row[4], row[5]) if row else None]


    def print_current_entry_time_spent(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
                FROM work_entries ORDER BY id DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                print(f"Current entry time spent: {row[0]:.2f} hours")
            else:
                print("No current entry")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
     

    def get_total_time_spent(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT project_number, SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
            FROM work_entries
            GROUP BY project_number
        ''')
        results = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}
