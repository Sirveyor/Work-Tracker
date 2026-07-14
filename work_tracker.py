import functools
import sqlite3
from contextlib import closing
from datetime import datetime, date, timedelta
from database import create_connection, create_table


def db_operation(default=None):
    """Decorator that catches sqlite3 errors raised by a WorkTracker method,
    prints a user-facing message, and returns `default` instead of letting
    the error crash the application.

    Args:
        default: The value to return if a database error occurs.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sqlite3.Error as e:
                print(f"Database error in {func.__name__}: {e}")
                return default
        return wrapper
    return decorator

class WorkEntry:
    """
    Represents a work entry for a specific project.

    Attributes:
        id (int): The row identifier for the work entry.
        project_number (str): The identifier for the project.
        person (str): The name of the person who worked on the project.
        start_time (str): The start time of the work entry.
        end_time (str): The end time of the work entry.
        description (str): A brief description of the work performed.
    """

    def __init__(self, entry_id, project_number, person, start_time, end_time, description):
        """
        Initializes a new instance of the WorkEntry class.

        Args:
            entry_id (int): The row identifier for the work entry.
            project_number (str): The identifier for the project.
            person (str): The name of the person who worked on the project.
            start_time (str): The start time of the work entry.
            end_time (str): The end time of the work entry.
            description (str): A brief description of the work performed.
        """
        self.id = entry_id
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
        try:
            create_table()
        except sqlite3.Error as e:
            print(f"Fatal: could not initialize the database: {e}")
            raise SystemExit(1)

    @db_operation(default=False)
    def add_entry(self, project_number, person, start_time, end_time, description):
        """
        Adds a new work entry to the work_entries table.

        Args:
            project_number (str): The identifier for the project.
            person (str): The name of the person who worked on the project.
            start_time (str): The start time of the work entry.
            end_time (str): The end time of the work entry.
            description (str): A brief description of the work performed.

        Returns:
            bool: True if the entry was added, False if a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO work_entries (project_number, person, start_time, end_time, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_number, person, start_time, end_time, description))
            conn.commit()
            return True

    @db_operation(default=[])
    def get_all_entries(self):
        """
        Retrieves all work entries from the work_entries table.

        Returns:
            list: A list of WorkEntry objects representing all work entries,
                or an empty list if a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM work_entries')
            rows = cursor.fetchall()
            return [WorkEntry(row[1], row[0], row[2], row[3], row[4], row[5]) for row in rows]

    @db_operation(default=None)
    def get_last_entry(self):
        """
        Retrieves the most recent work entry from the work_entries table.

        Returns:
            WorkEntry: The most recent work entry, or None if no entries exist
                or a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM work_entries ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            return WorkEntry(row[1], row[0], row[2], row[3], row[4], row[5]) if row else None

    @db_operation(default=None)
    def get_entry_by_id(self, entry_id):
        """
        Retrieves a single work entry by its row id.

        Args:
            entry_id (int): The id of the work entry to retrieve.

        Returns:
            WorkEntry: The matching work entry, or None if no entry has that id
                or a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM work_entries WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            return WorkEntry(row[1], row[0], row[2], row[3], row[4], row[5]) if row else None

    @db_operation(default=False)
    def update_entry(self, entry_id, project_number, person, start_time, end_time, description):
        """
        Updates an existing work entry.

        Args:
            entry_id (int): The id of the work entry to update.
            project_number (str): The identifier for the project.
            person (str): The name of the person who worked on the project.
            start_time (str): The start time of the work entry.
            end_time (str): The end time of the work entry.
            description (str): A brief description of the work performed.

        Returns:
            bool: True if an entry was updated, False if no entry had that id
                or a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE work_entries
                SET project_number = ?, person = ?, start_time = ?, end_time = ?, description = ?
                WHERE id = ?
            ''', (project_number, person, start_time, end_time, description, entry_id))
            conn.commit()
            return cursor.rowcount > 0

    @db_operation(default=False)
    def delete_entry(self, entry_id):
        """
        Deletes a work entry by its row id.

        Args:
            entry_id (int): The id of the work entry to delete.

        Returns:
            bool: True if an entry was deleted, False if no entry had that id
                or a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM work_entries WHERE id = ?', (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    @db_operation(default=None)
    def print_current_entry_time_spent(self):
        """
        Prints the time spent on the most recent work entry in hours.
        If no entries exist, prints a message indicating no current entry.
        """
        with closing(create_connection()) as conn:
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

    @db_operation(default={})
    def get_total_time_spent(self):
        """
        Calculates the total time spent on each project.

        Returns:
            dict: A dictionary where keys are project numbers and values are total hours
                spent, or an empty dict if a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT project_number, SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
                FROM work_entries
                GROUP BY project_number
            ''')
            results = cursor.fetchall()
            return {row[0]: row[1] for row in results}

    @db_operation(default=[])
    def filter_entries_by_date_range(self, start_date=None, end_date=None, project_number=None):
        """
        Retrieves work entries filtered by date range and optionally by project number.

        Args:
            start_date (str, optional): Start date in 'YYYY-MM-DD' format. If None, no lower bound.
            end_date (str, optional): End date in 'YYYY-MM-DD' format. If None, no upper bound.
            project_number (str, optional): Specific project number to filter by.

        Returns:
            list: A list of WorkEntry objects matching the filter criteria, or an empty
                list if a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()

            # Build the SQL query dynamically based on provided filters
            query = 'SELECT * FROM work_entries WHERE 1=1'
            params = []

            if start_date:
                query += ' AND date(start_time) >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date(start_time) <= ?'
                params.append(end_date)

            if project_number:
                query += ' AND project_number = ?'
                params.append(project_number)

            query += ' ORDER BY start_time'

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [WorkEntry(row[1], row[0], row[2], row[3], row[4], row[5]) for row in rows]

    def filter_entries_by_today(self, project_number=None):
        """
        Retrieves work entries for today.

        Args:
            project_number (str, optional): Specific project number to filter by.

        Returns:
            list: A list of WorkEntry objects for today.
        """
        today = date.today().strftime('%Y-%m-%d')
        return self.filter_entries_by_date_range(start_date=today, end_date=today, project_number=project_number)

    def filter_entries_by_this_week(self, project_number=None):
        """
        Retrieves work entries for the current week (Monday to Sunday).

        Args:
            project_number (str, optional): Specific project number to filter by.

        Returns:
            list: A list of WorkEntry objects for this week.
        """
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        return self.filter_entries_by_date_range(
            start_date=monday.strftime('%Y-%m-%d'),
            end_date=sunday.strftime('%Y-%m-%d'),
            project_number=project_number
        )

    @db_operation(default={})
    def get_total_time_by_date_range(self, start_date=None, end_date=None, project_number=None):
        """
        Calculates total time spent within a date range, optionally filtered by project.

        Args:
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            end_date (str, optional): End date in 'YYYY-MM-DD' format.
            project_number (str, optional): Specific project number to filter by.

        Returns:
            dict: A dictionary where keys are project numbers and values are total hours
                spent, or an empty dict if a database error occurred.
        """
        with closing(create_connection()) as conn:
            cursor = conn.cursor()

            query = '''
                SELECT project_number, SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
                FROM work_entries WHERE 1=1
            '''
            params = []

            if start_date:
                query += ' AND date(start_time) >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date(start_time) <= ?'
                params.append(end_date)

            if project_number:
                query += ' AND project_number = ?'
                params.append(project_number)

            query += ' GROUP BY project_number'

            cursor.execute(query, params)
            results = cursor.fetchall()

            return {row[0]: row[1] for row in results}
