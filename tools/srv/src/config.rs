/// Configuration handling for the srv HTTP server.
///
/// This module provides functionality for loading and validating
/// server configuration from command-line arguments and config files.
use std::{env, fs, path::{Path, PathBuf}, io, error::Error};
use serde::{Deserialize, Serialize};
use tracing::{info, warn};

/// Server configuration options
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ServerConfig {
    /// Port to listen on
    pub port: u16,
    
    /// Directory to serve files from
    #[serde(skip)]
    pub directory: PathBuf,
    
    /// Directory path as string for serialization
    #[serde(rename = "directory")]
    pub directory_str: String,
    
    /// Whether to enable CORS
    #[serde(default = "default_cors")]
    pub enable_cors: bool,
    
    /// Whether to show hidden files in directory listings
    #[serde(default)]
    pub show_hidden: bool,
    
    /// Whether to follow symlinks
    #[serde(default = "default_true")]
    pub follow_symlinks: bool,
    
    /// Default index file
    #[serde(default = "default_index")]
    pub index_file: String,
    
    /// Maximum number of port attempts when binding
    #[serde(default = "default_port_attempts")]
    pub max_port_attempts: u8,
}

fn default_cors() -> bool { true }
fn default_true() -> bool { true }
fn default_index() -> String { "index.html".to_string() }
fn default_port_attempts() -> u8 { 10 }

impl Default for ServerConfig {
    fn default() -> Self {
        let dir = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        Self {
            port: 8000,
            directory_str: ".".to_string(),
            directory: dir,
            enable_cors: true,
            show_hidden: false,
            follow_symlinks: true,
            index_file: "index.html".to_string(),
            max_port_attempts: 10,
        }
    }
}

impl ServerConfig {
    /// Create a new config with specified port and directory
    pub fn new(port: u16, directory: &str) -> Self {
        let dir_path = PathBuf::from(directory);
        Self {
            port,
            directory_str: directory.to_string(),
            directory: dir_path,
            ..Default::default()
        }
    }
    
    /// Resolve and validate the directory path
    pub fn resolve_directory(&mut self) -> Result<(), Box<dyn Error>> {
        let dir_path = PathBuf::from(&self.directory_str);
        self.directory = if dir_path.is_absolute() {
            dir_path.clone()
        } else {
            match env::current_dir() {
                Ok(current) => current.join(&dir_path),
                Err(e) => return Err(format!("Failed to get current directory: {}", e).into()),
            }
        };
        
        // Verify directory exists
        if !self.directory.exists() {
            return Err(format!("Directory does not exist: {}", self.directory.display()).into());
        }
        
        if !self.directory.is_dir() {
            return Err(format!("Path is not a directory: {}", self.directory.display()).into());
        }
        
        Ok(())
    }
}

/// Path to the default config file
const CONFIG_FILE: &str = ".srv.toml";

/// Load configuration from command-line args and config file
pub fn load_config() -> Result<ServerConfig, Box<dyn Error>> {
    // First try to parse command-line arguments
    let args: Vec<String> = env::args().collect();
    let (port, dir) = parse_arguments(&args);
    
    // Create base config from command-line args
    let mut config = ServerConfig::new(port, &dir);
    
    // Try to load from config file
    if let Some(file_config) = load_config_file(&config.directory) {
        // Merge file config with command-line args, with command-line taking precedence
        merge_configs(&mut config, file_config);
    }
    
    // Resolve and validate the directory
    config.resolve_directory()?;
    
    Ok(config)
}

/// Parse command line arguments for port and directory
fn parse_arguments(args: &[String]) -> (u16, String) {
    // Default values
    let default_port = 8000;
    let default_dir = ".".to_string();
    
    if args.len() <= 1 {
        // No arguments provided
        return (default_port, default_dir);
    }
    
    // Check if first argument is a directory or a port
    let first_arg = &args[1];
    if let Ok(port) = first_arg.parse::<u16>() {
        // First arg is a port
        let dir = if args.len() > 2 { args[2].clone() } else { default_dir };
        return (port, dir);
    } else {
        // First arg is a directory
        return (default_port, first_arg.clone());
    }
}

/// Load configuration from a config file in the specified directory
fn load_config_file(directory: &Path) -> Option<ServerConfig> {
    // Check for config file in specified directory
    let config_path = directory.join(CONFIG_FILE);
    
    if config_path.exists() {
        match fs::read_to_string(&config_path) {
            Ok(content) => {
                match toml::from_str::<ServerConfig>(&content) {
                    Ok(mut config) => {
                        info!("Loaded configuration from {}", config_path.display());
                        
                        // Set directory to the config file's directory if it's not absolute
                        let dir_path = PathBuf::from(&config.directory_str);
                        if !dir_path.is_absolute() {
                            // Use the directory where the config file is located
                            if let Some(parent) = config_path.parent() {
                                config.directory = parent.join(dir_path);
                            }
                        } else {
                            config.directory = dir_path;
                        }
                        
                        return Some(config);
                    },
                    Err(e) => {
                        warn!("Failed to parse config file {}: {}", config_path.display(), e);
                    }
                }
            },
            Err(e) if e.kind() != io::ErrorKind::NotFound => {
                warn!("Failed to read config file {}: {}", config_path.display(), e);
            },
            _ => {}
        }
    }
    
    None
}

/// Merge configurations, with command-line args taking precedence
fn merge_configs(cmd_config: &mut ServerConfig, file_config: ServerConfig) {
    // Only override port if it wasn't explicitly set via command line
    let args: Vec<String> = env::args().collect();
    let was_port_specified = args.len() > 1 && args[1].parse::<u16>().is_ok();
    
    if !was_port_specified {
        cmd_config.port = file_config.port;
    }
    
    // Copy other settings
    cmd_config.enable_cors = file_config.enable_cors;
    cmd_config.show_hidden = file_config.show_hidden;
    cmd_config.follow_symlinks = file_config.follow_symlinks;
    cmd_config.index_file = file_config.index_file;
    cmd_config.max_port_attempts = file_config.max_port_attempts;
}

/// Save current configuration to a file
#[allow(dead_code)]
pub fn save_config(config: &ServerConfig, directory: &Path) -> Result<(), Box<dyn Error>> {
    let config_path = directory.join(CONFIG_FILE);
    let config_str = toml::to_string_pretty(config)?;
    fs::write(&config_path, config_str)?;
    info!("Configuration saved to {}", config_path.display());
    Ok(())
}
