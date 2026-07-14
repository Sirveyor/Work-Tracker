use anyhow::Result;
use chrono::{Datelike, Local};
use rusqlite::{params, Connection, Row};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkEntry {
    pub project_number: String,
    pub person: String,
    pub start_time: String,
    pub end_time: String,
    pub description: String,
}

impl WorkEntry {
    pub fn new(
        project_number: String,
        person: String,
        start_time: String,
        end_time: String,
        description: String,
    ) -> Self {
        Self {
            project_number,
            person,
            start_time,
            end_time,
            description,
        }
    }

    pub fn from_row(row: &Row) -> rusqlite::Result<Self> {
        Ok(WorkEntry {
            project_number: row.get(0)?,
            person: row.get(2)?,
            start_time: row.get(3)?,
            end_time: row.get(4)?,
            description: row.get(5)?,
        })
    }
}

pub struct WorkTracker {
    connection: Connection,
}

impl WorkTracker {
    pub fn new() -> Result<Self> {
        let conn = Connection::open("work_tracker.db")?;
        let tracker = Self { connection: conn };
        tracker.create_table()?;
        Ok(tracker)
    }

    fn create_table(&self) -> Result<()> {
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS work_entries (
                project_number TEXT NOT NULL,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                description TEXT NOT NULL
            )",
            [],
        )?;
        Ok(())
    }

    pub fn add_entry(
        &self,
        project_number: &str,
        person: &str,
        start_time: &str,
        end_time: &str,
        description: &str,
    ) -> Result<()> {
        self.connection.execute(
            "INSERT INTO work_entries (project_number, person, start_time, end_time, description)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            params![project_number, person, start_time, end_time, description],
        )?;
        Ok(())
    }

    pub fn get_all_entries(&self) -> Result<Vec<WorkEntry>> {
        let mut stmt = self.connection.prepare("SELECT * FROM work_entries")?;
        let entry_iter = stmt.query_map([], |row| WorkEntry::from_row(row))?;

        let mut entries = Vec::new();
        for entry in entry_iter {
            entries.push(entry?);
        }
        Ok(entries)
    }

    pub fn get_last_entry(&self) -> Result<Option<WorkEntry>> {
        let mut stmt = self
            .connection
            .prepare("SELECT * FROM work_entries ORDER BY id DESC LIMIT 1")?;
        
        let mut entry_iter = stmt.query_map([], |row| WorkEntry::from_row(row))?;
        
        if let Some(entry_result) = entry_iter.next() {
            Ok(Some(entry_result?))
        } else {
            Ok(None)
        }
    }

    pub fn print_current_entry_time_spent(&self) -> Result<()> {
        let mut stmt = self.connection.prepare(
            "SELECT project_number, julianday(end_time), julianday(start_time)
             FROM work_entries ORDER BY id DESC LIMIT 1",
        )?;

        let mut row_iter = stmt.query_map([], |row| {
            let project_number: String = row.get(0)?;
            let end_julian: f64 = row.get(1)?;
            let start_julian: f64 = row.get(2)?;
            Ok((project_number, end_julian, start_julian))
        })?;

        if let Some(result) = row_iter.next() {
            let (project_number, end_julian, start_julian) = result?;
            let hours_worked = (end_julian - start_julian) * 24.0;
            println!("Time spent on Job {}: {:.2} hours", project_number, hours_worked);
        } else {
            println!("No current entry");
        }
        Ok(())
    }

    pub fn get_total_time_spent(&self) -> Result<HashMap<String, f64>> {
        let mut stmt = self.connection.prepare(
            "SELECT project_number, SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
             FROM work_entries
             GROUP BY project_number",
        )?;

        let total_iter = stmt.query_map([], |row| {
            let project: String = row.get(0)?;
            let hours: f64 = row.get(1)?;
            Ok((project, hours))
        })?;

        let mut totals = HashMap::new();
        for total_result in total_iter {
            let (project, hours) = total_result?;
            totals.insert(project, hours);
        }
        Ok(totals)
    }

    pub fn filter_entries_by_date_range(
        &self,
        start_date: Option<&str>,
        end_date: Option<&str>,
        project_number: Option<&str>,
    ) -> Result<Vec<WorkEntry>> {
        let mut query = "SELECT * FROM work_entries WHERE 1=1".to_string();
        let mut params: Vec<String> = Vec::new();

        if let Some(start) = start_date {
            query.push_str(" AND date(start_time) >= ?");
            params.push(start.to_string());
        }

        if let Some(end) = end_date {
            query.push_str(" AND date(start_time) <= ?");
            params.push(end.to_string());
        }

        if let Some(project) = project_number {
            query.push_str(" AND project_number = ?");
            params.push(project.to_string());
        }

        query.push_str(" ORDER BY start_time");

        let mut stmt = self.connection.prepare(&query)?;
        let params_refs: Vec<&dyn rusqlite::ToSql> = params.iter().map(|s| s as &dyn rusqlite::ToSql).collect();
        let entry_iter = stmt.query_map(&params_refs[..], |row| WorkEntry::from_row(row))?;

        let mut entries = Vec::new();
        for entry in entry_iter {
            entries.push(entry?);
        }
        Ok(entries)
    }

    pub fn filter_entries_by_today(&self, project_number: Option<&str>) -> Result<Vec<WorkEntry>> {
        let today = Local::now().format("%Y-%m-%d").to_string();
        self.filter_entries_by_date_range(Some(&today), Some(&today), project_number)
    }

    pub fn filter_entries_by_this_week(&self, project_number: Option<&str>) -> Result<Vec<WorkEntry>> {
        let today = Local::now().date_naive();
        let days_from_monday = today.weekday().num_days_from_monday();
        let monday = today - chrono::Duration::days(days_from_monday as i64);
        let sunday = monday + chrono::Duration::days(6);

        let start_date = monday.format("%Y-%m-%d").to_string();
        let end_date = sunday.format("%Y-%m-%d").to_string();

        self.filter_entries_by_date_range(Some(&start_date), Some(&end_date), project_number)
    }

    pub fn get_total_time_by_date_range(
        &self,
        start_date: Option<&str>,
        end_date: Option<&str>,
        project_number: Option<&str>,
    ) -> Result<HashMap<String, f64>> {
        let mut query = "SELECT project_number, SUM(julianday(end_time) - julianday(start_time)) * 24 AS total_hours
                         FROM work_entries WHERE 1=1".to_string();
        let mut params: Vec<String> = Vec::new();

        if let Some(start) = start_date {
            query.push_str(" AND date(start_time) >= ?");
            params.push(start.to_string());
        }

        if let Some(end) = end_date {
            query.push_str(" AND date(start_time) <= ?");
            params.push(end.to_string());
        }

        if let Some(project) = project_number {
            query.push_str(" AND project_number = ?");
            params.push(project.to_string());
        }

        query.push_str(" GROUP BY project_number");

        let mut stmt = self.connection.prepare(&query)?;
        let params_refs: Vec<&dyn rusqlite::ToSql> = params.iter().map(|s| s as &dyn rusqlite::ToSql).collect();
        let total_iter = stmt.query_map(&params_refs[..], |row| {
            let project: String = row.get(0)?;
            let hours: f64 = row.get(1)?;
            Ok((project, hours))
        })?;

        let mut totals = HashMap::new();
        for total_result in total_iter {
            let (project, hours) = total_result?;
            totals.insert(project, hours);
        }
        Ok(totals)
    }
}