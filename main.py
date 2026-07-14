import os
import json
import logging
import sqlite3
from datetime import datetime
from work_tracker import WorkTracker

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_tracker.log')

def load_last_person():
    """
    Loads the last person's name from a JSON file located in the 'data' directory.

    If the 'data' directory does not exist, it creates the directory.
    If the 'last_person.json' file exists, it reads the file and returns the value
    associated with the 'last_person' key. If the key does not exist, it returns an
    empty string. If the file does not exist, it returns an empty string.

    Returns:
        str: The name of the last person or an empty string if not found.
    """
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    json_file_path = os.path.join(data_dir, 'last_person.json')

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('last_person', '')
    return ''

def save_last_person(person):
    """
    Saves the provided person's data to a JSON file in the 'data' directory.

    If the 'data' directory does not exist, it creates the directory.
    The function writes the person's data to a file named 'last_person.json'
    in JSON format, with the key 'last_person'.

    Args:
        person (str): The name of the person to be saved.
    """
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    json_file_path = os.path.join(data_dir, 'last_person.json')

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump({'last_person': person}, f)


def get_valid_input(prompt, fmt, empty_value, quit_value, invalid_label):
    """Prompts the user for a value matching a datetime format, with an empty-input
    default and a quit sentinel, retrying on invalid input.

    Args:
        prompt (str): The prompt to display to the user.
        fmt (str): The strptime/strftime format the input must match.
        empty_value: Value to return (or zero-arg callable to invoke) on empty input.
        quit_value: Value to return if the user quits or exhausts their attempts.
        invalid_label (str): Human-readable description used in the error message.

    Returns:
        The parsed input string, the resolved empty_value, or quit_value.
    """
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        value = input(prompt)

        if value.lower() == '':
            return empty_value() if callable(empty_value) else empty_value
        elif value.lower() == 'q':
            return quit_value

        try:
            datetime.strptime(value, fmt)
            return value
        except ValueError:
            attempts += 1
            print(f"Invalid {invalid_label} format. Please use {fmt}. "
                  f"{max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return quit_value


def get_valid_start_time():
    """Prompts the user for a start time and validates the input.

    Returns:
      str: A valid start time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts.
    """
    return get_valid_input(
        "Enter start time (YYYY-MM-DD HH:MM or <Enter> for now), 'q' to quit: ",
        '%Y-%m-%d %H:%M',
        empty_value=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'),
        quit_value=None,
        invalid_label="date or time",
    )


def get_valid_end_time():
    """Prompts the user for a end time and validates the input.

    Returns:
      str: A valid end time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts.
    """
    return get_valid_input(
        "Enter end time (YYYY-MM-DD HH:MM or <Enter> for now, 'q' to quit): ",
        '%Y-%m-%d %H:%M',
        empty_value=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'),
        quit_value=None,
        invalid_label="date or time",
    )


def get_valid_date():
    """Prompts the user for a date and validates the input.

    Returns:
      str: A valid date string in the format 'YYYY-MM-DD',
           or None if the input is invalid or user quits.
    """
    return get_valid_input(
        "Enter date (YYYY-MM-DD or <Enter> to skip), 'q' to quit: ",
        '%Y-%m-%d',
        empty_value=None,
        quit_value='quit',
        invalid_label="date",
    )


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
        for entry in entries:
            print(format_entry(entry))
        print(f"\nTotal entries found: {len(entries)}")
    else:
        print("No entries found matching the filter criteria.")

    print(f"+--------------------------------------+\n")


def get_entry_for_action(tracker, action_label):
    """Prompts for an entry id and looks it up, printing feedback on failure.

    Args:
        tracker (WorkTracker): The tracker to look up the entry in.
        action_label (str): Verb describing the action, used in the prompt (e.g. "edit").

    Returns:
        WorkEntry: The matching entry, or None if the user cancelled or the id was invalid.
    """
    entry_id_input = input(f"Enter the entry ID to {action_label} (or <Enter> to cancel): ").strip()
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

    This function initializes the WorkTracker object and loads the last person's
    name from a file. It then enters a loop where the user can choose from several
    options: adding a work entry, viewing all entries, searching for total time
    spent by job number, or exiting the application.

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
        7. Exit: Exits the application.
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

    last_person = load_last_person()
    print("Welcome to the Work Tracker!")

    while True:
        print("\nOptions:")
        print("1. Add work entry")
        print("2. View all entries")
        print("3. Search total time spent by job number")
        print("4. Filter entries by date")
        print("5. Edit an entry")
        print("6. Delete an entry")
        print("7. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            person = input(f"Enter your name (default: {last_person}): ") or last_person
            project_number = input("Enter project number: ")
            start_time = get_valid_start_time()
            if start_time is None:
                continue
            print(f"Start time: {start_time}")
            end_time = get_valid_end_time()
            if end_time is None:
                continue
            print(f"End time: {end_time}")

            parsed_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            parsed_end = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            if parsed_end <= parsed_start:
                print("End time must be after start time. Entry not added.")
                continue

            description = input("Enter a description of the work done: ")

            if tracker.add_entry(project_number, person, start_time, end_time, description):
                print('\n+--------------------------------------+')
                print(f"Entry added! {project_number}")
                print(f"{person}")
                print(f"Start time: {start_time} \nEnd time: {end_time}\n")
                print(f"Description - {description}")
                tracker.print_current_entry_time_spent()
                print('\n+--------------------------------------+')
                save_last_person(person)
            else:
                print("Failed to save the entry due to a database error.")

        elif choice == '2':
            print("\nCurrent Entries:")
            for entry in tracker.get_all_entries():
                print(format_entry(entry))
        elif choice == '3':
            job_number = input("Enter the job number to search for total time spent: ")
            total_time = tracker.get_total_time_spent()
            print('\n+--------------------------------------+')
            if job_number in total_time:
                for entry in tracker.get_all_entries():
                    if entry.project_number == job_number:
                        print(format_entry(entry))
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
            print("Leave a field blank to keep its current value.\n")

            project_number = input(f"Project number [{entry.project_number}]: ").strip() or entry.project_number
            person = input(f"Person [{entry.person}]: ").strip() or entry.person
            start_time = input(f"Start time [{entry.start_time}] (YYYY-MM-DD HH:MM): ").strip() or entry.start_time
            end_time = input(f"End time [{entry.end_time}] (YYYY-MM-DD HH:MM): ").strip() or entry.end_time
            description = input(f"Description [{entry.description}]: ").strip() or entry.description

            try:
                parsed_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
                parsed_end = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            except ValueError:
                print("Invalid date/time format. Edit cancelled.")
                continue

            if parsed_end <= parsed_start:
                print("End time must be after start time. Edit cancelled.")
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
            confirm = input("Type 'y' to confirm deletion: ").strip().lower()
            if confirm == 'y':
                if tracker.delete_entry(entry.id):
                    print("Entry deleted.")
                else:
                    print("Failed to delete the entry due to a database error.")
            else:
                print("Deletion cancelled.")

        elif choice == '7':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
