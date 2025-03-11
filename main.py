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
        start_time_input = input("Enter start time (YYYY-MM-DD HH:MM or 'now'): ")

        if start_time_input.lower() == 'now':
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
        end_time_input = input("Enter end time (YYYY-MM-DD HH:MM or 'now'): ")

        if end_time_input.lower() == 'now':
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
        4. Exit: Exits the application.
    """
    tracker = WorkTracker()
    last_person = load_last_person()
    print("Welcome to the Work Tracker!")

    while True:
        print("\nOptions:")
        print("1. Add work entry")
        print("2. View all entries")
        print("3. Search total time spent by job number")
        print("4. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            person = input(f"Enter your name (default: {last_person}): ") or last_person
            project_number = input("Enter project number: ")
            start_time = get_valid_start_time()
            end_time = get_valid_end_time()
            description = input("Enter a description of the work done: ")
            
            if start_time or end_time:
                tracker.add_entry(project_number, person, start_time, end_time, description)
                last_entry = tracker.get_last_entry()
                print([last_entry])
                tracker.print_current_entry_time_spent()
                print("Entry added!")
                save_last_person(person)
                print('\n')
            else:
                print("Invalid start or end time. Entry not added.")
                main()

        elif choice == '2':
            print("\nCurrent Entries:")
            for entry in tracker.get_entries():
                print(f"Project {entry.project_number}: {entry.person} worked from {entry.start_time}\
                    to {entry.end_time}: {entry.description}")

        elif choice == '3':
            job_number = input("Enter the job number to search for total time spent: ")
            total_time = tracker.get_total_time_spent()
            if job_number in total_time:
                print(f"{total_time[job_number]:.2f} hours spent on {job_number}.")
            else:
                print(f"No entries found for {job_number}.")

        elif choice == '4':
            break

if __name__ == "__main__":
    main()
