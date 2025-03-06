import os
import json
from datetime import datetime
from work_tracker import WorkTracker

def load_last_person():
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    json_file_path = os.path.join(data_dir, 'last_person.json')
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('last_person', '')
    return ''

def save_last_person(person):
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

        try:
            datetime.strptime(start_time_input, '%Y-%m-%d %H:%M')
            return start_time_input
        except ValueError:
            attempts += 1
            print(f"Invalid date or time format. Please use YYYY-MM-DD HH:MM. {max_attempts - attempts} attempts remaining.")

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

        try:
            datetime.strptime(end_time_input, '%Y-%m-%d %H:%M')
            return end_time_input
        except ValueError:
            attempts += 1
            print(f"Invalid date or time format. Please use YYYY-MM-DD HH:MM. {max_attempts - attempts} attempts remaining.")

    print("Too many invalid attempts. Please try again later.")
    return None


def main():
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
            #start_time_input = input("Enter start time (or 'now' for current time): ")
            start_time = get_valid_start_time()
            #start_time = datetime.now().strftime('%Y-%m-%d %H:%M') if start_time_input.lower() == 'now' else start_time_input
            #end_time_input = input("Enter end time (or 'now' for current time): ")
            end_time = get_valid_end_time()
            #end_time = datetime.now().strftime('%Y-%m-%d %H:%M') if end_time_input.lower() == 'now' else end_time_input
            description = input("Enter a description of the work done: ")
            tracker.add_entry(project_number, person, start_time, end_time, description)
            print(tracker.get_last_entry())
            print(tracker.print_current_entry_time_spent())
            print("Entry added!")
            save_last_person(person)
            print('\n')

        elif choice == '2':
            print("\nCurrent Entries:")
            for entry in tracker.get_entries():
                print(f"Project {entry.project_number}: {entry.person} worked from {entry.start_time} to {entry.end_time}: {entry.description}")

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
