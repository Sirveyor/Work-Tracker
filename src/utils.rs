use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize)]
struct LastPersonData {
    last_person: String,
}

pub fn load_last_person() -> Result<String> {
    let data_dir = "data";
    if !Path::new(data_dir).exists() {
        fs::create_dir_all(data_dir)?;
    }

    let json_file_path = Path::new(data_dir).join("last_person.json");

    if json_file_path.exists() {
        let content = fs::read_to_string(&json_file_path)?;
        let data: LastPersonData = serde_json::from_str(&content)?;
        Ok(data.last_person)
    } else {
        Ok(String::new())
    }
}

pub fn save_last_person(person: &str) -> Result<()> {
    let data_dir = "data";
    if !Path::new(data_dir).exists() {
        fs::create_dir_all(data_dir)?;
    }

    let json_file_path = Path::new(data_dir).join("last_person.json");
    let data = LastPersonData {
        last_person: person.to_string(),
    };

    let content = serde_json::to_string_pretty(&data)?;
    fs::write(&json_file_path, content)?;
    Ok(())
}