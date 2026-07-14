import csv

from main import export_entries_to_csv
from work_tracker import WorkEntry


def test_export_entries_to_csv(tmp_path):
    entries = [
        WorkEntry(1, "P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first"),
        WorkEntry(2, "P2", "Bob", "2026-01-06 09:00", "2026-01-06 11:00", "second"),
    ]
    filepath = tmp_path / "export.csv"

    assert export_entries_to_csv(entries, str(filepath)) is True

    with open(filepath, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    assert rows[0] == ['ID', 'Project Number', 'Person', 'Start Time', 'End Time', 'Description']
    assert rows[1] == ['1', 'P1', 'Alice', '2026-01-05 09:00', '2026-01-05 10:00', 'first']
    assert rows[2] == ['2', 'P2', 'Bob', '2026-01-06 09:00', '2026-01-06 11:00', 'second']
    assert len(rows) == 3


def test_export_entries_to_csv_empty_list(tmp_path):
    filepath = tmp_path / "export.csv"

    assert export_entries_to_csv([], str(filepath)) is True

    with open(filepath, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    assert rows == [['ID', 'Project Number', 'Person', 'Start Time', 'End Time', 'Description']]


def test_export_entries_to_csv_unwritable_path_returns_false():
    entries = [WorkEntry(1, "P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first")]

    # A directory that doesn't exist and can't be created as a file path.
    unwritable_path = "/no/such/directory/export.csv"

    assert export_entries_to_csv(entries, unwritable_path) is False
