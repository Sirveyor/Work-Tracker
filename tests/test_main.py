import csv
from datetime import timedelta

import pytest

from main import (
    export_entries_to_csv,
    get_valid_edit_time,
    get_valid_end_time,
    get_valid_start_time,
    parse_duration,
    parse_flexible_time,
    print_entries_table,
)
from work_tracker import WorkEntry


def queued_input(monkeypatch, values):
    """Feeds a fixed queue of responses to successive input() calls."""
    responses = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt='': next(responses))


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


@pytest.mark.parametrize("text,expected", [
    ("+2h", timedelta(hours=2)),
    ("+90m", timedelta(minutes=90)),
    ("+1h30m", timedelta(hours=1, minutes=30)),
    ("+2H", timedelta(hours=2)),  # case-insensitive
])
def test_parse_duration_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["+", "2h", "+2x", "+2hr", ""])
def test_parse_duration_invalid(text):
    assert parse_duration(text) is None


def test_parse_flexible_time_full_datetime():
    assert parse_flexible_time("2026-01-05 09:30", "2026-01-01") == "2026-01-05 09:30"


def test_parse_flexible_time_hh_mm_anchored():
    assert parse_flexible_time("09:30", "2026-01-05") == "2026-01-05 09:30"


def test_parse_flexible_time_invalid():
    assert parse_flexible_time("not a time", "2026-01-05") is None


def test_get_valid_start_time_accepts_hh_mm_shorthand(monkeypatch):
    queued_input(monkeypatch, ["09:30"])
    result = get_valid_start_time()
    assert result.endswith(" 09:30")
    assert len(result) == len("2026-01-05 09:30")


def test_get_valid_end_time_accepts_duration_shorthand(monkeypatch):
    queued_input(monkeypatch, ["+2h"])
    result = get_valid_end_time("2026-01-05 09:00")
    assert result == "2026-01-05 11:00"


def test_get_valid_end_time_accepts_hh_mm_anchored_to_start_date(monkeypatch):
    queued_input(monkeypatch, ["17:00"])
    result = get_valid_end_time("2026-01-05 09:00")
    assert result == "2026-01-05 17:00"


def test_get_valid_end_time_retries_on_invalid_then_accepts(monkeypatch):
    queued_input(monkeypatch, ["nonsense", "+1h"])
    result = get_valid_end_time("2026-01-05 09:00")
    assert result == "2026-01-05 10:00"


def test_get_valid_edit_time_blank_keeps_current(monkeypatch):
    queued_input(monkeypatch, [""])
    result = get_valid_edit_time("prompt: ", "2026-01-05 09:00", anchor_date="2026-01-05")
    assert result == "2026-01-05 09:00"


def test_get_valid_edit_time_accepts_duration_relative_to_start(monkeypatch):
    queued_input(monkeypatch, ["+30m"])
    result = get_valid_edit_time(
        "prompt: ", "2026-01-05 10:00", anchor_date="2026-01-05", relative_to="2026-01-05 09:00")
    assert result == "2026-01-05 09:30"


def test_print_entries_table_aligns_columns(capsys):
    entries = [
        WorkEntry(1, "P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "short"),
        WorkEntry(22, "P200", "Bob", "2026-01-06 09:00", "2026-01-06 11:00", "a much longer description"),
    ]

    print_entries_table(entries)
    lines = capsys.readouterr().out.rstrip("\n").split("\n")

    # header, separator, and one row per entry
    assert len(lines) == 4
    assert lines[0].startswith("ID")
    assert lines[1].startswith("--")
    # the ID column should be wide enough for '22', so '1' is padded to line up under it
    assert lines[2][:2] == "1 "
    assert lines[3][:2] == "22"


def test_print_entries_table_empty_list(capsys):
    print_entries_table([])
    lines = capsys.readouterr().out.rstrip("\n").split("\n")

    # just header and separator, no data rows
    assert len(lines) == 2
    assert lines[0].startswith("ID")
