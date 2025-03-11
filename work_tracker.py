import sqlite3
from database import create_connection, create_table

class WorkEntry:
    """
    Represents a work entry for a specific project.

    Attributes:
        project_number (str): The identifier for the project.
        person (str): The name of the person who worked on the project.
        start_time (datetime): The start time of the work entry.
        end_time (datetime): The end time of the work entry.
        description (str): A brief description of the work performed.
    """

    def __init__(self, project_number, person, start_time, end_time, description):
        """
        Initializes a new instance of the WorkEntry class.

        Args:
            project_number (str): The identifier for the project.
            person (str): The name of the person who worked on the project.
            start_time (datetime): The start time of the work entry.
            end_time (datetime): The end time of the work entry.
            description (str): A brief description of the work performed.
        """
        self.project_number = project_number
        self.person = person
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

class WorkTracker:
    """
    A class to track work entries for various projects.

    Methods:
        create_table(): Creates the work_entries table if it does not exist.
        add_entry(project_number, person, start_time, end_time, description): Adds a new work
            entry to the database.
        get_entries(): Retrieves all work entries from the database.
        get_last_entry(): Retrieves the most recent work entry from the database.
        print_current_entry_time_spent(): Prints the time spent on the most recent work entry.
        get_total_time_spent(): Calculates the total time spent on each project.
    """

    def __init__(self):
        """Initializes the WorkTracker and creates the work_entries table."""
        #Done ! TODO: Use the create_table method from the database module
        create_table()

    
    def add_entry(self, project_number, person, start_time, end_time, description):
        """
        Adds a new work entry to the work_entries table.

        Args:
            project_number (str): The identifier for the project.
            person (str): The name of the person who worked on the project.
            start_time (str): The start time of the work entry.
            end_time (str): The end time of the work entry.
            description (str): A brief description of the work performed.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO work_entries (project_number, person, start_time, end_time, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_number, person, start_time, end_time, description))
        conn.commit()
        conn.close()

    def get_entries(self):
        """
        Retrieves all work entries from the work_entries table.

        Returns:
            list: A list of WorkEntry objects representing all work entries.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM work_entries')
        rows = cursor.fetchall()
        conn.close()
        #TODO: Use a work entry object to represent each row
        return [WorkEntry(row[0], row[2], row[3], row[4], row[5]) for row in rows]

    def get_last_entry(self):
        """
        Retrieves the most recent work entry from the work_entries table.

        Returns:
            WorkEntry: The most recent work entry, or None if no entries exist.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM work_entries ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return [WorkEntry(row[0], row[2], row[3], row[4], row[5]) if row else None]

    def print_current_entry_time_spent(self):
        """
        Prints the time spent on the most recent work entry in hours.
        If no entries exist, prints a message indicating no current entry.
        """
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT project_number, julianday(end_time), julianday(start_time)
                FROM work_entries ORDER BY id DESC LIMIT 1''')
            row = cursor.fetchone()
            if row:
                current_time = (row[1] - row[2]) * 24
                print(f"Time spent on Job {row[0]}: {current_time:.2f} hours")
            else:
                print("No current entry")
        except sqlite3.DatabaseError as db_err:
            print(f"Database error occurred: {db_err}")
        except sqlite3.OperationalError as op_err:
            print(f"Operational error occurred: {op_err}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()

    def get_total_time_spent(self):
        """
        Calculates the total time spent on each project.

        Returns:
            dict: A dictionary where keys are project numbers and values are total hours spent.
        """
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
