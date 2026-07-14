import os
import json
from datetime import datetime
from work_tracker import WorkTracker

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


def get_valid_start_time():
    """Prompts the user for a start time and validates the input.

    Returns:
      str: A valid start time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts.
    """

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        start_time_input = input("Enter start time (YYYY-MM-DD HH:MM or <Enter> for now), 'q' to quit: ")

        if start_time_input.lower() == '':
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        elif start_time_input.lower() == 'q':
            return None

        try:
            datetime.strptime(start_time_input, '%Y-%m-%d %H:%M')
            return start_time_input
        except ValueError:
            attempts += 1
            print(f"Invalid date or time format. Please use YYYY-MM-DD HH:MM. \
                {max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return None

def get_valid_end_time():
    """Prompts the user for a end time and validates the input.

    Returns:
      str: A valid end time string in the format '%Y-%m-%d %H:%M',
           or None if the input is invalid after several attempts.
    """

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        end_time_input = input("Enter end time (YYYY-MM-DD HH:MM or <Enter> for now, 'q' to quit): ")

        if end_time_input.lower() == '':
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        elif end_time_input.lower() == 'q':
            return None

        try:
            datetime.strptime(end_time_input, '%Y-%m-%d %H:%M')
            return end_time_input
        except ValueError:
            attempts += 1
            print(f"Invalid date or time format. Please use YYYY-MM-DD HH:MM. \
                {max_attempts - attempts} attempts remaining.")

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
            # Validate date format
            datetime.strptime(date_input, '%Y-%m-%d')
            return date_input
        except ValueError:
            attempts += 1
            print(f"Invalid date format. Please use YYYY-MM-DD. "
                  f"{max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return 'quit'


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
            print(f"Project {entry.project_number}: {entry.person} worked from "
                  f"{entry.start_time} to {entry.end_time}: {entry.description}")
        print(f"\nTotal entries found: {len(entries)}")
    else:
        print("No entries found matching the filter criteria.")
    
    print(f"+--------------------------------------+\n")


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
        5. Exit: Exits the application.
    """
    tracker = WorkTracker()
    last_person = load_last_person()
    print("Welcome to the Work Tracker!")

    while True:
        print("\nOptions:")
        print("1. Add work entry")
        print("2. View all entries")
        print("3. Search total time spent by job number")
        print("4. Filter entries by date")
        print("5. Exit")
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
            description = input("Enter a description of the work done: ")

            if start_time or end_time:
                tracker.add_entry(project_number, person, start_time, end_time, description)
                print('\n+--------------------------------------+')
                print(F"Entry added! \b{project_number}\b")
                print(f"{person}")
                print(f"Start time: {start_time} \nEnd time: {end_time}\n")
                print(f"Description - {description}")
                tracker.print_current_entry_time_spent()
                print('\n+--------------------------------------+')
                save_last_person(person)

            else:
                print("Invalid start or end time. Entry not added.")
                continue

        elif choice == '2':
            print("\nCurrent Entries:")
            for entry in tracker.get_all_entries():
                print(f"Project {entry.project_number}: {entry.person} worked from "
                      f"{entry.start_time} to {entry.end_time}: {entry.description}")
        elif choice == '3': #TODO: Implement print each row of the table from the select query
            job_number = input("Enter the job number to search for total time spent: ")
            total_time = tracker.get_total_time_spent()
            print('\n+--------------------------------------+')
            if job_number in total_time:
                for entry in tracker.get_all_entries():
                    if entry.project_number == job_number:
                        print(f"Project {entry.project_number}: {entry.person} worked from "
                              f"{entry.start_time} to {entry.end_time}: {entry.description}")
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
            break

if __name__ == "__main__":
    main()
