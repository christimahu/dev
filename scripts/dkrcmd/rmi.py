"""
Remove Image command module for the Docker container manager.

This module handles the 'rmi' command which removes Docker images.
"""

import os
import sys
from .utils import run_command, get_images, image_exists

def rmi_command(args):
    """
    Remove Docker images.
    
    This command:
    1. If an image name is provided, removes that specific image
    2. If --all flag is used, removes all non-dev images
    3. If no name is provided, shows a list of images to choose from
    
    Args:
        args: Command-line arguments containing:
            - name: Optional image name to remove
            - all: Flag to remove all images
    """
    # Remove all images if --all flag is used
    if args.all:
        return remove_all_images()
    
    # Remove specific image if name is provided
    if args.name:
        return remove_specific_image(args.name)
    
    # Interactive mode if no specific image or --all flag
    images = get_images(exclude_dev=True)
    
    if not images:
        print("No images found.")
        return True
    
    return interactive_remove(images)

def remove_specific_image(image_name):
    """
    Remove a specific image by name.
    
    Args:
        image_name: Name of the image to remove
        
    Returns:
        bool: Success or failure
    """
    if not image_exists(image_name):
        print(f"Image '{image_name}' does not exist.")
        return False
    
    print(f"Removing image: {image_name}")
    result = run_command(["docker", "rmi", image_name], check=False)
    
    if result is not None:
        print(f"Image '{image_name}' removed successfully.")
        return True
    else:
        print(f"Failed to remove image '{image_name}'.")
        print("It may be in use by a container. Try removing the container first with 'dkr rm'.")
        
        # Try with force flag if user wants
        response = input("Do you want to force remove this image? [y/N]: ").strip().lower()
        if response == 'y' or response == 'yes':
            print(f"Force removing image: {image_name}")
            result = run_command(["docker", "rmi", "-f", image_name], check=False)
            
            if result is not None:
                print(f"Image '{image_name}' force removed successfully.")
                return True
        
        return False

def remove_all_images():
    """
    Remove all images (except dev images).
    
    Returns:
        bool: Success or failure
    """
    images = get_images(exclude_dev=True)
    
    if not images:
        print("No images to remove.")
        return True
    
    print(f"Removing {len(images)} images...")
    
    success_count = 0
    for image in images:
        image_tag = f"{image['repository']}:{image['tag']}"
        print(f"Removing image: {image_tag} ({image['id'][:12]})")
        result = run_command(["docker", "rmi", image['id']], check=False)
        if result is not None:
            success_count += 1
    
    print(f"Removed {success_count} of {len(images)} images.")
    if success_count < len(images):
        print("Some images may be in use by containers.")
        print("Remove the containers first with 'dkr rm --all'.")
        
        # Try with force flag if user wants
        response = input("Do you want to force remove all remaining images? [y/N]: ").strip().lower()
        if response == 'y' or response == 'yes':
            # Get remaining images
            remaining_images = get_images(exclude_dev=True)
            if remaining_images:
                force_count = 0
                print(f"Force removing {len(remaining_images)} images...")
                for image in remaining_images:
                    image_tag = f"{image['repository']}:{image['tag']}"
                    print(f"Force removing image: {image_tag} ({image['id'][:12]})")
                    result = run_command(["docker", "rmi", "-f", image['id']], check=False)
                    if result is not None:
                        force_count += 1
                
                print(f"Force removed {force_count} more images.")
                success_count += force_count
    
    return success_count > 0

def interactive_remove(images):
    """
    Interactively remove images by letting the user choose from a list.
    
    Args:
        images: List of image dictionaries
        
    Returns:
        bool: Success or failure
    """
    print("\nImages:")
    print(f"{'Option':<8} {'Image ID':<15} {'Repository:Tag':<50} {'Size':<15}")
    print(f"{'-'*8} {'-'*15} {'-'*50} {'-'*15}")
    
    for i, image in enumerate(images, 1):
        repo_tag = f"{image['repository']}:{image['tag']}"
        print(f"{i:<8} {image['id'][:12]:<15} {repo_tag[:50]:<50} {image['size']:<15}")
    
    print(f"{'-'*8} {'-'*15} {'-'*50} {'-'*15}")
    print("a       Remove all images")
    print("q       Quit without removing any image")
    
    choice = input("\nEnter option (number, 'a' for all, or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Operation cancelled.")
        return True
    
    if choice == 'a':
        return remove_all_images()
    
    # Check if choice is a valid number
    if choice.isdigit() and 1 <= int(choice) <= len(images):
        image = images[int(choice) - 1]
        image_tag = f"{image['repository']}:{image['tag']}"
        
        print(f"Removing image: {image_tag} ({image['id'][:12]})")
        result = run_command(["docker", "rmi", image['id']], check=False)
        
        if result is not None:
            print(f"Image '{image_tag}' removed successfully.")
            return True
        else:
            print(f"Failed to remove image '{image_tag}'.")
            print("It may be in use by a container. Try removing the container first with 'dkr rm'.")
            
            # Try with force flag if user wants
            response = input("Do you want to force remove this image? [y/N]: ").strip().lower()
            if response == 'y' or response == 'yes':
                print(f"Force removing image: {image_tag}")
                result = run_command(["docker", "rmi", "-f", image['id']], check=False)
                
                if result is not None:
                    print(f"Image '{image_tag}' force removed successfully.")
                    return True
            
            return False
    else:
        print("Invalid selection.")
        return False
