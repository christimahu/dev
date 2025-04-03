use axum::Router;
use std::{env, fs, net::SocketAddr, path::PathBuf, time::Instant};
use tower_http::{
    cors::CorsLayer,
    services::ServeDir,
    trace::{DefaultMakeSpan, DefaultOnRequest, DefaultOnResponse, TraceLayer},
};
use tracing::{info, error, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

#[tokio::main]
async fn main() {
    // Setup enhanced logging
    setup_logging();
    
    // Get command line arguments
    let args: Vec<String> = env::args().collect();
    
    // Parse arguments more carefully
    let (port, dir) = parse_arguments(&args);
    
    // Convert to absolute path and verify it exists
    let dir_path = PathBuf::from(&dir);
    let abs_path = if dir_path.is_absolute() {
        dir_path.clone()
    } else {
        match std::env::current_dir() {
            Ok(current) => current.join(&dir_path),
            Err(e) => {
                error!("Failed to get current directory: {}", e);
                eprintln!("Error: Failed to get current directory: {}", e);
                std::process::exit(1);
            }
        }
    };
    
    // Verify directory exists
    if !abs_path.exists() {
        error!("Directory does not exist: {}", abs_path.display());
        eprintln!("Error: Directory does not exist: {}", abs_path.display());
        std::process::exit(1);
    }
    
    if !abs_path.is_dir() {
        error!("Path is not a directory: {}", abs_path.display());
        eprintln!("Error: Path is not a directory: {}", abs_path.display());
        std::process::exit(1);
    }
    
    // Log directory contents for debugging
    info!("Directory contents of {}:", abs_path.display());
    match fs::read_dir(&abs_path) {
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
    
    // Get local IP for display
    let local_ip = get_local_ip();
    
    // Create router with static file service and detailed logging
    let serve_dir = ServeDir::new(&dir)
        .append_index_html_on_directories(true);
    
    let app = Router::new()
        .fallback_service(serve_dir)
        .layer(
            TraceLayer::new_for_http()
                .make_span_with(DefaultMakeSpan::default().include_headers(true))
                .on_request(DefaultOnRequest::new().level(tracing::Level::INFO))
                .on_response(DefaultOnResponse::new().level(tracing::Level::INFO))
        )
        .layer(CorsLayer::permissive());
    
    // Bind to all interfaces
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    
    // Print server information
    println!("\n=================================================================");
    println!("📂 Serving files from: {}", abs_path.display());
    println!("🌐 Local URL: http://localhost:{}", port);
    println!("🔗 Network URL: http://{}:{}", local_ip, port);
    println!("=================================================================\n");
    
    // Start the server with more robust error handling
    info!("Starting server on {}", addr);
    
    // Fixed version for axum 0.6.18
    match tokio::net::TcpListener::bind(addr).await {
        Ok(listener) => {
            println!("Server started successfully! Press Ctrl+C to stop.");
            
            // Set up periodic status reports
            let start_time = Instant::now();
            let _status_task = tokio::spawn(async move {
                loop {
                    tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
                    let uptime = Instant::now().duration_since(start_time);
                    info!("Server status: Running for {:?}", uptime);
                }
            });
            
            // Use axum::Server instead of axum::serve which doesn't exist in 0.6.18
            match axum::Server::bind(&addr)
                .serve(app.into_make_service())
                .await 
            {
                Ok(_) => {
                    info!("Server shut down gracefully");
                    println!("Server shut down gracefully");
                }
                Err(e) => {
                    error!("Server error: {}", e);
                    eprintln!("Server error: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Err(e) => {
            error!("Failed to bind to address {}: {}", addr, e);
            eprintln!("Error: Failed to bind to address {}: {}", addr, e);
            std::process::exit(1);
        }
    }
}

// Parse command line arguments more carefully
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

// Function to get local IP
fn get_local_ip() -> String {
    info!("Attempting to get local IP address");
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg("ifconfig | grep 'inet ' | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}'")
        .output();
    
    match output {
        Ok(output) if output.status.success() => {
            let ip = String::from_utf8_lossy(&output.stdout).trim().to_string();
            info!("Found local IP: {}", ip);
            ip
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

// Set up enhanced logging
fn setup_logging() {
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
