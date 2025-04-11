"""
Stop command module for the Docker container manager.

This module handles the 'stop' command which stops running containers.
"""

import os
import sys
from .utils import run_command, get_running_containers, container_running

def stop_command(args):
    """
    Stop running Docker containers.
    
    This command:
    1. If a container name is provided, stops that specific container
    2. If no name is provided, shows a list of running containers to choose from
    
    Args:
        args: Command-line arguments containing:
            - name: Optional container name to stop
    """
    # If a specific container was requested
    if args.name:
        return stop_specific_container(args.name)
    
    # Otherwise, show list of running containers
    running_containers = get_running_containers(exclude_dev=True)
    
    if not running_containers:
        print("No running containers found.")
        return True
    
    return interactive_stop(running_containers)

def stop_specific_container(container_name):
    """
    Stop a specific container by name.
    
    Args:
        container_name: Name of the container to stop
        
    Returns:
        bool: Success or failure
    """
    if not container_running(container_name):
        print(f"Container '{container_name}' is not running.")
        return False
    
    print(f"Stopping container: {container_name}")
    result = run_command(["docker", "stop", container_name], check=False)
    
    if result is not None:
        print(f"Container '{container_name}' stopped successfully.")
        return True
    else:
        print(f"Failed to stop container '{container_name}'.")
        return False

def interactive_stop(containers):
    """
    Interactively stop containers by letting the user choose from a list.
    
    Args:
        containers: List of container dictionaries
        
    Returns:
        bool: Success or failure
    """
    print("\nRunning containers:")
    print(f"{'Option':<8} {'Container ID':<15} {'Name':<25} {'Status':<20} {'Image':<25}")
    print(f"{'-'*8} {'-'*15} {'-'*25} {'-'*20} {'-'*25}")
    
    for i, container in enumerate(containers, 1):
        print(f"{i:<8} {container['id'][:12]:<15} {container['name'][:25]:<25} "
              f"{container['status'][:20]:<20} {container['image'][:25]:<25}")
    
    print(f"{'-'*8} {'-'*15} {'-'*25} {'-'*20} {'-'*25}")
    print("a       Stop all containers")
    print("q       Quit without stopping any container")
    
    choice = input("\nEnter option (number, 'a' for all, or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Operation cancelled.")
        return True
    
    if choice == 'a':
        # Stop all containers
        success_count = 0
        for container in containers:
            print(f"Stopping container: {container['name']} ({container['id'][:12]})")
            result = run_command(["docker", "stop", container['id']], check=False)
            if result is not None:
                success_count += 1
        
        print(f"Stopped {success_count} of {len(containers)} containers.")
        return success_count > 0
    
    # Check if choice is a valid number
    if choice.isdigit() and 1 <= int(choice) <= len(containers):
        container = containers[int(choice) - 1]
        print(f"Stopping container: {container['name']} ({container['id'][:12]})")
        result = run_command(["docker", "stop", container['id']], check=False)
        
        if result is not None:
            print(f"Container '{container['name']}' stopped successfully.")
            return True
        else:
            print(f"Failed to stop container '{container['name']}'.")
            return False
    else:
        print("Invalid selection.")
        return False
