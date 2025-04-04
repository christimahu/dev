"""
Utility functions for the development environment.
"""

import os
import subprocess
import sys
import hashlib
from pathlib import Path
from .config import DEV_DIR, HOME_DIR

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
        return result.stdout.strip() if capture_output and result.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"Error message: {e.stderr if e.stderr else str(e)}")
        if check:
            sys.exit(1)
        return None

def get_container_name():
    """
    Generate a container name based on the current directory.
    
    This ensures that different projects get their own container instance,
    preventing conflicts between development environments.
    
    Returns:
        A container name string derived from the current directory path
    """
    current_dir = os.getcwd()
    if current_dir != DEV_DIR:
        dir_hash = hashlib.md5(current_dir.encode()).hexdigest()[:8]
        return f"dev-{dir_hash}"
    return "dev-main"

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

def parse_dev_env_file(env_file):
    """
    Parse a dev.env file for directory mappings, port mappings, and environment variables.
    
    Args:
        env_file: Path to the environment file
        
    Returns:
        Dictionary containing parsed mounts, ports, default workdir, and environment variables
    """
    result = {
        'mounts': [],
        'ports': [],
        'env_vars': {},
        'default_workdir': '/home/me'
    }
    
    if not os.path.exists(env_file):
        print(f"Notice: {env_file} not found.")
        print(f"Create it based on dev_example.env for custom directory mappings and ports.")
        return result
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line:
                key, value = [part.strip() for part in line.split('=', 1)]
                
                if key == 'MOUNT':
                    # Process directory mounting
                    # Format: MOUNT=HOST_PATH:CONTAINER_PATH[:OPTIONS]
                    if ':' in value:
                        parts = value.split(':')
                        if len(parts) >= 2:
                            host_path = os.path.expanduser(parts[0])
                            container_path = parts[1]
                            options = parts[2] if len(parts) > 2 else ""
                            
                            # Validate the host path exists
                            if os.path.exists(host_path):
                                result['mounts'].append({
                                    'host_path': host_path,
                                    'container_path': container_path,
                                    'options': options
                                })
                            else:
                                print(f"Warning: Host path '{host_path}' does not exist. Mount ignored.")
                    
                elif key == 'PORT':
                    # Process port mapping
                    # Format: PORT=HOST_PORT:CONTAINER_PORT
                    if ':' in value:
                        result['ports'].append(value)
                
                elif key == 'DEFAULT_WORKDIR':
                    # Set default working directory in container
                    result['default_workdir'] = value
                
                else:
                    # Everything else is treated as an environment variable
                    result['env_vars'][key] = value
    
    # If no mounts were specified, warn user and add a default mount for .dev
    if not result['mounts']:
        print("Warning: No valid mounts found in dev.env.")
        dev_dir_host = DEV_DIR
        if os.path.exists(dev_dir_host):
            print(f"Adding default mount for {dev_dir_host}:/home/me/.dev")
            result['mounts'].append({
                'host_path': dev_dir_host,
                'container_path': '/home/me/.dev',
                'options': ""
            })
    
    return result
