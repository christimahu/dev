/// A simple HTTP server for serving static files.
///
/// This tool provides a convenient way to serve files from a specified directory
/// over HTTP, with features like configuration file support, automatic port selection,
/// enhanced content type detection, and detailed logging.
mod config;
mod server;
mod utils;

use std::process;
use tracing::{info, error};

/// Main entry point for the server application.
///
/// This async function drives the entire application lifecycle:
/// 1. Sets up logging configuration
/// 2. Loads configuration from config file and/or command line args
/// 3. Starts the server with the provided configuration
#[tokio::main]
async fn main() {
    // Initialize enhanced logging system
    utils::setup_logging();
    
    // Parse command-line arguments and load config
    let config = match config::load_config() {
        Ok(config) => config,
        Err(e) => {
            error!("Configuration error: {}", e);
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    };
    
    // Log configuration
    info!("Configuration loaded: serving {} on port {}", config.directory.display(), config.port);
    
    // Start the server
    if let Err(e) = server::run_server(config).await {
        error!("Server error: {}", e);
        eprintln!("Server error: {}", e);
        process::exit(1);
    }

    info!("Server shutdown complete");
}
