"""
Shell command functionality for the development environment.

This module handles the 'dev' command, which provides a shell inside the development container.
It supports multiple terminal sessions connected to the same container, port conflict resolution,
and directory mapping between host and container.

Tutorial:
---------
The shell_command function is the main entry point for the 'dev' command. It:
1. Determines the appropriate working directory based on your current location
2. Checks if a container already exists and is running, stopped, or needs to be created
3. Handles container creation, startup, and shell access
4. Manages port conflicts to ensure containers can start successfully

Examples:
---------
- Enter a development container:
  ```bash
  dev
  ```

- Run a command in the container:
  ```bash
  dev exec ls -la
  ```
"""

import os
import subprocess
import socket
from .config import DEV_DIR, IMAGE_NAME, IMAGE_TAG
from .utils import run_command, get_container_name, container_exists, container_running, parse_dev_env_file


def shell_command(args):
    """
    Enter a shell in the development container.
    
    If the container is already running, this will connect to it.
    If the container exists but is not running, it will be started.
    If the container doesn't exist, it will be created with the specified mounts and ports.
    
    Multiple terminal sessions can connect to the same container, allowing for
    parallel work (e.g., editing in one terminal while building in another).
    
    The container will remain running until explicitly stopped with 'dev stop'.
    """
    container_name = get_container_name()
    current_dir = os.getcwd()
    
    # Parse dev.env for mounts, ports, and environment variables
    env_file = os.path.join(DEV_DIR, "dev.env")
    config = parse_dev_env_file(env_file)
    
    # Determine the working directory inside the container
    work_dir = determine_working_directory(current_dir, config)
    
    # CASE 1: Container is already running - just connect to it
    if container_running(container_name):
        connect_to_running_container(container_name, work_dir)
        return  # Important: return here to avoid stopping the container
    
    # CASE 2: Container exists but is not running - start it
    elif container_exists(container_name):
        start_existing_container(container_name, config, work_dir)
    
    # CASE 3: Container doesn't exist - create it
    else:
        create_new_container(container_name, config, work_dir)
    
    # After shell exits, DO NOT stop the container to allow multiple sessions
    print(f"Disconnected from container {container_name}")
    print(f"Container is still running. Use 'dev stop' to stop it when you're done.")


def determine_working_directory(current_dir, config):
    """
    Determine the appropriate working directory inside the container.
    
    If the current directory is within a mounted path, use the corresponding
    container path. Otherwise, use the default working directory.
    
    Args:
        current_dir: Current directory on the host
        config: Configuration from dev.env
        
    Returns:
        Path to use as working directory inside the container
    """
    for mount in config['mounts']:
        host_path = mount['host_path']
        container_path = mount['container_path']
        
        # Expand the host path to handle ~ and environment variables
        expanded_host_path = os.path.expanduser(os.path.expandvars(host_path))
        
        # Check if current directory is inside this mount
        if current_dir.startswith(expanded_host_path):
            # Calculate the relative path
            rel_path = os.path.relpath(current_dir, expanded_host_path)
            return os.path.join(container_path, rel_path)
    
    # If current directory is not in any mount, use DEFAULT_WORKDIR
    return config['default_workdir']


def connect_to_running_container(container_name, work_dir):
    """
    Connect to an already running container.
    
    Args:
        container_name: Name of the container
        work_dir: Working directory to use inside the container
    """
    print(f"Connecting to existing container: {container_name}")
    
    # Execute interactive shell in the existing container
    shell_cmd = ["docker", "exec", "-it", "-w", work_dir, container_name, "/bin/bash"]
    subprocess.run(shell_cmd)


