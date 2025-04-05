"""
Help command functionality for the development environment.

This module provides comprehensive help information for all dev commands,
including general help and command-specific details.
"""

import argparse
import textwrap
from typing import Dict, Optional


def help_command(args):
    """
    Display help information for the development environment.
    
    This command provides detailed help for all commands or for a specific
    command when requested. It's designed to make the development tooling
    more user-friendly by providing clear and comprehensive documentation.
    
    Args:
        args: Command-line arguments containing the optional command to get help for
    """
    if hasattr(args, 'command_name') and args.command_name:
        # Display help for a specific command
        display_command_help(args.command_name)
    else:
        # Display general help
        display_general_help()


def display_general_help():
    """
    Display the general help information for all commands.
    
    This includes a brief overview of the development environment and
    a list of all available commands with their descriptions.
    """
    # Header text
    print("\n=== Development Environment Manager ===")
    print("A Docker-based development environment providing a consistent experience across machines.\n")
    
    # Main commands section
    print("COMMON COMMANDS:")
    print_command_help("dev", "Enter a shell in the development container")
    print_command_help("dev build", "Build the development container image")
    print_command_help("dev rebuild", "Rebuild the container with updated plugins")
    print_command_help("dev status", "Show status of the development containers")
    
    # Container management section
    print("\nCONTAINER MANAGEMENT:")
    print_command_help("dev exec <command>", "Execute a command in the development container")
    print_command_help("dev stop", "Stop the development container")
    print_command_help("dev delete", "Delete the development container")
    print_command_help("dev logs", "View logs from the development container")
    
    # Maintenance section
    print("\nMAINTENANCE:")
    print_command_help("dev prune", "Clean up unused Docker resources")
    
    # Help section
    print("\nHELP:")
    print_command_help("dev help", "Display this help message")
    print_command_help("dev help <command>", "Display detailed help for a specific command")
    
    # Footer text
    print("\nFor more information on a specific command, run 'dev help <command>'.")
    print("Example: dev help build\n")


def display_command_help(command_name: str):
    """
    Display detailed help for a specific command.
    
    Args:
        command_name: The name of the command to show help for
    """
    # Dictionary mapping command names to their detailed help
    command_help: Dict[str, str] = {
        "shell": """
        Enter a shell in the development container.
        
        Usage: dev shell
        
        If the container is already running, this will connect to it.
        If the container exists but is not running, it will be started.
        If the container doesn't exist, it will be created with the specified mounts and ports.
        
        Multiple terminal sessions can connect to the same container, allowing for
        parallel work (e.g., editing in one terminal while building in another).
        
        The container will remain running until explicitly stopped with 'dev stop'.
        """,
        
        "build": """
        Build the development container image.
        
        Usage: dev build [--no-cache] [--stage STAGE]
        
        Options:
          --no-cache       Build without using cache
          --stage STAGE    Build stage (full, user, or final)
        
        The build command creates the Docker image that serves as the foundation
        for your development environment. This needs to be run at least once before
        using other commands like 'dev shell'.
        """,
        
        "rebuild": """
        Rebuild the development container image and update plugins.
        
        Usage: dev rebuild [--no-cache] [--with-plugins] [--name NAME]
        
        Options:
          --no-cache       Build without using cache
          --with-plugins   Update Neovim plugins during rebuild
          --name NAME      Container name (default: based on current directory)
        
        This command is useful when you've updated your Neovim configuration
        or need to refresh the container image with new plugins.
        """,
        
        "stop": """
        Stop the development container.
        
        Usage: dev stop [--name NAME]
        
        Options:
          --name NAME      Container name (default: based on current directory)
        
        This gracefully stops the container while preserving its state,
        allowing it to be restarted later with the same configuration.
        """,
        
        "delete": """
        Delete the development container.
        
        Usage: dev delete [--name NAME]
        
        Options:
          --name NAME      Container name (default: based on current directory)
        
        This permanently removes the container and all non-mounted data.
        The container must be stopped first if it's running.
        """,
        
        "status": """
        Show status of the development containers.
        
        Usage: dev status [--name NAME]
        
        Options:
          --name NAME      Container name (default: based on current directory)
        
        Displays detailed information about the container including:
        - Image information
        - Container status
        - Port mappings
        - Volume mounts
        """,
        
        "exec": """
        Execute a command in the development container.
        
        Usage: dev exec [--name NAME] [-i/--interactive] COMMAND [ARGS...]
        
        Options:
          --name NAME       Container name (default: based on current directory)
          -i, --interactive Run in interactive mode
        
        This allows running commands inside a running container without
        starting a full interactive shell. If the container isn't running,
        it will be started automatically.
        
        Example: dev exec python3 script.py
        """,
        
        "logs": """
        View logs from the development container.
        
        Usage: dev logs [--name NAME] [-f/--follow] [--lines LINES]
        
        Options:
          --name NAME       Container name (default: based on current directory)
          -f, --follow      Follow log output
          --lines LINES     Number of lines to show (default: 100)
        
        Displays the output logs from the container, which can be useful
        for troubleshooting or monitoring background processes.
        """,
        
        "prune": """
        Clean up unused Docker resources.
        
        Usage: dev prune [--all] [--volumes]
        
        Options:
          --all             Remove all unused containers, networks, and images
          --volumes         Also remove volumes
        
        This command helps keep your system clean by removing unused
        Docker resources like stopped containers and dangling images.
        """,
        
        "help": """
        Display help information for the development environment.
        
        Usage: dev help [COMMAND]
        
        Options:
          COMMAND           The command to get help for
        
        If no command is specified, displays general help information.
        If a command is specified, displays detailed help for that command.
        
        Example: dev help build
        """
    }
    
    # Check if the command exists in our help dictionary
    if command_name in command_help:
        print(f"\n=== Help: dev {command_name} ===\n")
        # Print the dedented help text
        print(textwrap.dedent(command_help[command_name]).strip())
        print()
    else:
        print(f"\nNo detailed help available for '{command_name}'.")
        print("Run 'dev help' for a list of available commands.\n")


def print_command_help(command: str, description: str):
    """
    Print a formatted command and its description.
    
    Args:
        command: The command syntax
        description: The command description
    """
    print(f"  {command.ljust(25)} {description}")


def setup_help_parser(subparsers):
    """
    Set up the argument parser for the help command.
    
    Args:
        subparsers: The subparser collection to add to
        
    Returns:
        The created subparser
    """
    help_parser = subparsers.add_parser("help", help="Display help information")
    help_parser.add_argument("command_name", nargs="?", help="Command to get help for")
    return help_parser
