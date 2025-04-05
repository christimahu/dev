"""
Container management functions for the development environment.

This module provides commands for managing container lifecycle:
- status: Display container information and status
- stop: Stop running containers with interactive selection
- delete: Remove containers
- exec: Execute commands inside containers
- logs: View container logs
- cleanup: Remove all development containers

Tutorial:
---------
These functions provide an interface to Docker for managing development containers.
They abstract away complex Docker commands and provide a more user-friendly experience.

Examples:
---------
1. Stopping containers:
   When multiple containers are running, `stop_command` will show a menu:
   ```
   Running development containers:
   ============================================================
   Option   Container ID    Name                Status           
   ------------------------------------------------------------
   1        95f94a20b6ad    dev-37753f2e        Up 24 minutes   
   2        73199ac8cf91    dev-485001ea        Up 24 minutes   
   3        a4f02133e162    dev-145bc274        Up 25 minutes   
   ------------------------------------------------------------
   a        Stop all containers
   q        Quit without stopping any container
   ============================================================
   ```

2. Cleaning up containers:
   `cleanup_command` will stop and remove all development containers:
   ```
   Cleaning up all development containers...
   Stopping container dev-37753f2e (95f94a20b6ad)...
   Removing container dev-37753f2e (95f94a20b6ad)...
   Stopping container dev-485001ea (73199ac8cf91)...
   Removing container dev-485001ea (73199ac8cf91)...
   Removed 3 development container(s).
   ```
"""

import os
import subprocess
import sys
from .config import DEV_DIR
from .utils import run_command, get_container_name, container_exists, container_running, parse_dev_env_file


def status_command(args):
    """
    Show status of the development containers.
    
    Displays detailed information about the container including:
    - Image information
    - Container status
    - Port mappings
    - Volume mounts
    
    Args:
        args: Command-line arguments containing optional container name
    
    Tutorial:
    ---------
    This command acts like a more detailed `docker ps` specifically for
    development containers. It provides a comprehensive overview of the
    container's configuration and current state.
    """
    from .config import IMAGE_NAME, IMAGE_TAG
    
    container_name = args.name if args.name else get_container_name()
    
    print("\nDevelopment Environment Status:")
    print("=" * 40)
    
    # Check image
    image_info = run_command(["docker", "images", "-q", f"{IMAGE_NAME}:{IMAGE_TAG}"], check=False)
    if image_info:
        image_details = run_command(["docker", "image", "inspect", "-f", "{{.Created}}", f"{IMAGE_NAME}:{IMAGE_TAG}"], check=False)
        print(f"Image: {IMAGE_NAME}:{IMAGE_TAG} (Created: {image_details})")
    else:
        print(f"Image: {IMAGE_NAME}:{IMAGE_TAG} (Not found)")
    
    # Check container
    if container_exists(container_name):
        status = "Running" if container_running(container_name) else "Stopped"
        try:
            # Get container details with proper error handling
            inspect_format = "{{.Config.Image}} | {{.State.StartedAt}} | {{.NetworkSettings.IPAddress}}"
            details = run_command([
                "docker", "inspect", 
                "-f", inspect_format,
                container_name
            ], check=False)
            
            # Split details, but handle case where we don't get all values
            parts = details.split(" | ")
            image = parts[0] if len(parts) > 0 else "Unknown"
            started = parts[1] if len(parts) > 1 else "Unknown"
            ip = parts[2] if len(parts) > 2 else "None"
            
            print(f"Container: {container_name} ({status})")
            print(f"Started: {started}")
            print(f"IP Address: {ip}")
            
            # Get port mappings
            port_info = run_command([
                "docker", "inspect", 
                "-f", "{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{println}}{{end}}", 
                container_name
            ], check=False)
            
            if port_info and port_info.strip():
                print("Port Mappings:")
                for line in port_info.split("\n"):
                    if line.strip():
                        print(f"  {line}")
                
            # Get mount info
            mount_info = run_command([
                "docker", "inspect", 
                "-f", "{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}", 
                container_name
            ], check=False)
            
            if mount_info and mount_info.strip():
                print("Volume Mounts:")
                for line in mount_info.split("\n"):
                    if line.strip():
                        print(f"  {line}")
        except Exception as e:
            print(f"Container: {container_name} ({status})")
            print(f"Error getting container details: {e}")
    else:
        print(f"Container: {container_name} (Not found)")
    
    print("=" * 40)


