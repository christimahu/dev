"""
Shell command functionality for the development environment.

This module handles the 'dev' command, which provides a shell inside the development container.
It supports multiple terminal sessions connected to the same container, port conflict resolution,
and directory mapping between host and container.
"""

import os
import subprocess
from .config import DEV_DIR, IMAGE_NAME, IMAGE_TAG
from .utils import run_command, get_container_name, container_exists, container_running, parse_dev_env_file
import socket

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
    
    # CASE 1: Container is already running - just connect to it
    if container_running(container_name):
        print(f"Connecting to existing container: {container_name}")
        
        # Determine the working directory inside the container
        current_dir_in_container = None
        for mount in config['mounts']:
            host_path = mount['host_path']
            container_path = mount['container_path']
            
            # Check if current directory is inside this mount
            if current_dir.startswith(host_path):
                # Calculate the relative path
                rel_path = os.path.relpath(current_dir, host_path)
                current_dir_in_container = os.path.join(container_path, rel_path)
                break
        
        # Execute interactive shell in the existing container
        if current_dir_in_container:
            shell_cmd = ["docker", "exec", "-it", "-w", current_dir_in_container, container_name, "/bin/bash"]
        else:
            shell_cmd = ["docker", "exec", "-it", "-w", config['default_workdir'], container_name, "/bin/bash"]
        
        subprocess.run(shell_cmd)
        return  # Important: return here to avoid stopping the container
    
    # CASE 2: Container exists but is not running - start it
    elif container_exists(container_name):
        print(f"Starting existing container: {container_name}")
        run_command(["docker", "start", container_name])
        
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
        
        # Update working directory if needed
        current_dir_in_container = None
        
        # Try to find a mount point that contains the current directory
        for mount in config['mounts']:
            host_path = mount['host_path']
            container_path = mount['container_path']
            
            # Check if current directory is inside this mount
            if current_dir.startswith(host_path):
                # Calculate the relative path
                rel_path = os.path.relpath(current_dir, host_path)
                current_dir_in_container = os.path.join(container_path, rel_path)
                break
        
        # If we found a matching mount, update the container's working directory
        if current_dir_in_container and os.path.exists(current_dir):
            try:
                run_command(["docker", "exec", container_name, "bash", "-c", f"cd {current_dir_in_container} || true"])
            except Exception as e:
                print(f"Warning: Could not change directory: {e}")
    
    # CASE 3: Container doesn't exist - create it
    else:
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
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('0.0.0.0', int(host_port)))
                # Port is available, add the mapping
                cmd.append(f"--publish={port_mapping}")
            except socket.error:
                print(f"Port {host_port} is already in use, skipping port mapping for {port_mapping}")
            finally:
                s.close()
        
        # Add networking and security options
        cmd.extend(["--network", "bridge", "--cap-add=SYS_PTRACE", "--security-opt", "seccomp=unconfined"])
        
        # Add environment variables
        for key, value in config['env_vars'].items():
            cmd.append(f"--env={key}={value}")
        
        # Determine the working directory
        work_dir = config['default_workdir']
        
        # Try to find a mount point that contains the current directory
        current_dir_in_container = None
        for mount in config['mounts']:
            host_path = mount['host_path']
            container_path = mount['container_path']
            
            # Check if current directory is inside this mount
            if current_dir.startswith(host_path):
                # Calculate the relative path
                rel_path = os.path.relpath(current_dir, host_path)
                current_dir_in_container = os.path.join(container_path, rel_path)
                work_dir = current_dir_in_container
                break
        
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
    
    # If we have a container path for the current directory, use it as working directory
    # Otherwise use the default_workdir from config
    if current_dir_in_container:
        shell_cmd = ["docker", "exec", "-it", "-w", current_dir_in_container, container_name, "/bin/bash"]
    else:
        shell_cmd = ["docker", "exec", "-it", "-w", config['default_workdir'], container_name, "/bin/bash"]
    
    subprocess.run(shell_cmd)
    
    # After shell exits, DO NOT stop the container to allow multiple sessions
    print(f"Disconnected from container {container_name}")
    print(f"Container is still running. Use 'dev stop' to stop it when you're done.")
