/// Utility functions for the srv HTTP server.
///
/// This module provides helper functions for logging, network operations,
/// and other miscellaneous tasks.
use std::{fs, path::PathBuf};
use tracing::{info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

/// Set up enhanced logging with proper filtering.
///
/// Configures the tracing subscriber with:
/// - Environment variable-based filter (RUST_LOG)
/// - Fallback to "info" level if not specified
/// - Formatted output with timestamps
pub fn setup_logging() {
    // Create a custom filter
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info,tower_http=debug"));
    
    // Set up the subscriber
    tracing_subscriber::registry()
        .with(filter)
        .with(tracing_subscriber::fmt::layer())
        .init();
    
    info!("Logging initialized");
}

/// Log the contents of the directory for debugging purposes.
///
/// This helps users see what files are being served without
/// having to switch to another terminal to run `ls`.
pub fn log_directory_contents(path: &PathBuf) {
    info!("Directory contents of {}:", path.display());
    match fs::read_dir(path) {
        Ok(entries) => {
            for entry in entries {
                if let Ok(entry) = entry {
                    let file_type = if entry.path().is_dir() { "DIR" } else { "FILE" };
                    info!("  {} - {}", file_type, entry.path().display());
                }
            }
        }
        Err(e) => {
            warn!("Could not read directory contents: {}", e);
        }
    }
}

/// Attempt to find the local IP address for display purposes.
///
/// # Returns
/// A string containing the local IP address or "localhost" if not found
pub fn get_local_ip() -> String {
    info!("Attempting to get local IP address");
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg("ifconfig | grep 'inet ' | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}'")
        .output();
    
    match output {
        Ok(output) if output.status.success() => {
            let ip = String::from_utf8_lossy(&output.stdout).trim().to_string();
            if !ip.is_empty() {
                info!("Found local IP: {}", ip);
                ip
            } else {
                warn!("No local IP found, falling back to localhost");
                "localhost".to_string()
            }
        }
        Ok(_) => {
            warn!("Failed to get local IP, falling back to localhost");
            "localhost".to_string()
        }
        Err(e) => {
            warn!("Error getting local IP: {}, falling back to localhost", e);
            "localhost".to_string()
        }
    }
}

/// Calculate human-readable file size
#[allow(dead_code)]
pub fn human_readable_size(size: u64) -> String {
    const UNITS: [&str; 6] = ["B", "KB", "MB", "GB", "TB", "PB"];
    let mut size = size as f64;
    let mut unit_index = 0;

    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }

    if unit_index == 0 {
        format!("{} {}", size, UNITS[unit_index])
    } else {
        format!("{:.2} {}", size, UNITS[unit_index])
    }
}

/// Get file modification time as ISO 8601 string
#[allow(dead_code)]
pub fn get_modification_time(path: &PathBuf) -> String {
    match fs::metadata(path) {
        Ok(metadata) => {
            match metadata.modified() {
                Ok(time) => {
                    match time.duration_since(std::time::UNIX_EPOCH) {
                        Ok(duration) => {
                            // Simple ISO 8601 format
                            let seconds = duration.as_secs();
                            // We're not using nanos for this simple implementation
                            
                            // Very simple date formatting without dependencies
                            // This could be improved with a proper date-time crate
                            let secs_per_day = 86400;
                            let days_since_epoch = seconds / secs_per_day;
                            let seconds_in_day = seconds % secs_per_day;
                            
                            // 1970-01-01 is day 0
                            // This is very basic and doesn't account for leap years properly
                            let year = 1970 + (days_since_epoch / 365);
                            let day_of_year = days_since_epoch % 365;
                            
                            // Simple month estimation - not perfect but close enough for display
                            let days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
                            let mut month = 0;
                            let mut day = day_of_year;
                            
                            for (i, &days) in days_in_month.iter().enumerate() {
                                if day < days {
                                    month = i + 1;
                                    break;
                                }
                                day -= days;
                            }
                            
                            // If we went through all months, set to December
                            if month == 0 {
                                month = 12;
                                day = 31;
                            }
                            
                            // Add 1 to day since we're 0-indexed
                            day += 1;
                            
                            // Format time
                            let hours = (seconds_in_day / 3600) % 24;
                            let minutes = (seconds_in_day / 60) % 60;
                            let seconds = seconds_in_day % 60;
                            
                            format!("{:04}-{:02}-{:02} {:02}:{:02}:{:02}", 
                                    year, month, day, hours, minutes, seconds)
                        },
                        Err(_) => "Unknown time".to_string(),
                    }
                },
                Err(_) => "Unknown time".to_string(),
            }
        },
        Err(_) => "Unknown time".to_string(),
    }
}