def get_running_dev_containers():
    """
    Get a list of all running development containers.
    
    Returns:
        List of dictionaries with container information (id, name, status)
    
    Tutorial:
    ---------
    This helper function finds all containers with the 'dev-' prefix.
    It's used by other commands to identify which containers are managed
    by the development environment.
    """
    containers_output = run_command(
        ["docker", "ps", "--filter", "name=dev-", "--format", "{{.ID}}|{{.Names}}|{{.Status}}"],
        capture_output=True,
        check=False
    )
    
    if not containers_output or containers_output.strip() == "":
        return []
    
    containers = []
    for line in containers_output.strip().split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 3:
                containers.append({
                    "id": parts[0],
                    "name": parts[1],
                    "status": parts[2]
                })
    
    return containers


def display_container_selection(containers):
    """
    Display an interactive menu for container selection.
    
    Args:
        containers: List of container dictionaries
        
    Returns:
        Selected container ID or special command ('all', 'none')
    
    Tutorial:
    ---------
    This function presents a user-friendly menu for selecting which container
    to operate on. It's used when multiple containers are running and the user
    needs to choose one (or all) to stop or delete.
    """
    if not containers:
        print("No running development containers found.")
        return None
    
    print("\nRunning development containers:")
    print("=" * 60)
    print(f"{'Option':<8} {'Container ID':<15} {'Name':<20} {'Status':<20}")
    print("-" * 60)
    
    for i, container in enumerate(containers, 1):
        print(f"{i:<8} {container['id'][:12]:<15} {container['name']:<20} {container['status']:<20}")
    
    print("-" * 60)
    print("a       Stop all containers")
    print("q       Quit without stopping any container")
    print("=" * 60)
    
    while True:
        choice = input("Enter option (number, 'a' for all, or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            return 'none'
        elif choice == 'a':
            return 'all'
        elif choice.isdigit() and 1 <= int(choice) <= len(containers):
            return containers[int(choice) - 1]['id']
        else:
            print("Invalid selection. Please try again.")


def stop_command(args):
    """
    Stop the development container(s).
    
    This gracefully stops container(s) with a short timeout while preserving state,
    allowing restart later with the same configuration. If multiple containers are
    running, shows an interactive selection menu.
    
    Args:
        args: Command-line arguments containing optional container name
    
    Tutorial:
    ---------
    This command provides several ways to stop containers:
    
    1. Stop a specific container by name: dev stop --name container_name
    2. If only one container is running: dev stop
    3. If multiple containers are running, show a selection menu: dev stop
    
    The selection menu allows stopping a specific container, all containers,
    or cancelling the operation.
    """
    # Check if a specific container was requested
    if args.name:
        container_name = args.name
        if container_running(container_name):
            print(f"Stopping container: {container_name}")
            run_command(["docker", "stop", "-t", "1", container_name])
        else:
            print(f"Container {container_name} is not running.")
        return
    
    # Get all running development containers
    containers = get_running_dev_containers()
    
    # Handle based on number of containers
    if not containers:
        print("No running development containers found.")
        return
    elif len(containers) == 1:
        # If only one container is running, stop it directly
        container = containers[0]
        print(f"Stopping container: {container['name']} ({container['id'][:12]})")
        run_command(["docker", "stop", "-t", "1", container['id']])
    else:
        # If multiple containers are running, show selection menu
        selection = display_container_selection(containers)
        
        if selection == 'none':
            print("Operation cancelled.")
            return
        elif selection == 'all':
            print("Stopping all development containers...")
            for container in containers:
                print(f"Stopping {container['name']} ({container['id'][:12]})...")
                run_command(["docker", "stop", "-t", "1", container['id']])
            print("All containers stopped.")
        else:
            # Stop the selected container
            container_id = selection
            container_name = next((c['name'] for c in containers if c['id'] == container_id), container_id)
            print(f"Stopping container: {container_name} ({container_id[:12]})")
            run_command(["docker", "stop", "-t", "1", container_id])


def delete_command(args):
    """
    Delete the development container.
    
    This permanently removes the container and all non-mounted data.
    The container will be stopped first if it's running.
    
    Args:
        args: Command-line arguments containing optional container name
    
    Tutorial:
    ---------
    Use this command to completely remove a container when you're done with it
    or need to start fresh. Any data not in mounted volumes will be lost.
    
    Example:
        dev delete            # Delete container for current directory
        dev delete --name dev-12345  # Delete specific container
    """
    container_name = args.name if args.name else get_container_name()
    
    if container_exists(container_name):
        if container_running(container_name):
            print(f"Stopping container: {container_name}")
            run_command(["docker", "stop", "-t", "1", container_name])
        
        print(f"Removing container: {container_name}")
        run_command(["docker", "rm", container_name])
    else:
        print(f"Container {container_name} does not exist.")


def exec_command(args):
    """
    Execute a command in the development container.
    
    This allows running commands inside a running container without
    starting a full interactive shell. If the container isn't running,
    it will be started automatically.
    
    Args:
        args: Command-line arguments containing:
            - command: The command to execute
            - name (optional): Container name
            - interactive (optional): Whether to run in interactive mode
    
    Tutorial:
    ---------
    This command lets you run commands in the container without entering
    a full shell. It's useful for quick operations or scripting.
    
    Examples:
        dev exec ls -la                 # Run 'ls -la' in the container
        dev exec -i python manage.py    # Run Python interactively
        dev exec --name dev-12345 npm install  # Run in specific container
    """
    container_name = args.name if args.name else get_container_name()
    
    if not container_running(container_name):
        print(f"Container {container_name} is not running.")
        if container_exists(container_name):
            print(f"Starting container {container_name}...")
            run_command(["docker", "start", container_name])
        else:
            print("Please create and start the container first.")
            return
    
    cmd = ["docker", "exec"]
    if args.interactive:
        cmd.append("-it")
    cmd.append(container_name)
    
    # Handle command arguments properly
    if isinstance(args.command, list):
        # If command is already a list, extend cmd with it
        cmd.extend(args.command)
    elif isinstance(args.command, str):
        # If it's a single string, pass it as a shell command
        cmd.extend(["bash", "-c", args.command])
    else:
        # For any other case, convert to string
        cmd.extend(["bash", "-c", str(args.command)])
    
    subprocess.run(cmd)


def logs_command(args):
    """
    View logs from the development container.
    
    Displays the output logs from the container, which can be useful
    for troubleshooting or monitoring background processes.
    
    Args:
        args: Command-line arguments containing:
            - name (optional): Container name
            - follow (optional): Whether to follow log output
            - lines (optional): Number of lines to show
    
    Tutorial:
    ---------
    This command shows the output from processes running in the container.
    It's helpful when debugging or checking what happened in a container.
    
    Examples:
        dev logs                # Show recent logs
        dev logs -f             # Follow logs in real-time
        dev logs --lines 50     # Show last 50 lines
    """
    container_name = args.name if args.name else get_container_name()
    
    if container_exists(container_name):
        cmd = ["docker", "logs"]
        if args.follow:
            cmd.append("-f")
        if args.lines:
            cmd.extend(["--tail", str(args.lines)])
        cmd.append(container_name)
        subprocess.run(cmd)
    else:
        print(f"Container {container_name} does not exist.")


def cleanup_command(args):
    """
    Remove all development containers (both running and stopped).
    
    This helps keep your Docker environment clean by removing containers
    with the 'dev-' prefix. Stops any running containers before removal.
    
    Args:
        args: Command-line arguments
    
    Tutorial:
    ---------
    Use this command when you want to clean up your Docker environment
    and remove all containers created by the dev tool. This is useful when
    you have many development containers and want to start fresh.
    
    Example:
        dev cleanup  # Removes all containers with 'dev-' prefix
    """
    print("Cleaning up all development containers...")
    
    # Get all containers with dev- prefix
    dev_containers = run_command(
        ["docker", "ps", "-a", "--filter", "name=dev-", "--format", "{{.ID}}|{{.Names}}|{{.Status}}"], 
        capture_output=True, 
        check=False
    )
    
    if not dev_containers or dev_containers.strip() == "":
        print("No development containers found.")
        return
    
    container_list = dev_containers.strip().split("\n")
    removed_count = 0
    
    for container_info in container_list:
        if not container_info.strip():
            continue
            
        parts = container_info.split("|")
        if len(parts) >= 2:
            container_id = parts[0]
            container_name = parts[1]
            is_running = "Up" in container_info
            
            # Stop container if running
            if is_running:
                print(f"Stopping container {container_name} ({container_id[:12]})...")
                run_command(["docker", "stop", "-t", "1", container_id])
            
            print(f"Removing container {container_name} ({container_id[:12]})...")
            run_command(["docker", "rm", container_id])
            removed_count += 1
    
    if removed_count > 0:
        print(f"Removed {removed_count} development container(s).")
    else:
        print("No containers were removed.")
