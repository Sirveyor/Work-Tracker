# Work Tracker

A command-line app for tracking time spent on projects and generating reports of time worked.

## Features

- **Add work entries** — project number, person, start/end time, and description
- **View all entries** in a column-aligned table
- **Search total time spent** by job number
- **Filter entries by date** — today, this week, or a custom date range, optionally scoped to one project
- **Edit or delete an entry** — shows the 10 most recent entries to pick an ID from, previews the change, and asks for confirmation before saving
- **Export entries to CSV** for reporting — all entries, today's, this week's, or a custom date range
- **Remembers the last-used person and project number** between runs
- **Flexible time entry**:
  - Full timestamp: `2026-01-05 09:30`
  - Same-day shorthand: `09:30` (anchored to today when adding, or to the entry's own date when editing)
  - Duration shorthand for end time, relative to the start time just entered: `+2h`, `+90m`, `+1h30m`
- Confirmation prompt (`y`) before every add, edit, or delete
- Errors are logged with full tracebacks to `work_tracker.log`; the terminal only shows a short message

## Requirements

Python 3.11+ and the standard library — no runtime dependencies.

## Running

```bash
python main.py
```

## Menu

```
1. Add work entry
2. View all entries
3. Search total time spent by job number
4. Filter entries by date
5. Edit an entry
6. Delete an entry
7. Export entries to CSV
8. Exit
```

Options 4 and 7 open a submenu to pick **today's entries**, **this week's entries**, a **custom date range** (with an optional project filter), or (option 7 only) **all entries**.

## Data storage

- Work entries: `work_tracker.db` (SQLite), created next to the script regardless of the current working directory
- Remembered person/project: `data/last_used.json`
- Error log: `work_tracker.log`

None of these are tracked in git (see `.gitignore`).

## Development

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest
```

Tests run automatically on push/PR via GitHub Actions (`.github/workflows/tests.yml`) across Python 3.11–3.13.

## Project structure

- `main.py` — CLI entry point: menu loop, input validation/parsing, formatting, CSV export
- `work_tracker.py` — `WorkTracker`/`WorkEntry` and all database operations
- `database.py` — SQLite connection and table setup
- `tests/` — pytest suite
- `src/*.rs`, `Cargo.toml` — an in-progress Rust port of this app (see [README_RUST.md](README_RUST.md))

## License

GPL-3.0 — see [LICENSE](LICENSE).
