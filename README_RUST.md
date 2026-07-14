# Work Tracker - Rust Version

A Rust implementation of the Work Tracker application for tracking time spent on various projects.

## Features

- Add work entries with project number, person, start/end times, and descriptions
- View all work entries
- Search total time spent by job number
- Filter entries by date ranges:
  - Today's entries
  - This week's entries
  - Custom date ranges
- Project-specific filtering within date ranges
- Persistent storage using SQLite database
- JSON-based storage for user preferences

## Dependencies

- **rusqlite**: SQLite database operations
- **serde**: JSON serialization/deserialization  
- **chrono**: Date and time handling
- **anyhow**: Error handling

## Building and Running

### Prerequisites
Make sure you have Rust installed. If not, install it from [rustup.rs](https://rustup.rs/).

### Build the project:
```bash
cargo build --release
```

### Run the application:
```bash
cargo run
```

### Run in development mode:
```bash
cargo run
```

## Project Structure

- `src/main.rs` - Main application with menu system and user interface
- `src/work_tracker.rs` - Core work tracking logic and database operations
- `src/utils.rs` - Utility functions for data persistence
- `Cargo.toml` - Project configuration and dependencies

## Usage

The application provides a menu-driven interface with the following options:

1. **Add work entry** - Create a new time tracking entry
2. **View all entries** - Display all recorded work entries  
3. **Search total time spent by job number** - Find total hours for a specific project
4. **Filter entries by date** - View entries filtered by various date criteria
5. **Exit** - Close the application

### Date Filtering Options

When selecting option 4, you can filter entries by:
- **Today's entries** - Show only today's work
- **This week's entries** - Show current week's work (Monday-Sunday)
- **Custom date range** - Specify start/end dates and optionally filter by project

## Data Storage

- Work entries are stored in `work_tracker.db` (SQLite database)
- Last used person name is saved in `data/last_person.json`

## Migration from Python Version

This Rust version maintains compatibility with the SQLite database created by the Python version, so you can use the same data files.