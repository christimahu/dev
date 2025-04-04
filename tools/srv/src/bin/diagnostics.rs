/// A simple diagnostic tool for the srv server
/// 
/// This can be run separately to test if the server is working
/// and check for port and networking issues.
use std::process::Command;
use std::net::{TcpStream, SocketAddr};
use std::time::Duration;
use std::thread;
use std::str::FromStr;

fn main() {
    println!("=== srv Diagnostic Tool ===");
    
    // Check if srv is running
    println!("\nChecking if a server is running on port 8000...");
    match TcpStream::connect("127.0.0.1:8000") {
        Ok(_) => println!("✅ Found server on localhost:8000"),
        Err(e) => println!("❌ No server on localhost:8000: {}", e),
    }
    
    println!("\nChecking if a server is running on 0.0.0.0:8000...");
    match TcpStream::connect("0.0.0.0:8000") {
        Ok(_) => println!("✅ Found server on 0.0.0.0:8000"),
        Err(e) => println!("❌ No server on 0.0.0.0:8000: {}", e),
    }
    
    // Check for other processes using port 8000
    println!("\nChecking for processes using port 8000...");
    let output = Command::new("sh")
        .arg("-c")
        .arg("lsof -i :8000 || netstat -tuln | grep 8000")
        .output();
    
    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            
            if !stdout.is_empty() {
                println!("Processes using port 8000:\n{}", stdout);
            } else if !stderr.is_empty() && !stderr.contains("command not found") {
                println!("Error checking processes: {}", stderr);
            } else {
                println!("No processes found using port 8000");
            }
        },
        Err(e) => println!("Error running process check: {}", e),
    }
    
    // Check networking setup
    println!("\nNetwork interfaces:");
    let output = Command::new("sh")
        .arg("-c")
        .arg("ip addr || ifconfig")
        .output();
    
    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            if !stdout.is_empty() {
                println!("{}", stdout);
            } else {
                println!("No network interface information available");
            }
        },
        Err(e) => println!("Error checking network interfaces: {}", e),
    }
    
    // Try to start a simple test server on 8001 and connect to it
    println!("\nTesting basic TCP server functionality...");
    let test_port = 8001;
    
    // Spawn a thread to run a simple socket server
    let server_thread = thread::spawn(move || {
        // Try to bind to all interfaces
        let addr = SocketAddr::from_str(&format!("0.0.0.0:{}", test_port)).unwrap();
        match std::net::TcpListener::bind(addr) {
            Ok(listener) => {
                println!("✅ Test server started on port {}", test_port);
                println!("Waiting for a connection...");
                
                // Accept one connection
                match listener.accept() {
                    Ok((_, addr)) => println!("✅ Received connection from {}", addr),
                    Err(e) => println!("❌ Error accepting connection: {}", e),
                }
            },
            Err(e) => println!("❌ Could not start test server on port {}: {}", test_port, e),
        }
    });
    
    // Give server time to start
    thread::sleep(Duration::from_millis(200));
    
    // Connect to our test server
    println!("Trying to connect to test server...");
    match TcpStream::connect(format!("127.0.0.1:{}", test_port)) {
        Ok(_) => println!("✅ Successfully connected to test server"),
        Err(e) => println!("❌ Failed to connect to test server: {}", e),
    }
    
    // Wait for server thread to finish
    let _ = server_thread.join();
    
    println!("\n=== Diagnostic Complete ===");
}
