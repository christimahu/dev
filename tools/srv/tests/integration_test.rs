use std::process::{Command, Child};
use std::time::Duration;
use std::thread;
use std::fs::{self, File};
use std::io::Write;
use reqwest;
use tempfile::tempdir;

// Helper function to start the srv binary
fn start_srv(port: u16, dir: &str) -> Child {
    let cargo_manifest_dir = env!("CARGO_MANIFEST_DIR");
    let srv_path = format!("{}/target/debug/srv", cargo_manifest_dir);
    
    Command::new(srv_path)
        .arg(port.to_string())
        .arg(dir)
        .spawn()
        .expect("Failed to start srv process")
}

// Helper to wait for the server to be ready
fn wait_for_server(port: u16) -> bool {
    // Try to connect to the server a few times
    for _ in 0..10 {
        thread::sleep(Duration::from_millis(500));
        
        let url = format!("http://localhost:{}", port);
        match reqwest::blocking::get(&url) {
            Ok(_) => return true,
            Err(_) => continue,
        }
    }
    false
}

#[test]
#[ignore] // Ignore by default as this test requires building the binary first
fn test_srv_serves_files() {
    // Create a temporary directory
    let dir = tempdir().expect("Failed to create temporary directory");
    let dir_path = dir.path();
    
    // Create an HTML file
    let html_path = dir_path.join("test.html");
    let html_content = "<html><body>Test Page</body></html>";
    let mut file = File::create(html_path).expect("Failed to create test HTML file");
    file.write_all(html_content.as_bytes()).expect("Failed to write HTML content");
    
    // Start the server
    let port = 9876;
    let mut srv = start_srv(port, dir_path.to_str().unwrap());
    
    // Wait for the server to start
    assert!(wait_for_server(port), "Server failed to start");
    
    // Test that the file is accessible
    let url = format!("http://localhost:{}/test.html", port);
    let response = reqwest::blocking::get(&url).expect("Failed to get file");
    
    assert!(response.status().is_success());
    assert_eq!(response.text().unwrap(), html_content);
    
    // Clean up
    srv.kill().expect("Failed to kill srv process");
}

#[test]
#[ignore] // Ignore by default as this test requires building the binary first
fn test_srv_directory_listing() {
    // Create a temporary directory
    let dir = tempdir().expect("Failed to create temporary directory");
    let dir_path = dir.path();
    
    // Create a subdirectory
    let subdir_path = dir_path.join("subdir");
    fs::create_dir(&subdir_path).expect("Failed to create subdirectory");
    
    // Start the server
    let port = 9877;
    let mut srv = start_srv(port, dir_path.to_str().unwrap());
    
    // Wait for the server to start
    assert!(wait_for_server(port), "Server failed to start");
    
    // Test that the directory listing works
    let url = format!("http://localhost:{}", port);
    let response = reqwest::blocking::get(&url).expect("Failed to get directory listing");
    
    assert!(response.status().is_success());
    
    // The response should contain a link to the subdirectory
    let body = response.text().unwrap();
    assert!(body.contains("subdir"));
    
    // Clean up
    srv.kill().expect("Failed to kill srv process");
}

#[test]
#[ignore] // Ignore by default as this test requires building the binary first
fn test_srv_port_conflict_handling() {
    // Create a temporary directory
    let dir = tempdir().expect("Failed to create temporary directory");
    let dir_path = dir.path();
    
    // Start the server on port 9878
    let port = 9878;
    let mut srv1 = start_srv(port, dir_path.to_str().unwrap());
    
    // Wait for the server to start
    assert!(wait_for_server(port), "First server failed to start");
    
    // Start another server on the same port
    // It should automatically choose a different port
    let mut srv2 = start_srv(port, dir_path.to_str().unwrap());
    
    // The second server should be on port + 1
    assert!(wait_for_server(port + 1), "Second server failed to start on alternate port");
    
    // Clean up
    srv1.kill().expect("Failed to kill first srv process");
    srv2.kill().expect("Failed to kill second srv process");
}
