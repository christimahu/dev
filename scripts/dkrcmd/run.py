"""
Run command module for the Docker container manager.

This module handles the 'run' command which starts containers based on images.
"""

import os
import sys
import uuid
from pathlib import Path
from .utils import run_command, container_exists, image_exists, get_default_image_name
from .config import DEFAULT_PORTS, DEFAULT_DOCKER_FLAGS

def run_command(args):
    """
    Run a Docker container based on an image.
    
    This command:
    1. Determines the image to use (from args or default)
    2. Verifies the image exists
    3. Sets up port mappings and environment variables
    4. Starts the container
    5. Reports success or failure
    
    Args:
        args: Command-line arguments containing:
            - image: Optional image name
            - name: Optional container name
            - port: Optional port mappings
            - env: Optional environment variables
    """
    # Determine the image to use
    image = args.image if args.image else get_default_image_name()
    
    # Check if image exists
    if not image_exists(image):
        print(f"Error: Image '{image}' not found.")
        print("Build the image first with: dkr build")
        return False
    
    # Generate container name if not provided
    container_name = args.name if args.name else f"container-{str(uuid.uuid4())[:8]}"
    
    # Check if container with this name already exists
    if container_exists(container_name):
        print(f"Error: Container '{container_name}' already exists.")
        print("Use a different name or remove the existing container:")
        print(f"  dkr rm --name {container_name}")
        return False
    
    # Build the run command
    run_cmd = ["docker", "run", "-it"]
    
    # Add default flags (e.g., --rm to remove container when it exits)
    for flag in DEFAULT_DOCKER_FLAGS:
        run_cmd.append(flag)
    
    # Add name
    run_cmd.extend(["--name", container_name])
    
    # Add port mappings
    if args.port:
        for port in args.port:
            run_cmd.extend(["-p", port])
    else:
        # Use default ports if none specified
        for port in DEFAULT_PORTS:
            run_cmd.extend(["-p", port])
    
    # Add environment variables
    if args.env:
        for env_var in args.env:
            run_cmd.extend(["-e", env_var])
    
    # Add the image name
    run_cmd.append(image)
    
    print(f"Starting container '{container_name}' from image '{image}'")
    if args.port:
        print(f"Port mappings: {', '.join(args.port)}")
    else:
        print(f"Default port mappings: {', '.join(DEFAULT_PORTS)}")
    
    # Run the container
    print("\nContainer output:")
    print("=" * 40)
    
    result = run_command(run_cmd, capture_output=False, check=False)
    
    # The container has finished running (because it exited or was detached)
    print("=" * 40)
    
    # Check final container state
    if container_exists(container_name) and not container_running(container_name):
        print(f"\n✅ Container '{container_name}' has exited.")
        if "--rm" in run_cmd:
            print("The container was automatically removed (--rm flag).")
        else:
            print("Container still exists. To remove it:")
            print(f"  dkr rm --name {container_name}")
    elif container_running(container_name):
        print(f"\n✅ Container '{container_name}' is running.")
        print("To stop the container:")
        print(f"  dkr stop --name {container_name}")
    else:
        print(f"\n❓ Container '{container_name}' not found.")
        print("It may have been automatically removed.")
    
    return True
