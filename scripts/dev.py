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
- dev stop          : Stop the development container
- dev delete        : Delete the development container
- dev help          : Display helpful information about commands
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
from devcmd.container import stop_command, delete_command, status_command, exec_command, logs_command
from devcmd.maintenance import prune_command, update_srv_function
from devcmd.help import help_command, setup_help_parser

def main():
    """
    Main entry point for the development environment manager.
    
    Parses command-line arguments and calls the appropriate command function.
    """
    parser = argparse.ArgumentParser(description="Development Environment Manager")
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
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the development container")
    stop_parser.add_argument("--name", help="Container name (default: based on current directory)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete the development container")
    delete_parser.add_argument("--name", help="Container name (default: based on current directory)")
    
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
    prune_parser = subparsers.add_parser("prune", help="Clean up unused Docker resources")
    prune_parser.add_argument("--all", action="store_true", help="Remove all unused resources")
    prune_parser.add_argument("--volumes", action="store_true", help="Also remove volumes")
    
    # Help command
    help_parser = setup_help_parser(subparsers)
    
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
        "help": help_command
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
