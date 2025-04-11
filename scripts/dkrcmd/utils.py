"""
Utility functions for the Docker container manager.

This module provides helper functions for Docker operations like:
- Running Docker commands
- Checking container status
- Parsing command outputs
- Handling errors
"""

import os
import subprocess
import sys
from pathlib import Path
from .config import DEV_CONTAINER_PREFIX, get_default_tag

def run_command(cmd, capture_output=True, text=True, check=True):
    """
    Execute a shell command and return its output.
    
    Args:
        cmd: List containing the command and its arguments
        capture_output: Whether to capture and return command output
        text: Whether to return output as text (vs. bytes)
        check: Whether to raise an exception on command failure
        
    Returns:
        Command output as string if capture_output=True, otherwise empty string
    """
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=text, check=check)
        return result.stdout.strip() if capture_output and hasattr(result, 'stdout') and result.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error message: {e.stderr}")
        else:
            print(f"Error: {str(e)}")
        if check:
            sys.exit(1)
        return None

def get_running_containers(exclude_dev=True):
    """
    Get a list of all running containers, optionally excluding dev containers.
    
    Args:
        exclude_dev: Whether to exclude development containers
        
    Returns:
        List of dictionaries with container information (id, name, status, image)
    """
    filter_arg = f"--filter=name=^(?!{DEV_CONTAINER_PREFIX})" if exclude_dev else ""
    
    cmd = ["docker", "ps", filter_arg, "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}"]
    
    # Remove empty elements from cmd (happens if filter_arg is empty)
    cmd = [arg for arg in cmd if arg]
    
    containers_output = run_command(cmd, check=False)
    
    if not containers_output:
        return []
    
    containers = []
    for line in containers_output.strip().split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 4:
                containers.append({
                    "id": parts[0],
                    "name": parts[1],
                    "status": parts[2],
                    "image": parts[3]
                })
    
    return containers

def get_all_containers(exclude_dev=True):
    """
    Get a list of all containers (running and stopped), optionally excluding dev containers.
    
    Args:
        exclude_dev: Whether to exclude development containers
        
    Returns:
        List of dictionaries with container information (id, name, status, image)
    """
    filter_arg = f"--filter=name=^(?!{DEV_CONTAINER_PREFIX})" if exclude_dev else ""
    
    cmd = ["docker", "ps", "-a", filter_arg, "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}"]
    
    # Remove empty elements from cmd (happens if filter_arg is empty)
    cmd = [arg for arg in cmd if arg]
    
    containers_output = run_command(cmd, check=False)
    
    if not containers_output:
        return []
    
    containers = []
    for line in containers_output.strip().split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 4:
                containers.append({
                    "id": parts[0],
                    "name": parts[1],
                    "status": parts[2],
                    "image": parts[3]
                })
    
    return containers

def get_images(exclude_dev=True):
    """
    Get a list of all Docker images, optionally excluding dev images.
    
    Args:
        exclude_dev: Whether to exclude development images
        
    Returns:
        List of dictionaries with image information (id, repository, tag, size)
    """
    # Get all images
    cmd = ["docker", "images", "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Size}}"]
    images_output = run_command(cmd, check=False)
    
    if not images_output:
        return []
    
    images = []
    for line in images_output.strip().split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 4:
                # Skip dev images if requested
                if exclude_dev and DEV_CONTAINER_PREFIX in parts[1]:
                    continue
                
                images.append({
                    "id": parts[0],
                    "repository": parts[1],
                    "tag": parts[2],
                    "size": parts[3]
                })
    
    return images

def get_default_image_name():
    """
    Generate a default image name based on the current directory.
    
    Returns:
        str: Default image name
    """
    return get_default_tag()

def container_exists(container_name):
    """
    Check if a container with the given name exists.
    
    Args:
        container_name: Name of the container to check
        
    Returns:
        Boolean indicating if the container exists
    """
    result = run_command(["docker", "ps", "-a", "-q", "-f", f"name={container_name}"], check=False)
    return bool(result)

def container_running(container_name):
    """
    Check if a container with the given name is running.
    
    Args:
        container_name: Name of the container to check
        
    Returns:
        Boolean indicating if the container is running
    """
    result = run_command(["docker", "ps", "-q", "-f", f"name={container_name}"], check=False)
    return bool(result)

def image_exists(image_name):
    """
    Check if an image with the given name exists.
    
    Args:
        image_name: Name of the image to check
        
    Returns:
        Boolean indicating if the image exists
    """
    result = run_command(["docker", "images", "-q", image_name], check=False)
    return bool(result)

def format_container_info(container):
    """
    Format container information for display.
    
    Args:
        container: Dictionary with container information
        
    Returns:
        str: Formatted string with container details
    """
    return f"{container['id'][:12]} | {container['name']} | {container['status']} | {container['image']}"

def format_image_info(image):
    """
    Format image information for display.
    
    Args:
        image: Dictionary with image information
        
    Returns:
        str: Formatted string with image details
    """
    return f"{image['id'][:12]} | {image['repository']}:{image['tag']} | {image['size']}"
