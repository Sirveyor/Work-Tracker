mod utils;
mod work_tracker;

use anyhow::Result;
use chrono::Local;
use std::io::{self, Write};
use work_tracker::{WorkEntry, WorkTracker};

fn get_valid_start_time() -> Result<Option<String>> {
    let max_attempts = 3;
    let mut attempts = 0;

    while attempts < max_attempts {
        print!("Enter start time (YYYY-MM-DD HH:MM or <Enter> for now), 'q' to quit: ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();

        if input.is_empty() {
            return Ok(Some(Local::now().format("%Y-%m-%d %H:%M").to_string()));
        } else if input.to_lowercase() == "q" {
            return Ok(None);
        }

        if validate_datetime_format(input) {
            return Ok(Some(input.to_string()));
        } else {
            attempts += 1;
            println!(
                "Invalid date or time format. Please use YYYY-MM-DD HH:MM. {} attempts remaining.",
                max_attempts - attempts
            );
        }
    }

    println!("Too many invalid attempts. Please try again later.");
    Ok(None)
}

fn get_valid_end_time() -> Result<Option<String>> {
    let max_attempts = 3;
    let mut attempts = 0;

    while attempts < max_attempts {
        print!("Enter end time (YYYY-MM-DD HH:MM or <Enter> for now, 'q' to quit): ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();

        if input.is_empty() {
            return Ok(Some(Local::now().format("%Y-%m-%d %H:%M").to_string()));
        } else if input.to_lowercase() == "q" {
            return Ok(None);
        }

        if validate_datetime_format(input) {
            return Ok(Some(input.to_string()));
        } else {
            attempts += 1;
            println!(
                "Invalid date or time format. Please use YYYY-MM-DD HH:MM. {} attempts remaining.",
                max_attempts - attempts
            );
        }
    }

    println!("Too many invalid attempts. Please try again later.");
    Ok(None)
}

fn get_valid_date() -> Result<String> {
    let max_attempts = 3;
    let mut attempts = 0;

    while attempts < max_attempts {
        print!("Enter date (YYYY-MM-DD or <Enter> to skip), 'q' to quit: ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();

        if input.is_empty() {
            return Ok("skip".to_string());
        } else if input.to_lowercase() == "q" {
            return Ok("quit".to_string());
        }

        if validate_date_format(input) {
            return Ok(input.to_string());
        } else {
            attempts += 1;
            println!(
                "Invalid date format. Please use YYYY-MM-DD. {} attempts remaining.",
                max_attempts - attempts
            );
        }
    }

    println!("Too many invalid attempts. Please try again later.");
    Ok("quit".to_string())
}

fn validate_datetime_format(input: &str) -> bool {
    chrono::NaiveDateTime::parse_from_str(input, "%Y-%m-%d %H:%M").is_ok()
}

fn validate_date_format(input: &str) -> bool {
    chrono::NaiveDate::parse_from_str(input, "%Y-%m-%d").is_ok()
}

fn display_filtered_entries(entries: &[WorkEntry], filter_description: &str) {
    println!("\n+--------------------------------------+");
    println!("Entries {}:", filter_description);
    println!("+--------------------------------------+");

    if !entries.is_empty() {
        for entry in entries {
            println!(
                "Project {}: {} worked from {} to {}: {}",
                entry.project_number, entry.person, entry.start_time, entry.end_time, entry.description
            );
        }
        println!("\nTotal entries found: {}", entries.len());
    } else {
        println!("No entries found matching the filter criteria.");
    }

    println!("+--------------------------------------+\n");
}

fn get_input(prompt: &str) -> Result<String> {
    print!("{}", prompt);
    io::stdout().flush()?;
    let mut input = String::new();
    io::stdin().read_line(&mut input)?;
    Ok(input.trim().to_string())
}

fn main() -> Result<()> {
    println!("Welcome to the Work Tracker!");
    let tracker = WorkTracker::new()?;
    let last_person = utils::load_last_person().unwrap_or_default();

    loop {
        println!("\nOptions:");
        println!("1. Add work entry");
        println!("2. View all entries");
        println!("3. Search total time spent by job number");
        println!("4. Filter entries by date");
        println!("5. Exit");

        let choice = get_input("Choose an option: ")?;

        match choice.as_str() {
            "1" => {
                println!("\n+--------------------------------------+");
                let person_prompt = format!("Enter your name (default: {}): ", last_person);
                let person_input = get_input(&person_prompt)?;
                let person = if person_input.is_empty() {
                    last_person.clone()
                } else {
                    person_input
                };

                let project_number = get_input("Enter project number: ")?;

                let start_time = match get_valid_start_time()? {
                    Some(time) => time,
                    None => continue,
                };
                println!("Start time: {}", start_time);

                let end_time = match get_valid_end_time()? {
                    Some(time) => time,
                    None => continue,
                };
                println!("End time: {}", end_time);

                let description = get_input("Enter a description of the work done: ")?;

                if !start_time.is_empty() && !end_time.is_empty() {
                    tracker.add_entry(&project_number, &person, &start_time, &end_time, &description)?;
                    println!("\n+--------------------------------------+");
                    println!("Entry added! {}", project_number);
                    println!("{}", person);
                    println!("Start time: {}", start_time);
                    println!("End time: {}", end_time);
                    println!("Description - {}", description);
                    tracker.print_current_entry_time_spent()?;
                    println!("+--------------------------------------+");
                    utils::save_last_person(&person)?;
                } else {
                    println!("Invalid start or end time. Entry not added.");
                    continue;
                }
            }
            "2" => {
                println!("\n+--------------------------------------+");
                println!("Current Entries:");
                let entries = tracker.get_all_entries()?;
                for entry in entries {
                    println!(
                        "Project {}: {} worked from {} to {}: {}",
                        entry.project_number, entry.person, entry.start_time, entry.end_time, entry.description
                    );
                }
                println!("+--------------------------------------+");
            }
            "3" => {
                println!("\n+--------------------------------------+");
                let job_number = get_input("Enter the job number to search for total time spent: ")?;
                let total_time = tracker.get_total_time_spent()?;
                println!("\n+--------------------------------------+");
                if let Some(&hours) = total_time.get(&job_number) {
                    let all_entries = tracker.get_all_entries()?;
                    for entry in all_entries {
                        if entry.project_number == job_number {
                            println!(
                                "Project {}: {} worked from {} to {}: {}",
                                entry.project_number, entry.person, entry.start_time, entry.end_time, entry.description
                            );
                        }
                    }
                    println!("{:.2} hours spent on {}.", hours, job_number);
                } else {
                    println!("No entries found for {}.", job_number);
                }
                println!("+--------------------------------------+\n");
            }
            "4" => {
                println!("\n+--------------------------------------+");
                println!("Date Filter Options:");
                println!("1. Today's entries");
                println!("2. This week's entries");
                println!("3. Custom date range");
                println!("4. Return to main menu");
                println!("+--------------------------------------+");

                let filter_choice = get_input("Choose filter option: ")?;

                match filter_choice.as_str() {
                    "1" => {
                        let entries = tracker.filter_entries_by_today(None)?;
                        display_filtered_entries(&entries, "for today");
                    }
                    "2" => {
                        let entries = tracker.filter_entries_by_this_week(None)?;
                        display_filtered_entries(&entries, "for this week");
                    }
                    "3" => {
                        println!("\nEnter date range (leave blank to skip):");
                        let start_date = get_valid_date()?;
                        if start_date == "quit" {
                            continue;
                        }

                        let end_date = get_valid_date()?;
                        if end_date == "quit" {
                            continue;
                        }

                        let project_filter_input = get_input("Enter project number to filter by (or <Enter> for all): ")?;
                        let project_filter = if project_filter_input.is_empty() {
                            None
                        } else {
                            Some(project_filter_input.as_str())
                        };

                        let start_opt = if start_date == "skip" { None } else { Some(start_date.as_str()) };
                        let end_opt = if end_date == "skip" { None } else { Some(end_date.as_str()) };

                        let entries = tracker.filter_entries_by_date_range(start_opt, end_opt, project_filter)?;

                        let mut desc_parts = Vec::new();
                        if let Some(start) = start_opt {
                            desc_parts.push(format!("from {}", start));
                        }
                        if let Some(end) = end_opt {
                            desc_parts.push(format!("to {}", end));
                        }
                        if let Some(project) = project_filter {
                            desc_parts.push(format!("for project {}", project));
                        }

                        let description = if desc_parts.is_empty() {
                            "with no date filter".to_string()
                        } else {
                            desc_parts.join(" ")
                        };

                        display_filtered_entries(&entries, &description);

                        if !entries.is_empty() {
                            let totals = tracker.get_total_time_by_date_range(start_opt, end_opt, project_filter)?;
                            println!("Time totals by project:");
                            for (project, hours) in totals {
                                println!("  Project {}: {:.2} hours", project, hours);
                            }
                            println!();
                        }
                    }
                    "4" => continue,
                    _ => println!("Invalid choice. Returning to main menu."),
                }
            }
            "5" => break,
            _ => println!("Invalid option. Please choose 1-5."),
        }
    }

    println!("Thank you for using Work Tracker!");
    Ok(())
}