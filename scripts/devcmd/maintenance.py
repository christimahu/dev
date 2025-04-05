"""
Maintenance commands for the development environment.

This module provides functions for maintaining and cleaning up Docker resources:
- prune: Clean up unused Docker resources (general cleanup)
- prune_images: Remove only dev-related Docker images
- update_srv_function: Helper for updating the srv function paths

Tutorial:
---------
These functions handle maintenance tasks for keeping the Docker environment
clean and organized. They provide targeted cleanup operations to remove
unused containers, images, and other resources.

Examples:
---------
1. General cleanup of unused resources:
   ```
   dev prune  # Removes unused containers and dangling images
   ```

2. Cleanup of development images:
   ```
   dev prune-images  # Shows menu to select which dev images to remove
   ```
"""

import os
import subprocess
from .config import DEV_DIR, IMAGE_NAME


def prune_command(args):
    """
    Clean up unused Docker resources.
    
    Removes unused containers, networks, and images to free up disk space
    and keep your Docker environment clean.
    
    Args:
        args: Command-line arguments with options:
            - all: Remove all unused resources (including non-dev containers)
            - volumes: Also remove volumes
    
    Tutorial:
    ---------
    This command helps keep your Docker environment clean by removing
    unused resources. It's similar to running `docker system prune`
    but with more control over what gets removed.
    
    Examples:
        dev prune                  # Remove unused containers and dangling images
        dev prune --all            # Remove all unused resources
        dev prune --all --volumes  # Also remove unused volumes
    """
    print("Cleaning up unused Docker resources...")
    
    if args.all:
        print("WARNING: This will remove all unused containers, networks, images, and volumes.")
        confirm = input("Are you sure you want to continue? [y/N]: ")
        
        if confirm.lower() == 'y':
            subprocess.run(["docker", "container", "prune", "-f"])
            subprocess.run(["docker", "network", "prune", "-f"])
            subprocess.run(["docker", "image", "prune", "-a", "-f"])
            if args.volumes:
                subprocess.run(["docker", "volume", "prune", "-f"])
        else:
            print("Prune operation canceled.")
    else:
        subprocess.run(["docker", "container", "prune", "-f"])
        subprocess.run(["docker", "image", "prune", "-f"])


def prune_images_command(args):
    """
    Remove development environment Docker images.
    
    This command helps keep your Docker environment clean by removing
    only development environment images created by this tool.
    
    Args:
        args: Command-line arguments with options:
            - force: Force removal without confirmation
    
    Tutorial:
    ---------
    Use this command when you want to remove old or unused development
    images. It shows a menu of available images and lets you choose
    which ones to remove. Unlike regular Docker commands, it only
    targets images created by the development environment.
    
    Examples:
        dev prune-images           # Show menu of images to remove
        dev prune-images --force   # Remove all dev images without confirmation
    """
    # Get list of dev environment images
    image_list = run_command_with_output([
        "docker", "images", 
        "--filter", f"reference={IMAGE_NAME}*", 
        "--format", "{{.ID}}|{{.Repository}}:{{.Tag}}|{{.Size}}"
    ])
    
    if not image_list:
        print("No development environment images found.")
        return
    
    # Display images
    print("\nDevelopment environment images:")
    print("=" * 70)
    print(f"{'Option':<8} {'Image ID':<15} {'Repository:Tag':<35} {'Size':<15}")
    print("-" * 70)
    
    images = []
    for i, image_info in enumerate(image_list, 1):
        parts = image_info.split("|")
        if len(parts) >= 3:
            image_id = parts[0]
            repo_tag = parts[1]
            size = parts[2]
            
            images.append({
                "id": image_id,
                "repo_tag": repo_tag,
                "size": size
            })
            
            print(f"{i:<8} {image_id[:12]:<15} {repo_tag:<35} {size:<15}")
    
    print("-" * 70)
    print("a       Remove all development images")
    print("q       Quit without removing any images")
    print("=" * 70)
    
    if args.force:
        choice = "a"  # Auto-select all images in force mode
    else:
        choice = input("Enter option (number, 'a' for all, or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Operation cancelled.")
        return
    elif choice == 'a':
        # Remove all images
        print("Removing all development environment images...")
        for image in images:
            print(f"Removing {image['repo_tag']} ({image['id'][:12]})...")
            subprocess.run(["docker", "rmi", "-f", image['id']])
        print("All development environment images removed.")
    elif choice.isdigit() and 1 <= int(choice) <= len(images):
        # Remove selected image
        image = images[int(choice) - 1]
        print(f"Removing {image['repo_tag']} ({image['id'][:12]})...")
        subprocess.run(["docker", "rmi", "-f", image['id']])
        print("Image removed.")
    else:
        print("Invalid selection. No images removed.")


def run_command_with_output(cmd):
    """
    Run a command and return its output as a list of lines.
    
    Args:
        cmd: Command to execute as a list of strings
        
    Returns:
        List of output lines or empty list if command fails
    
    Tutorial:
    ---------
    This is a helper function for safely running commands and 
    processing their output. It handles errors gracefully and
    returns the output in a convenient format.
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            return [line for line in result.stdout.strip().split('\n') if line.strip()]
        return []
    except subprocess.CalledProcessError:
        return []


def update_srv_function():
    """
    Update the srv function to use .dev instead of dev.
    
    This function fixes paths in the shell_functions file,
    ensuring they point to the correct locations.
    
    Tutorial:
    ---------
    This is a maintenance function used during installation and updates.
    It updates path references in shell scripts to ensure they point to
    the correct location (~/.dev instead of ~/dev).
    """
    shell_functions_path = os.path.join(DEV_DIR, "config", "shell_functions")
    
    if os.path.exists(shell_functions_path):
        with open(shell_functions_path, 'r') as f:
            content = f.read()
        
        # Update paths from ~/dev to ~/.dev
        updated_content = content.replace("$HOME/dev/", "$HOME/.dev/")
        updated_content = updated_content.replace("~/dev/", "~/.dev/")
        
        with open(shell_functions_path, 'w') as f:
            f.write(updated_content)
        
        print("Updated shell_functions with correct .dev paths")