def check_port_availability(port):
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        
    Returns:
        Boolean indicating if the port is available
    """
    try:
        # Try to create a socket and bind to the port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', int(port)))
        s.close()
        return True
    except socket.error:
        return False


def start_existing_container(container_name, config, work_dir):
    """
    Start an existing but stopped container.
    
    This function handles port conflicts by removing conflicting port mappings
    before starting the container.
    
    Args:
        container_name: Name of the container
        config: Configuration from dev.env
        work_dir: Working directory to use inside the container
    """
    print(f"Starting existing container: {container_name}")
    
    # Check for port conflicts and update container port bindings if needed
    port_conflicts = []
    for port_mapping in config['ports']:
        host_port = port_mapping.split(':')[0]
        if not check_port_availability(host_port):
            port_conflicts.append(host_port)
    
    if port_conflicts:
        print(f"Detected port conflicts for ports: {', '.join(port_conflicts)}")
        print("Updating container to avoid port conflicts...")
        
        # Get current port mappings
        cmd = ["docker", "container", "inspect", 
               "--format", "{{json .HostConfig.PortBindings}}", 
               container_name]
        
        try:
            # Update container to remove conflicting ports
            for port in port_conflicts:
                # For each conflicting port, remove its mapping
                cmd = ["docker", "container", "update", 
                       "--publish-rm", f"{port}", 
                       container_name]
                run_command(cmd, check=False)
        except Exception as e:
            print(f"Warning: Could not update port bindings: {e}")
            print("Container may still have port conflicts.")
    
    # Start the container
    try:
        run_command(["docker", "start", container_name])
    except Exception as e:
        print(f"Error starting container: {e}")
        print("You may need to use 'dev delete' and then 'dev' to create a new container.")
        return
    
    # Run initialization script to ensure environment is set up
    # This handles cases where the container was stopped and environment needs refreshing
    init_script = """
    # Create Neovim config directory
    mkdir -p /home/me/.config/nvim

    # Set up Neovim configuration
    # Always use the in-container path to avoid symlink issues with host
    ln -sf /home/me/.dev/config/init.lua /home/me/.config/nvim/init.lua

    # Set up bashrc to source shell_functions
    if ! grep -q "source /home/me/.dev/config/shell_functions" /home/me/.bashrc; then
        echo "source /home/me/.dev/config/shell_functions" >> /home/me/.bashrc
    fi
    
    # Source shell_functions in this session to ensure commands are available immediately
    source /home/me/.dev/config/shell_functions || true
    """
    
    # Execute initialization script
    try:
        run_command(["docker", "exec", container_name, "bash", "-c", init_script])
    except Exception as e:
        print(f"Warning: Initialization script encountered an error: {e}")
        print("The container may not be fully configured.")
    
    # Execute interactive shell
    print(f"Connecting to development container: {container_name}")
    shell_cmd = ["docker", "exec", "-it", "-w", work_dir, container_name, "/bin/bash"]
    subprocess.run(shell_cmd)


def create_new_container(container_name, config, work_dir):
    """
    Create a new container if none exists.
    
    Args:
        container_name: Name of the container
        config: Configuration from dev.env
        work_dir: Working directory to use inside the container
    """
    print(f"Creating new development container: {container_name}")
    
    # Create Docker command
    cmd = ["docker", "run", "-d", "-it", "--name", container_name]
    
    # Add all mounts
    for mount in config['mounts']:
        mount_str = f"{mount['host_path']}:{mount['container_path']}"
        if mount['options']:
            mount_str += f":{mount['options']}"
        cmd.append(f"--volume={mount_str}")
    
    # Add port mappings - but skip any ports that are already in use
    for port_mapping in config['ports']:
        # Format: "9000:8000" 
        host_port, container_port = port_mapping.split(':')
        
        # Check if the host port is already allocated
        if check_port_availability(host_port):
            # Port is available, add the mapping
            cmd.append(f"--publish={port_mapping}")
        else:
            print(f"Port {host_port} is already in use, skipping port mapping for {port_mapping}")
    
    # Add networking and security options
    cmd.extend(["--network", "bridge", "--cap-add=SYS_PTRACE", "--security-opt", "seccomp=unconfined"])
    
    # Add environment variables
    for key, value in config['env_vars'].items():
        cmd.append(f"--env={key}={value}")
    
    # Set working directory
    cmd.append(f"--workdir={work_dir}")
    cmd.append(f"{IMAGE_NAME}:{IMAGE_TAG}")
    
    # Run the container
    run_command(cmd)
    
    # Run initialization script with improved error handling
    init_script = """
    # Create Neovim config directory
    mkdir -p /home/me/.config/nvim

    # Set up Neovim configuration
    # Always use the in-container path to avoid symlink issues with host
    ln -sf /home/me/.dev/config/init.lua /home/me/.config/nvim/init.lua

    # Set up bashrc to source shell_functions
    if ! grep -q "source /home/me/.dev/config/shell_functions" /home/me/.bashrc; then
        echo "source /home/me/.dev/config/shell_functions" >> /home/me/.bashrc
    fi
    """
    
    # Execute initialization script
    try:
        run_command(["docker", "exec", container_name, "bash", "-c", init_script])
    except Exception as e:
        print(f"Warning: Initialization script encountered an error: {e}")
        print("The container may not be fully configured.")
    
    # Execute interactive shell
    print(f"Connecting to development container: {container_name}")
    shell_cmd = ["docker", "exec", "-it", "-w", work_dir, container_name, "/bin/bash"]
    subprocess.run(shell_cmd)
