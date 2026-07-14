import os
import sqlite3
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_tracker.db')

def create_connection():
    """
    Creates a connection to the SQLite database specified by the database file name.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    """
    Creates a table named 'work_entries' in the SQLite database if it does not already exist.

    The table includes the following columns:
        - project_number (TEXT): The project number associated with the work entry.
        - id (INTEGER): A unique identifier for each work entry, automatically incremented.
        - person (TEXT): The name of the person associated with the work entry.
        - start_time (TEXT): The start time of the work entry.
        - end_time (TEXT): The end time of the work entry.
        - description (TEXT): A description of the work entry.

    This function establishes a connection to the database, executes the SQL command to create
    the table, commits the transaction, and then closes the connection.
    """
    with closing(create_connection()) as conn:
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
