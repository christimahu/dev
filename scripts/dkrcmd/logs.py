"""
Logs command module for the Docker container manager.

This module handles the 'logs' command which displays container logs.
"""

import os
import sys
import subprocess
from .utils import run_command, get_running_containers, container_exists, container_running

def logs_command(args):
    """
    Display logs from a Docker container.
    
    This command:
    1. If a container name is provided, shows logs for that specific container
    2. If no name is provided, shows a list of containers to choose from
    
    Args:
        args: Command-line arguments containing:
            - name: Optional container name to show logs for
            - follow: Flag to follow log output
            - lines: Number of lines to show (default: 100)
    """
    # If a specific container was requested
    if args.name:
        return show_container_logs(args.name, args.follow, args.lines)
    
    # Otherwise, show list of containers to choose from
    containers = get_running_containers(exclude_dev=True)
    
    # If no running containers, check all containers (including stopped ones)
    if not containers:
        containers = get_all_containers(exclude_dev=True)
        if containers:
            print("No running containers found. Showing stopped containers:")
        else:
            print("No containers found.")
            return True
    
    return interactive_logs(containers, args.follow, args.lines)

def show_container_logs(container_name, follow=False, lines=100):
    """
    Show logs for a specific container by name.
    
    Args:
        container_name: Name of the container to show logs for
        follow: Whether to follow log output
        lines: Number of lines to show
        
    Returns:
        bool: Success or failure
    """
    if not container_exists(container_name):
        print(f"Container '{container_name}' does not exist.")
        return False
    
    # Build log command
    log_cmd = ["docker", "logs"]
    
    # Add options
    if follow:
        log_cmd.append("-f")
    
    log_cmd.extend(["--tail", str(lines)])
    log_cmd.append(container_name)
    
    print(f"Showing logs for container: {container_name}")
    print(f"{'='*40}\n")
    
    # When following logs, we need to handle KeyboardInterrupt
    if follow:
        try:
            # We use subprocess directly here for better handling of streaming output
            subprocess.run(log_cmd)
        except KeyboardInterrupt:
            print("\nStopped following logs. (Keyboard Interrupt)")
    else:
        # For non-follow mode, use our standard run_command
        log_output = run_command(log_cmd, capture_output=True, check=False)
        if log_output:
            print(log_output)
        else:
            print("No logs available for this container.")
    
    print(f"\n{'='*40}")
    return True

def interactive_logs(containers, follow=False, lines=100):
    """
    Interactively show logs by letting the user choose a container from a list.
    
    Args:
        containers: List of container dictionaries
        follow: Whether to follow log output
        lines: Number of lines to show
        
    Returns:
        bool: Success or failure
    """
    print("\nContainers:")
    print(f"{'Option':<8} {'Container ID':<15} {'Name':<25} {'Status':<20} {'Image':<25}")
    print(f"{'-'*8} {'-'*15} {'-'*25} {'-'*20} {'-'*25}")
    
    for i, container in enumerate(containers, 1):
        print(f"{i:<8} {container['id'][:12]:<15} {container['name'][:25]:<25} "
              f"{container['status'][:20]:<20} {container['image'][:25]:<25}")
    
    print(f"{'-'*8} {'-'*15} {'-'*25} {'-'*20} {'-'*25}")
    print("q       Quit without showing logs")
    
    choice = input("\nEnter option (number or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Operation cancelled.")
        return True
    
    # Check if choice is a valid number
    if choice.isdigit() and 1 <= int(choice) <= len(containers):
        container = containers[int(choice) - 1]
        return show_container_logs(container['name'], follow, lines)
    else:
        print("Invalid selection.")
        return False
