import csv
import os
import json
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from work_tracker import WorkTracker

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_tracker.log')
DATA_DIR = 'data'
LAST_USED_PATH = os.path.join(DATA_DIR, 'last_used.json')
LEGACY_LAST_PERSON_PATH = os.path.join(DATA_DIR, 'last_person.json')


def load_last_used():
    """
    Loads the last-used person and project number from the 'data' directory,
    creating the directory if it doesn't exist.

    Falls back to the older last_person.json (used before project number was
    also remembered) if last_used.json doesn't exist yet, so an existing
    preference isn't silently lost on upgrade.

    Returns:
        dict: A dict with 'last_person' and 'last_project' keys, each defaulting
            to an empty string if not found.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(LAST_USED_PATH):
        with open(LAST_USED_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(LEGACY_LAST_PERSON_PATH):
        with open(LEGACY_LAST_PERSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    return {
        'last_person': data.get('last_person', ''),
        'last_project': data.get('last_project', ''),
    }


def save_last_used(person, project_number):
    """
    Saves the last-used person and project number to the 'data' directory,
    creating the directory if it doesn't exist.

    Args:
        person (str): The name of the person to remember.
        project_number (str): The project number to remember.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(LAST_USED_PATH, 'w', encoding='utf-8') as f:
        json.dump({'last_person': person, 'last_project': project_number}, f)


def parse_duration(text):
    """Parses a '+<duration>' shorthand like '+2h', '+90m', or '+1h30m'.

    Args:
        text (str): Candidate text, expected to start with '+'.

    Returns:
        timedelta: The parsed duration, or None if text isn't a valid
            duration shorthand (must start with '+' and specify at least
            hours or minutes).
    """
    if not text.startswith('+'):
        return None
    match = re.fullmatch(r'\+(?:(\d+)h)?(?:(\d+)m)?', text, re.IGNORECASE)
    if not match or not any(match.groups()):
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return timedelta(hours=hours, minutes=minutes)


def parse_flexible_time(value, anchor_date):
    """Parses a time value that may be a full 'YYYY-MM-DD HH:MM' or a
    time-only 'HH:MM' anchored to a given date.

    Args:
        value (str): The user-entered value.
        anchor_date (str): 'YYYY-MM-DD' to combine with an HH:MM-only value.

    Returns:
        str: A normalized 'YYYY-MM-DD HH:MM' string, or None if value matches
            neither format.
    """
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M')
        return value
    except ValueError:
        pass
    try:
        datetime.strptime(value, '%H:%M')
        return f"{anchor_date} {value}"
    except ValueError:
        return None


