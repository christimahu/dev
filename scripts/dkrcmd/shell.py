"""
Shell command module for the Docker container manager.

This module handles the 'shell' command which starts an interactive shell
in a container, useful for debugging and exploration.
"""

import os
import sys
import uuid
from pathlib import Path
from .utils import run_command, image_exists, get_default_image_name

def shell_command(args):
    """
    Start an interactive shell in a Docker container.
    
    This command:
    1. Determines the image to use (from args or default)
    2. Verifies the image exists
    3. Starts a container with a shell command
    
    Args:
        args: Command-line arguments containing:
            - image: Optional image name
    """
    # Determine the image to use
    image = args.image if args.image else get_default_image_name()
    
    # Check if image exists
    if not image_exists(image):
        print(f"Error: Image '{image}' not found.")
        print("Build the image first with: dkr build")
        return False
    
    # Generate random container name
    container_name = f"shell-{str(uuid.uuid4())[:8]}"
    
    # Build the shell command
    # Using --rm to automatically remove the container when it exits
    shell_cmd = [
        "docker", "run", 
        "--rm",                 # Remove when done
        "-it",                  # Interactive with TTY
        "--name", container_name,
        image,
        "/bin/bash"            # Command to run: bash shell
    ]
    
    # Check if bash exists in the image, if not try sh
    test_cmd = [
        "docker", "run", "--rm", image,
        "bash", "-c", "echo bash exists"
    ]
    
    bash_exists = run_command(test_cmd, check=False)
    
    if not bash_exists:
        # Try with /bin/sh instead
        shell_cmd[-1] = "/bin/sh"
    
    print(f"Starting interactive shell in container from image '{image}'")
    print("Container will be removed when you exit the shell.\n")
    
    # Run the container with shell
    result = run_command(shell_cmd, capture_output=False, check=False)
    
    # The shell has exited
    print("\nShell session ended")
    
    return True
