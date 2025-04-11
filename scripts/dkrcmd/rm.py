"""
Remove command module for the Docker container manager.

This module handles the 'rm' command which removes Docker containers.
"""

import os
import sys
from .utils import run_command, get_all_containers, container_exists, container_running

def rm_command(args):
    """
    Remove Docker containers.
    
    This command:
    1. If a container name is provided, removes that specific container
    2. If --all flag is used, removes all containers
    3. If no name is provided, shows a list of containers to choose from
    
    Args:
        args: Command-line arguments containing:
            - name: Optional container name to remove
            - all: Flag to remove all containers
    """
    # Remove all containers if --all flag is used
    if args.all:
        return remove_all_containers()
    
    # Remove specific container if name is provided
    if args.name:
        return remove_specific_container(args.name)
    
    # Interactive mode if no specific container or --all flag
    containers = get_all_containers(exclude_dev=True)
    
    if not containers:
        print("No containers found.")
        return True
    
    return interactive_remove(containers)

def remove_specific_container(container_name):
    """
    Remove a specific container by name.
    
    Args:
        container_name: Name of the container to remove
        
    Returns:
        bool: Success or failure
    """
    if not container_exists(container_name):
        print(f"Container '{container_name}' does not exist.")
        return False
    
    # Stop the container first if it's running
    if container_running(container_name):
        print(f"Container '{container_name}' is running. Stopping it first.")
        run_command(["docker", "stop", container_name], check=False)
    
    print(f"Removing container: {container_name}")
    result = run_command(["docker", "rm", container_name], check=False)
    
    if result is not None:
        print(f"Container '{container_name}' removed successfully.")
        return True
    else:
        print(f"Failed to remove container '{container_name}'.")
        return False

def remove_all_containers():
    """
    Remove all containers (except dev containers).
    
    Returns:
        bool: Success or failure
    """
    containers = get_all_containers(exclude_dev=True)
    
    if not containers:
        print("No containers to remove.")
        return True
    
    print(f"Removing {len(containers)} containers...")
    
    success_count = 0
    for container in containers:
        # Stop if running
        if "Up " in container['status']:
            print(f"Stopping container: {container['name']} ({container['id'][:12]})")
            run_command(["docker", "stop", container['id']], check=False)
        
        # Remove container
        print(f"Removing container: {container['name']} ({container['id'][:12]})")
        result = run_command(["docker", "rm", container['id']], check=False)
        if result is not None:
            success_count += 1
    
    print(f"Removed {success_count} of {len(containers)} containers.")
    return success_count > 0

def interactive_remove(containers):
    """
    Interactively remove containers by letting the user choose from a list.
    
    Args:
        containers: List of container dictionaries
        
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
    print("a       Remove all containers")
    print("q       Quit without removing any container")
    
    choice = input("\nEnter option (number, 'a' for all, or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Operation cancelled.")
        return True
    
    if choice == 'a':
        return remove_all_containers()
    
    # Check if choice is a valid number
    if choice.isdigit() and 1 <= int(choice) <= len(containers):
        container = containers[int(choice) - 1]
        
        # Stop if running
        if "Up " in container['status']:
            print(f"Container is running. Stopping it first.")
            run_command(["docker", "stop", container['id']], check=False)
        
        print(f"Removing container: {container['name']} ({container['id'][:12]})")
        result = run_command(["docker", "rm", container['id']], check=False)
        
        if result is not None:
            print(f"Container '{container['name']}' removed successfully.")
            return True
        else:
            print(f"Failed to remove container '{container['name']}'.")
            return False
    else:
        print("Invalid selection.")
        return False
