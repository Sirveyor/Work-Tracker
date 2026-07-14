import sqlite3
from datetime import date

import pytest

import database
from work_tracker import WorkEntry, WorkTracker


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    """A WorkTracker backed by a fresh, isolated SQLite file for each test."""
    db_path = tmp_path / "test_work_tracker.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_path))
    return WorkTracker()


def freeze_today(monkeypatch, fixed_today):
    """Make work_tracker.date.today() return a fixed date for the duration of a test."""
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return fixed_today

    monkeypatch.setattr("work_tracker.date", FrozenDate)


def test_add_and_get_all_entries(tracker):
    assert tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:30", "did work") is True

    entries = tracker.get_all_entries()
    assert len(entries) == 1

    entry = entries[0]
    assert isinstance(entry, WorkEntry)
    assert entry.id is not None
    assert entry.project_number == "P1"
    assert entry.person == "Alice"
    assert entry.start_time == "2026-01-05 09:00"
    assert entry.end_time == "2026-01-05 10:30"
    assert entry.description == "did work"


def test_get_last_entry_returns_none_when_empty(tracker):
    assert tracker.get_last_entry() is None


def test_get_last_entry_returns_entry_not_a_list(tracker):
    # Regression test: get_last_entry used to return [WorkEntry] instead of WorkEntry,
    # which made truthiness checks always pass even when the wrapped value was None.
    tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first")
    tracker.add_entry("P2", "Bob", "2026-01-06 09:00", "2026-01-06 10:00", "second")

    last = tracker.get_last_entry()
    assert isinstance(last, WorkEntry)
    assert last.project_number == "P2"


def test_get_entry_by_id(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first")
    entry_id = tracker.get_last_entry().id

    fetched = tracker.get_entry_by_id(entry_id)
    assert fetched.project_number == "P1"

    assert tracker.get_entry_by_id(entry_id + 1000) is None


def test_update_entry(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first")
    entry_id = tracker.get_last_entry().id

    updated = tracker.update_entry(entry_id, "P2", "Bob", "2026-01-05 09:00", "2026-01-05 11:00", "updated")
    assert updated is True

    entry = tracker.get_entry_by_id(entry_id)
    assert entry.project_number == "P2"
    assert entry.person == "Bob"
    assert entry.end_time == "2026-01-05 11:00"
    assert entry.description == "updated"


def test_update_nonexistent_entry_returns_false(tracker):
    assert tracker.update_entry(999, "P", "Q", "2026-01-05 09:00", "2026-01-05 10:00", "x") is False


def test_delete_entry(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "first")
    entry_id = tracker.get_last_entry().id

    assert tracker.delete_entry(entry_id) is True
    assert tracker.get_entry_by_id(entry_id) is None
    assert tracker.delete_entry(entry_id) is False  # already gone


def test_get_total_time_spent(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 11:00", "a")  # 2h
    tracker.add_entry("P1", "Alice", "2026-01-06 09:00", "2026-01-06 10:30", "b")  # 1.5h
    tracker.add_entry("P2", "Bob", "2026-01-05 09:00", "2026-01-05 09:30", "c")  # 0.5h

    totals = tracker.get_total_time_spent()
    assert totals["P1"] == pytest.approx(3.5)
    assert totals["P2"] == pytest.approx(0.5)


def test_filter_entries_by_date_range(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-01 09:00", "2026-01-01 10:00", "in range")
    tracker.add_entry("P1", "Alice", "2026-02-01 09:00", "2026-02-01 10:00", "out of range")

    entries = tracker.filter_entries_by_date_range(start_date="2026-01-01", end_date="2026-01-31")
    assert len(entries) == 1
    assert entries[0].description == "in range"


def test_filter_entries_by_date_range_with_project_filter(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-01 09:00", "2026-01-01 10:00", "p1 entry")
    tracker.add_entry("P2", "Bob", "2026-01-01 09:00", "2026-01-01 10:00", "p2 entry")

    entries = tracker.filter_entries_by_date_range(project_number="P2")
    assert len(entries) == 1
    assert entries[0].project_number == "P2"


def test_filter_entries_by_today(tracker, monkeypatch):
    freeze_today(monkeypatch, date(2026, 6, 15))

    tracker.add_entry("P1", "Alice", "2026-06-15 09:00", "2026-06-15 10:00", "today")
    tracker.add_entry("P1", "Alice", "2026-06-14 09:00", "2026-06-14 10:00", "yesterday")

    entries = tracker.filter_entries_by_today()
    assert len(entries) == 1
    assert entries[0].description == "today"


@pytest.mark.parametrize("fixed_today", [
    date(2026, 1, 1),   # Thursday, start of month - old date.replace(day=...) code crashed here
    date(2026, 1, 31),  # Saturday, end of month - same crash on the sunday side
    date(2026, 3, 2),   # ordinary Monday, for a non-edge sanity check
])
def test_filter_entries_by_this_week_does_not_crash_at_month_boundaries(tracker, monkeypatch, fixed_today):
    freeze_today(monkeypatch, fixed_today)

    # Should not raise ValueError like the old date.replace(day=...) implementation did.
    entries = tracker.filter_entries_by_this_week()
    assert entries == []


def test_filter_entries_by_this_week_includes_only_current_week(tracker, monkeypatch):
    freeze_today(monkeypatch, date(2026, 6, 17))

    tracker.add_entry("P1", "Alice", "2026-06-17 09:00", "2026-06-17 10:00", "this week")
    tracker.add_entry("P1", "Alice", "2026-06-08 09:00", "2026-06-08 10:00", "last week")

    entries = tracker.filter_entries_by_this_week()
    assert len(entries) == 1
    assert entries[0].description == "this week"


def test_get_total_time_by_date_range(tracker):
    tracker.add_entry("P1", "Alice", "2026-01-01 09:00", "2026-01-01 11:00", "a")  # 2h, in range
    tracker.add_entry("P1", "Alice", "2026-02-01 09:00", "2026-02-01 10:00", "b")  # 1h, out of range

    totals = tracker.get_total_time_by_date_range(start_date="2026-01-01", end_date="2026-01-31")
    assert totals["P1"] == pytest.approx(2.0)


def test_db_errors_are_handled_gracefully_instead_of_raising(tracker, monkeypatch):
    def broken_connection():
        raise sqlite3.OperationalError("simulated database is locked")

    monkeypatch.setattr("work_tracker.create_connection", broken_connection)

    assert tracker.add_entry("P1", "Alice", "2026-01-05 09:00", "2026-01-05 10:00", "x") is False
    assert tracker.get_all_entries() == []
    assert tracker.get_last_entry() is None
    assert tracker.get_entry_by_id(1) is None
    assert tracker.update_entry(1, "P", "Q", "2026-01-05 09:00", "2026-01-05 10:00", "d") is False
    assert tracker.delete_entry(1) is False
    assert tracker.get_total_time_spent() == {}
    assert tracker.filter_entries_by_date_range() == []
    assert tracker.get_total_time_by_date_range() == {}
