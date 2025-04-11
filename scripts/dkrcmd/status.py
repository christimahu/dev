"""
Status command module for the Docker container manager.

This module handles the 'status' command which displays information about 
running containers, excluding development containers.
"""

import os
import sys
from .utils import get_running_containers, get_all_containers, get_images, format_container_info, format_image_info

def status_command(args):
    """
    Display the status of all Docker containers (excluding dev containers).
    
    This command shows:
    1. Running containers
    2. Stopped containers
    3. Available images
    
    Args:
        args: Command-line arguments (not used in this command)
    """
    # Get running containers (excluding dev containers)
    running_containers = get_running_containers(exclude_dev=True)
    
    # Get all containers (including stopped ones)
    all_containers = get_all_containers(exclude_dev=True)
    
    # Get available images
    images = get_images(exclude_dev=True)
    
    # Get stopped containers by finding those in all_containers but not in running_containers
    running_ids = {c['id'] for c in running_containers}
    stopped_containers = [c for c in all_containers if c['id'] not in running_ids]
    
    # Display results
    print("\n=== Docker Container Status ===")
    
    # Running containers
    print("\nRunning Containers:")
    if running_containers:
        print(f"{'CONTAINER ID':<15} {'NAME':<25} {'STATUS':<20} {'IMAGE':<25}")
        print(f"{'-'*15} {'-'*25} {'-'*20} {'-'*25}")
        
        for container in running_containers:
            print(f"{container['id'][:12]:<15} {container['name'][:25]:<25} {container['status'][:20]:<20} {container['image'][:25]:<25}")
    else:
        print("No running containers")
    
    # Stopped containers
    print("\nStopped Containers:")
    if stopped_containers:
        print(f"{'CONTAINER ID':<15} {'NAME':<25} {'STATUS':<20} {'IMAGE':<25}")
        print(f"{'-'*15} {'-'*25} {'-'*20} {'-'*25}")
        
        for container in stopped_containers:
            print(f"{container['id'][:12]:<15} {container['name'][:25]:<25} {container['status'][:20]:<20} {container['image'][:25]:<25}")
    else:
        print("No stopped containers")
    
    # Images
    print("\nAvailable Images:")
    if images:
        print(f"{'IMAGE ID':<15} {'REPOSITORY:TAG':<50} {'SIZE':<15}")
        print(f"{'-'*15} {'-'*50} {'-'*15}")
        
        for image in images:
            repo_tag = f"{image['repository']}:{image['tag']}"
            print(f"{image['id'][:12]:<15} {repo_tag[:50]:<50} {image['size']:<15}")
    else:
        print("No images found")
    
    # Help information
    print("\nCommands:")
    print("  Start a container:    dkr run [--image <name>] [--port <p>]")
    print("  Stop a container:     dkr stop --name <name>")
    print("  Remove a container:   dkr rm --name <name>")
    print("  Remove an image:      dkr rmi --name <name>")
    print("  View container logs:  dkr logs --name <name>")
    print()
    
    return True
