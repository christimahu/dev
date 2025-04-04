"""
Maintenance commands for the development environment.
"""

import os
import subprocess
from .config import DEV_DIR

def prune_command(args):
    """
    Clean up unused Docker resources.
    
    Args:
        args: Command-line arguments
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

def update_srv_function():
    """
    Update the srv function to use .dev instead of dev
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
