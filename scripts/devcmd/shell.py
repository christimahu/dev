"""
Shell command functionality for the development environment.
"""

import os
import subprocess
from .config import DEV_DIR, IMAGE_NAME, IMAGE_TAG
from .utils import run_command, get_container_name, container_exists, container_running, parse_dev_env_file

def shell_command(args):
    """
    Enter a shell in the development container.
    
    This function creates a new container with your specified directories
    mounted, allowing access to your projects and files while isolating
    the container environment.
    """
    container_name = get_container_name()
    current_dir = os.getcwd()
    
    # Parse dev.env for mounts, ports, and environment variables
    env_file = os.path.join(DEV_DIR, "dev.env")
    config = parse_dev_env_file(env_file)
    
    # If container doesn't exist, create it
    if not container_exists(container_name):
        print(f"Creating new development container: {container_name}")
        
        # Create Docker command
        cmd = ["docker", "run", "-d", "-it", "--name", container_name]
        
        # Add all mounts
        for mount in config['mounts']:
            mount_str = f"{mount['host_path']}:{mount['container_path']}"
            if mount['options']:
                mount_str += f":{mount['options']}"
            cmd.append(f"--volume={mount_str}")
        
        # Add port mappings
        for port_mapping in config['ports']:
            cmd.append(f"--publish={port_mapping}")
        
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
    
    # If container exists but is not running, start it
    elif not container_running(container_name):
        print(f"Starting existing container: {container_name}")
        run_command(["docker", "start", container_name])
        
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
    
    # Execute interactive shell
    print(f"Connecting to development container: {container_name}")
    
    # If we have a container path for the current directory, use it as working directory
    # Otherwise use the default_workdir from config
    if current_dir_in_container:
        shell_cmd = ["docker", "exec", "-it", "-w", current_dir_in_container, container_name, "/bin/bash"]
    else:
        shell_cmd = ["docker", "exec", "-it", "-w", config['default_workdir'], container_name, "/bin/bash"]
    
    subprocess.run(shell_cmd)
    
    # After shell exits, stop the container after a brief delay
    print(f"Stopping container {container_name}")
    run_command(["docker", "stop", "-t", "1", container_name], check=False)
