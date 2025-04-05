#!/usr/bin/env python3
"""
Development Environment Manager
==============================

This script manages a Docker-based development environment, creating a consistent
development experience across different machines.

Common commands:
- dev               : Enter a shell in the development container
- dev build         : Build the development container image
- dev rebuild       : Rebuild the container with updated plugins
- dev status        : Show status of the development containers
- dev exec [command]: Execute a command in the development container
- dev stop          : Stop the development container (with interactive selection)
- dev delete        : Delete the development container
- dev cleanup       : Remove all development containers
- dev logs          : View logs from the development container
- dev prune         : Clean up unused Docker resources
- dev prune-images  : Remove development-related Docker images

Tutorial:
---------
This is the main command-line interface for the development environment. It provides
a set of commands for working with Docker containers in a more user-friendly way.

Getting Started:
1. Build the container: `dev build`
2. Start a shell: `dev`
3. Run commands inside the container: `dev exec <command>`
4. Check status: `dev status`
5. Stop containers: `dev stop`
6. Clean up: `dev cleanup`

Example workflow:
```bash
# Build the container image (only needed once)
dev build

# Enter a shell in the container
cd ~/my-project
dev

# Inside the container, do your work...
# When done, exit the shell with 'exit'

# If needed, stop the container
dev stop

# To remove all containers
dev cleanup
```
"""

import argparse
import sys
import os
from pathlib import Path

# Add the script directory to the path so Python can find the devcmd package
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import commands from modules
from devcmd.shell import shell_command
from devcmd.build import build_command, rebuild_command
from devcmd.container import stop_command, delete_command, status_command, exec_command, logs_command, cleanup_command
from devcmd.maintenance import prune_command, prune_images_command, update_srv_function

def main():
    """
    Main entry point for the development environment manager.
    
    Parses command-line arguments and calls the appropriate command function.
    
    Tutorial:
    ---------
    This function:
    1. Sets up the argument parser with all available commands
    2. Parses the command-line arguments
    3. Calls the appropriate function based on the command
    
    If no command is provided, it defaults to the 'shell' command,
    which enters a shell in the development container.
    """
    parser = argparse.ArgumentParser(
        description="Development Environment Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dev                    # Enter a shell in the container
  dev status             # Show container status
  dev stop               # Stop container with interactive selection
  dev exec ls -la        # Run command in container
  dev cleanup            # Remove all dev containers
  
For more information, see README.md or visit:
https://github.com/christimahu/dev
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Shell command
    subparsers.add_parser("shell", help="Enter a shell in the development container")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build the development container image")
    build_parser.add_argument("--no-cache", action="store_true", help="Build without using cache")
    build_parser.add_argument("--stage", choices=["full", "user", "final"], default="full", 
                              help="Build stage (full, user, or final)")
    
    # Rebuild command
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild container with updated plugins")
    rebuild_parser.add_argument("--no-cache", action="store_true", help="Build without using cache")
    rebuild_parser.add_argument("--with-plugins", action="store_true", help="Update Neovim plugins during rebuild")
    rebuild_parser.add_argument("--name", help="Container name (default: based on current directory)")
    
    # Stop command with improved interface
    stop_parser = subparsers.add_parser(
        "stop", 
        help="Stop development containers with interactive selection",
        description="Stops development containers. If multiple containers are running, shows a selection menu."
    )
    stop_parser.add_argument("--name", help="Specific container name to stop")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete the development container")
    delete_parser.add_argument("--name", help="Container name (default: based on current directory)")
    
    # Cleanup command (new)
    cleanup_parser = subparsers.add_parser(
        "cleanup", 
        help="Remove all development containers",
        description="Stops and removes all development containers (with 'dev-' prefix)."
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show status of development containers")
    status_parser.add_argument("--name", help="Container name (default: based on current directory)")
    
    # Exec command
    exec_parser = subparsers.add_parser("exec", help="Execute a command in the development container")
    exec_parser.add_argument("command", nargs="+", help="Command to execute")
    exec_parser.add_argument("--name", help="Container name (default: based on current directory)")
    exec_parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View logs from the development container")
    logs_parser.add_argument("--name", help="Container name (default: based on current directory)")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow log output")
    logs_parser.add_argument("--lines", type=int, default=100, help="Number of lines to show")
    
    # Prune command
    prune_parser = subparsers.add_parser(
        "prune", 
        help="Clean up unused Docker resources",
        description="Removes unused containers and dangling images to free up disk space."
    )
    prune_parser.add_argument("--all", action="store_true", help="Remove all unused resources")
    prune_parser.add_argument("--volumes", action="store_true", help="Also remove volumes")
    
    # Prune-images command (new)
    prune_images_parser = subparsers.add_parser(
        "prune-images", 
        help="Remove development-related Docker images",
        description="Removes Docker images created by the development environment."
    )
    prune_images_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation and remove all images")
    
    args = parser.parse_args()
    
    # If no command is provided, default to shell
    if not args.command:
        shell_command(args)
        return
    
    # Execute the appropriate command
    commands = {
        "shell": shell_command,
        "build": build_command,
        "rebuild": rebuild_command,
        "stop": stop_command,
        "delete": delete_command,
        "status": status_command,
        "exec": exec_command,
        "logs": logs_command,
        "prune": prune_command,
        "prune-images": prune_images_command,
        "cleanup": cleanup_command
    }
    
    # Fix for handling list-based command arguments
    command_name = args.command
    if hasattr(args, 'command') and isinstance(args.command, list):
        # For exec command, the actual command name is 'exec'
        # and args.command contains the command to execute
        # Instead of trying to use args.command as a key, we determine the command name
        # based on the subparser that was used
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for choice, subparser in action.choices.items():
                    if subparser == exec_parser and command_name is not None:
                        command_name = "exec"
                        break
    
    if command_name in commands:
        commands[command_name](args)
    else:
        parser.print_help()
    
    # Update references from ~/dev to ~/.dev in shell_functions
    if args.command in ["build", "rebuild"]:
        update_srv_function()


if __name__ == "__main__":
    main()