def get_valid_start_time():
    """Prompts the user for a start time and validates the input. Accepts a
    full 'YYYY-MM-DD HH:MM', a time-only 'HH:MM' anchored to today, blank for
    now, or 'q' to quit.

    Returns:
      str: A valid start time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts or the
           user quits.
    """
    max_attempts = 3
    attempts = 0
    today = datetime.now().strftime('%Y-%m-%d')

    while attempts < max_attempts:
        value = input("Enter start time (YYYY-MM-DD HH:MM, HH:MM for today, "
                       "or <Enter> for now), 'q' to quit: ").strip()

        if value == '':
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        if value.lower() == 'q':
            return None

        parsed = parse_flexible_time(value, today)
        if parsed:
            return parsed

        attempts += 1
        print("Invalid date or time format. Please use YYYY-MM-DD HH:MM or HH:MM. "
              f"{max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return None


def get_valid_end_time(start_time):
    """Prompts the user for an end time and validates the input. Accepts a
    full 'YYYY-MM-DD HH:MM', a time-only 'HH:MM' anchored to start_time's
    date, a '+<duration>' shorthand like '+2h' or '+90m' relative to
    start_time, blank for now, or 'q' to quit.

    Args:
        start_time (str): The already-collected start time, used to anchor
            HH:MM-only input and resolve duration shorthands.

    Returns:
      str: A valid end time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts or the
           user quits.
    """
    max_attempts = 3
    attempts = 0
    anchor_date = start_time.split(' ')[0]

    while attempts < max_attempts:
        value = input("Enter end time (YYYY-MM-DD HH:MM, HH:MM, +Nh/+Nm duration, "
                       "or <Enter> for now), 'q' to quit: ").strip()

        if value == '':
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        if value.lower() == 'q':
            return None

        duration = parse_duration(value)
        if duration is not None:
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            return (start_dt + duration).strftime('%Y-%m-%d %H:%M')

        parsed = parse_flexible_time(value, anchor_date)
        if parsed:
            return parsed

        attempts += 1
        print("Invalid end time. Use YYYY-MM-DD HH:MM, HH:MM, or +Nh/+Nm. "
              f"{max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return None


def get_valid_date():
    """Prompts the user for a date and validates the input.

    Returns:
      str: A valid date string in the format 'YYYY-MM-DD',
           or None if the input is invalid or user quits.
    """
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        date_input = input("Enter date (YYYY-MM-DD or <Enter> to skip), 'q' to quit: ")

        if date_input.lower() == '':
            return None  # Skip this date
        elif date_input.lower() == 'q':
            return 'quit'

        try:
            datetime.strptime(date_input, '%Y-%m-%d')
            return date_input
        except ValueError:
            attempts += 1
            print(f"Invalid date format. Please use YYYY-MM-DD. "
                  f"{max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return 'quit'


def get_valid_edit_time(prompt, current_value, anchor_date, relative_to=None):
    """Prompts for a datetime field during an edit. Blank input keeps
    current_value; 'q' cancels; anything else is re-prompted on invalid
    format instead of aborting. Accepts a full 'YYYY-MM-DD HH:MM', a
    time-only 'HH:MM' anchored to anchor_date, or (when relative_to is
    given) a '+<duration>' shorthand relative to that time.

    Args:
        prompt (str): The prompt to display to the user.
        current_value (str): The value to keep on blank input.
        anchor_date (str): 'YYYY-MM-DD' to combine with an HH:MM-only value.
        relative_to (str, optional): A 'YYYY-MM-DD HH:MM' time to resolve a
            '+<duration>' shorthand against (used when editing end time).

    Returns:
        str: The new or kept value, or None if the user quit.
    """
    while True:
        value = input(prompt).strip()
        if value == '':
            return current_value
        if value.lower() == 'q':
            return None

        if relative_to:
            duration = parse_duration(value)
            if duration is not None:
                start_dt = datetime.strptime(relative_to, '%Y-%m-%d %H:%M')
                return (start_dt + duration).strftime('%Y-%m-%d %H:%M')

        parsed = parse_flexible_time(value, anchor_date)
        if parsed:
            return parsed

        duration_hint = "+Nh/+Nm, " if relative_to else ""
        print(f"Invalid format. Please use YYYY-MM-DD HH:MM, HH:MM, {duration_hint}"
              f"leave blank to keep '{current_value}', or 'q' to cancel.")


def prompt_for_valid_time_range(get_start, get_end):
    """Collects a start/end time pair, re-prompting for both on a
    non-chronological order instead of discarding the rest of an in-progress
    add or edit.

    Args:
        get_start: Zero-arg callable returning a start time string, or None to cancel.
        get_end: One-arg callable(start_time) returning an end time string, or None to cancel.

    Returns:
        tuple: (start_time, end_time), or (None, None) if the user cancelled.
    """
    fmt = '%Y-%m-%d %H:%M'
    while True:
        start_time = get_start()
        if start_time is None:
            return None, None

        end_time = get_end(start_time)
        if end_time is None:
            return None, None

        if datetime.strptime(end_time, fmt) <= datetime.strptime(start_time, fmt):
            print("End time must be after start time. Please re-enter both times.")
            continue

        return start_time, end_time


def format_entry(entry):
    """Format a single work entry for display, including its id for reference
    when editing or deleting.

    Args:
        entry (WorkEntry): The entry to format.

    Returns:
        str: A one-line human-readable representation of the entry.
    """
    return (f"[ID {entry.id}] Project {entry.project_number}: {entry.person} worked from "
            f"{entry.start_time} to {entry.end_time}: {entry.description}")


def print_entries_table(entries):
    """Prints work entries as a column-aligned table, sized to the widest
    value in each column.

    Args:
        entries (list): List of WorkEntry objects to display.
    """
    headers = ["ID", "Project", "Person", "Start", "End", "Description"]
    rows = [
        [str(e.id), e.project_number, e.person, e.start_time, e.end_time, e.description]
        for e in entries
    ]

    widths = [
        max(len(headers[i]), max((len(row[i]) for row in rows), default=0))
        for i in range(len(headers))
    ]

    def format_row(row):
        return "  ".join(value.ljust(width) for value, width in zip(row, widths))

    print(format_row(headers))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))


def format_preview(project_number, person, start_time, end_time, description):
    """Format not-yet-saved entry fields for a confirmation prompt.

    Args:
        project_number (str): The identifier for the project.
        person (str): The name of the person who worked on the project.
        start_time (str): The start time of the work entry.
        end_time (str): The end time of the work entry.
        description (str): A brief description of the work performed.

    Returns:
        str: A one-line human-readable representation of the pending entry.
    """
    return (f"Project {project_number}: {person} worked from "
            f"{start_time} to {end_time}: {description}")


def export_entries_to_csv(entries, filepath):
    """Writes work entries to a CSV file for reporting.

    Args:
        entries (list): List of WorkEntry objects to export.
        filepath (str): Destination path for the CSV file.

    Returns:
        bool: True if the export succeeded, False if it could not be written.
    """
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Project Number', 'Person', 'Start Time', 'End Time', 'Description'])
            for entry in entries:
                writer.writerow([entry.id, entry.project_number, entry.person,
                                  entry.start_time, entry.end_time, entry.description])
        return True
    except OSError as e:
        print(f"Could not write to {filepath}: {e}")
        return False


def confirm(prompt):
    """Asks the user to type 'y' to proceed.

    Args:
        prompt (str): The yes/no question to ask.

    Returns:
        bool: True if the user typed 'y' (case-insensitive), False otherwise.
    """
    return input(prompt).strip().lower() == 'y'


def display_filtered_entries(entries, filter_description):
    """Display a list of work entries with a descriptive header.

    Args:
        entries (list): List of WorkEntry objects to display.
        filter_description (str): Description of the filter applied.
    """
    print("\n+--------------------------------------+")
    print(f"Entries {filter_description}:")
    print("+--------------------------------------+")

    if entries:
        print_entries_table(entries)
        print(f"\nTotal entries found: {len(entries)}")
    else:
        print("No entries found matching the filter criteria.")

    print(f"+--------------------------------------+\n")


def get_entry_for_action(tracker, action_label):
    """Shows recent entries, prompts for an entry id, and looks it up, printing
    feedback on failure.

    Args:
        tracker (WorkTracker): The tracker to look up the entry in.
        action_label (str): Verb describing the action, used in the prompt (e.g. "edit").

    Returns:
        WorkEntry: The matching entry, or None if the user cancelled or the id was invalid.
    """
    recent_entries = tracker.get_recent_entries(limit=10)
    if not recent_entries:
        print(f"No entries to {action_label}.")
        return None

    print("\nMost recent entries (see options 2 or 4 for the full list):")
    print_entries_table(recent_entries)

    entry_id_input = input(f"\nEnter the entry ID to {action_label} (or <Enter> to cancel): ").strip()
    if not entry_id_input:
        return None
    if not entry_id_input.isdigit():
        print("Invalid entry ID.")
        return None

    entry = tracker.get_entry_by_id(int(entry_id_input))
    if not entry:
        print(f"No entry found with ID {entry_id_input}.")
        return None
    return entry


def main():
    """
    Main function to run the Work Tracker application.

    This function initializes the WorkTracker object and loads the last-used
    person and project number from a file. It then enters a loop where the user
    can choose from several options: adding a work entry, viewing all entries,
    searching for total time spent by job number, or exiting the application.

    The function handles user input and calls appropriate methods from the
    WorkTracker class to perform the desired actions.

    Options:
        1. Add work entry: Prompts the user for details about the work entry and
           adds it to the tracker.
        2. View all entries: Displays all current work entries.
        3. Search total time spent by job number: Allows the user to search for
           the total time spent on a specific job number.
        4. Filter entries by date: Filter and view entries by date range or specific dates.
        5. Edit an entry: Update the fields of an existing entry by its ID.
        6. Delete an entry: Remove an existing entry by its ID.
        7. Export entries to CSV: Export all, today's, this week's, or a date
           range of entries to a CSV file for reporting.
        8. Exit: Exits the application.
    """
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.WARNING,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    try:
        tracker = WorkTracker()
    except sqlite3.Error as e:
        logging.exception("Fatal: could not initialize the database")
        print(f"Fatal: could not initialize the database: {e}")
        raise SystemExit(1)

    last_used = load_last_used()
    last_person = last_used['last_person']
    last_project = last_used['last_project']
    print("Welcome to the Work Tracker!")

    while True:
        print("\nOptions:")
        print("1. Add work entry")
        print("2. View all entries")
        print("3. Search total time spent by job number")
        print("4. Filter entries by date")
        print("5. Edit an entry")
        print("6. Delete an entry")
        print("7. Export entries to CSV")
        print("8. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            person = input(f"Enter your name (default: {last_person}): ") or last_person
            project_number = input(f"Enter project number (default: {last_project}): ").strip() or last_project

            start_time, end_time = prompt_for_valid_time_range(get_valid_start_time, get_valid_end_time)
            if start_time is None:
                continue
            print(f"Start time: {start_time}")
            print(f"End time: {end_time}")

            description = input("Enter a description of the work done: ")

            print("\nNew entry:")
            print(format_preview(project_number, person, start_time, end_time, description))
            if not confirm("Type 'y' to confirm adding this entry: "):
                print("Entry not added.")
                continue

            if tracker.add_entry(project_number, person, start_time, end_time, description):
                print('\n+--------------------------------------+')
                print(f"Entry added! {project_number}")
                print(f"{person}")
                print(f"Start time: {start_time} \nEnd time: {end_time}\n")
                print(f"Description - {description}")
                tracker.print_current_entry_time_spent()
                print('\n+--------------------------------------+')
                save_last_used(person, project_number)
                last_person = person
                last_project = project_number
            else:
                print("Failed to save the entry due to a database error.")

        elif choice == '2':
            print("\nCurrent Entries:")
            entries = tracker.get_all_entries()
            if entries:
                print_entries_table(entries)
            else:
                print("No entries found.")
        elif choice == '3':
            job_number = input("Enter the job number to search for total time spent: ")
            total_time = tracker.get_total_time_spent()
            print('\n+--------------------------------------+')
            if job_number in total_time:
                matching_entries = [e for e in tracker.get_all_entries() if e.project_number == job_number]
                print_entries_table(matching_entries)
                print(f"{total_time[job_number]:.2f} hours spent on {job_number}.")
            else:
                print(f"No entries found for {job_number}.")
            print('+--------------------------------------+\n')

        elif choice == '4':
            print("\n+--------------------------------------+")
            print("Date Filter Options:")
            print("1. Today's entries")
            print("2. This week's entries")
            print("3. Custom date range")
            print("4. Return to main menu")
            print("+--------------------------------------+")
            
            filter_choice = input("Choose filter option: ")
            
            if filter_choice == '1':
                entries = tracker.filter_entries_by_today()
                display_filtered_entries(entries, "for today")
                
            elif filter_choice == '2':
                entries = tracker.filter_entries_by_this_week()
                display_filtered_entries(entries, "for this week")
                
            elif filter_choice == '3':
                print("\nEnter date range (leave blank to skip):")
                start_date = get_valid_date()
                if start_date == 'quit':
                    continue
                    
                end_date = get_valid_date()
                if end_date == 'quit':
                    continue
                
                # Optional project filter
                project_filter = input("Enter project number to filter by (or <Enter> for all): ").strip()
                project_filter = project_filter if project_filter else None
                
                entries = tracker.filter_entries_by_date_range(
                    start_date=start_date, 
                    end_date=end_date, 
                    project_number=project_filter
                )
                
                # Build description for display
                desc_parts = []
                if start_date:
                    desc_parts.append(f"from {start_date}")
                if end_date:
                    desc_parts.append(f"to {end_date}")
                if project_filter:
                    desc_parts.append(f"for project {project_filter}")
                    
                description = " ".join(desc_parts) if desc_parts else "with no date filter"
                display_filtered_entries(entries, description)
                
                # Show time totals if entries found
                if entries:
                    totals = tracker.get_total_time_by_date_range(
                        start_date=start_date, 
                        end_date=end_date, 
                        project_number=project_filter
                    )
                    print("Time totals by project:")
                    for project, hours in totals.items():
                        print(f"  Project {project}: {hours:.2f} hours")
                    print()
                    
            elif filter_choice == '4':
                continue  # Return to main menu
            else:
                print("Invalid choice. Returning to main menu.")

        elif choice == '5':
            entry = get_entry_for_action(tracker, "edit")
            if not entry:
                continue

            print("\nCurrent entry:")
            print(format_entry(entry))
            print("Leave a field blank to keep its current value. Times also accept HH:MM "
                  "(same day) or, for end time, +Nh/+Nm relative to start. Enter 'q' at a "
                  "time prompt to cancel.\n")

            project_number = input(f"Project number [{entry.project_number}]: ").strip() or entry.project_number
            person = input(f"Person [{entry.person}]: ").strip() or entry.person

            entry_start_date = entry.start_time.split(' ')[0]
            start_time, end_time = prompt_for_valid_time_range(
                lambda: get_valid_edit_time(
                    f"Start time [{entry.start_time}] (YYYY-MM-DD HH:MM or HH:MM): ",
                    entry.start_time, anchor_date=entry_start_date),
                lambda start_time: get_valid_edit_time(
                    f"End time [{entry.end_time}] (YYYY-MM-DD HH:MM, HH:MM, or +Nh/+Nm): ",
                    entry.end_time, anchor_date=start_time.split(' ')[0], relative_to=start_time),
            )
            if start_time is None:
                print("Edit cancelled.")
                continue

            description = input(f"Description [{entry.description}]: ").strip() or entry.description

            print("\nUpdated entry will be:")
            print(format_preview(project_number, person, start_time, end_time, description))
            if not confirm("Type 'y' to confirm this update: "):
                print("Edit cancelled.")
                continue

            if tracker.update_entry(entry.id, project_number, person, start_time, end_time, description):
                print("Entry updated.")
            else:
                print("Failed to update the entry due to a database error.")

        elif choice == '6':
            entry = get_entry_for_action(tracker, "delete")
            if not entry:
                continue

            print("\nEntry to delete:")
            print(format_entry(entry))
            if confirm("Type 'y' to confirm deletion: "):
                if tracker.delete_entry(entry.id):
                    print("Entry deleted.")
                else:
                    print("Failed to delete the entry due to a database error.")
            else:
                print("Deletion cancelled.")

        elif choice == '7':
            print("\n+--------------------------------------+")
            print("Export Options:")
            print("1. All entries")
            print("2. Today's entries")
            print("3. This week's entries")
            print("4. Custom date range")
            print("5. Return to main menu")
            print("+--------------------------------------+")

            export_choice = input("Choose export option: ")

            if export_choice == '1':
                entries = tracker.get_all_entries()
            elif export_choice == '2':
                entries = tracker.filter_entries_by_today()
            elif export_choice == '3':
                entries = tracker.filter_entries_by_this_week()
            elif export_choice == '4':
                print("\nEnter date range (leave blank to skip):")
                start_date = get_valid_date()
                if start_date == 'quit':
                    continue
                end_date = get_valid_date()
                if end_date == 'quit':
                    continue
                project_filter = input("Enter project number to filter by (or <Enter> for all): ").strip()
                project_filter = project_filter if project_filter else None
                entries = tracker.filter_entries_by_date_range(
                    start_date=start_date,
                    end_date=end_date,
                    project_number=project_filter
                )
            elif export_choice == '5':
                continue
            else:
                print("Invalid choice. Returning to main menu.")
                continue

            if not entries:
                print("No entries to export.")
                continue

            default_filename = f"work_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filename = input(f"Enter filename to export to (default: {default_filename}): ").strip() or default_filename

            if export_entries_to_csv(entries, filename):
                print(f"Exported {len(entries)} entries to {filename}")
            else:
                print("Export failed.")

        elif choice == '8':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
