"""
Build command module for the Docker container manager.

This module handles the 'build' command which builds Docker images
from the current directory or a specified Dockerfile.
"""

import os
import sys
from pathlib import Path
from .utils import run_command, image_exists
from .config import get_default_tag

def build_command(args):
    """
    Build a Docker image from the current directory.
    
    This command:
    1. Determines the image tag (from args or default)
    2. Checks for the Dockerfile
    3. Builds the Docker image
    4. Reports success or failure
    
    Args:
        args: Command-line arguments containing:
            - tag: Optional image name and tag
            - file: Optional path to Dockerfile
    """
    # Determine the tag to use
    tag = args.tag if args.tag else get_default_tag()
    
    # Determine the Dockerfile path
    dockerfile = args.file if args.file else os.path.join(os.getcwd(), "Dockerfile")
    
    # Check if Dockerfile exists
    if not os.path.exists(dockerfile):
        print(f"Error: Dockerfile not found at {dockerfile}")
        print("Create a Dockerfile or specify its location with --file")
        return False
    
    # Construct build command
    build_cmd = ["docker", "build", "-t", tag, "-f", dockerfile, "."]
    
    print(f"Building Docker image: {tag}")
    print(f"Using Dockerfile: {dockerfile}")
    print("Building...")
    
    # Run the build
    result = run_command(build_cmd, capture_output=False, check=False)
    
    # Check if build succeeded by verifying the image exists
    if image_exists(tag):
        print(f"\n✅ Successfully built Docker image: {tag}")
        
        # Print next steps
        print("\nNext steps:")
        print(f"  Run the container:  dkr run --image {tag}")
        print(f"  Interactive shell:  dkr shell --image {tag}")
        
        return True
    else:
        print("\n❌ Failed to build Docker image.")
        print("Check the build output for errors.")
        return False
