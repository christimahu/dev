"""
Help command module for the Docker container manager.

This module provides comprehensive help information for all Docker commands,
including general help and command-specific details.
"""

import argparse
import textwrap
from typing import Dict, Optional


def help_command(args):
    """
    Display help information for the Docker container manager.
    
    This command provides detailed help for all commands or for a specific
    command when requested. It's designed to make the Docker container manager
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
    
    This includes a brief overview of the Docker container manager and
    a list of all available commands with their descriptions.
    """
    # Header text
    print("\n=== Docker Container Manager ===")
    print("A tool for managing Docker containers for application development.")
    print("Separate from the dev environment containers managed by dev.py.\n")
    
    # Main commands section
    print("CONTAINER MANAGEMENT:")
    print_command_help("dkr build", "Build a Docker image from the current directory")
    print_command_help("dkr run", "Run a container based on an image")
    print_command_help("dkr buildrun", "Build and run in one command")
    print_command_help("dkr shell", "Start an interactive shell in a container")
    
    print("\nCONTAINER LIFECYCLE:")
    print_command_help("dkr status", "List all running containers")
    print_command_help("dkr stop", "Stop running containers")
    print_command_help("dkr rm", "Remove containers")
    print_command_help("dkr rmi", "Remove images")
    print_command_help("dkr logs", "View container logs")
    
    # Help section
    print("\nHELP:")
    print_command_help("dkr help", "Display this help message")
    print_command_help("dkr help <command>", "Display detailed help for a specific command")
    
    # Footer text
    print("\nFor more information on a specific command, run 'dkr help <command>'.")
    print("Example: dkr help build\n")


def display_command_help(command_name: str):
    """
    Display detailed help for a specific command.
    
    Args:
        command_name: The name of the command to show help for
    """
    # Dictionary mapping command names to their detailed help
    command_help: Dict[str, str] = {
        "build": """
        Build a Docker image from the current directory.
        
        Usage: dkr build [--tag <n>] [--file <path>]
        
        Options:
          --tag     Image name and tag (default: directory name)
          --file    Path to Dockerfile (default: ./Dockerfile)
        
        This command:
        1. Uses the Dockerfile in the current directory (or the one specified with --file)
        2. Tags the image with the name provided (or generates one from the current directory)
        3. Builds the image using Docker
        
        Example: dkr build --tag myapp:1.0
        """,
        
        "run": """
        Run a container based on an image.
        
        Usage: dkr run [--name <n>] [--image <img>] [--port <p>] [--env <e>]
        
        Options:
          --name     Container name (auto-generated if not specified)
          --image    Image to run (default: directory name)
          --port/-p  Port mapping (e.g., 8080:80) - can be specified multiple times
          --env/-e   Environment variable (e.g., KEY=VALUE) - can be specified multiple times
        
        This command:
        1. Uses the specified image (or generates one from the current directory)
        2. Creates a container with the provided options
        3. Runs the container interactively
        
        Example: dkr run --image myapp:1.0 --port 8080:80 --env DEBUG=1
        """,
        
        "buildrun": """
        Build a Docker image and immediately run a container from it.
        
        Usage: dkr buildrun [--tag <t>] [--port <p>] [--env <e>]
        
        Options:
          --tag      Image name and tag (default: directory name)
          --port/-p  Port mapping (e.g., 8080:80) - can be specified multiple times
          --env/-e   Environment variable (e.g., KEY=VALUE) - can be specified multiple times
        
        This command:
        1. Builds an image using the Dockerfile in the current directory
        2. Immediately runs a container from the newly built image
        
        Example: dkr buildrun --tag myapp:1.0 --port 8080:80
        """,
        
        "shell": """
        Start an interactive shell in a container.
        
        Usage: dkr shell [--image <img>] [--force/-f]
        
        Options:
          --image    Image to use (default: directory name)
          --force/-f Skip security prompt
        
        This command:
        1. Creates a temporary container from the specified image
        2. Starts an interactive shell (/bin/bash or /bin/sh)
        3. Removes the container when you exit the shell
        
        WARNING: This command is primarily for debugging purposes.
        Production containers often do not have shell access for security reasons.
        
        Example: dkr shell --image myapp:1.0
        """,
        
        "status": """
        List all running containers.
        
        Usage: dkr status
        
        This command displays:
        1. Running containers
        2. Stopped containers
        3. Available images
        
        The output excludes development containers managed by dev.py.
        
        Example: dkr status
        """,
        
        "stop": """
        Stop running containers.
        
        Usage: dkr stop [--name <n>]
        
        Options:
          --name    Container name to stop
        
        This command:
        1. If a name is provided, stops that specific container
        2. If no name is provided, shows an interactive menu to select containers to stop
        
        Example: dkr stop --name mycontainer
        """,
        
        "rm": """
        Remove containers.
        
        Usage: dkr rm [--name <n>] [--all]
        
        Options:
          --name    Container name to remove
          --all     Remove all containers (excluding dev containers)
        
        This command:
        1. If a name is provided, removes that specific container
        2. If --all is specified, removes all containers (excluding dev containers)
        3. If no name is provided, shows an interactive menu to select containers to remove
        
        Example: dkr rm --name mycontainer
        """,
        
        "rmi": """
        Remove Docker images.
        
        Usage: dkr rmi [--name <n>] [--all]
        
        Options:
          --name    Image name to remove
          --all     Remove all images (excluding dev images)
        
        This command:
        1. If a name is provided, removes that specific image
        2. If --all is specified, removes all images (excluding dev images)
        3. If no name is provided, shows an interactive menu to select images to remove
        
        Example: dkr rmi --name myapp:1.0
        """,
        
        "logs": """
        View container logs.
        
        Usage: dkr logs [--name <n>] [--follow/-f] [--lines <l>]
        
        Options:
          --name      Container name to show logs for
          --follow/-f Follow log output
          --lines     Number of lines to show (default: 100)
        
        This command:
        1. If a name is provided, shows logs for that specific container
        2. If no name is provided, shows an interactive menu to select a container
        3. Displays the specified number of log lines
        4. Optionally follows the log output in real-time
        
        Example: dkr logs --name mycontainer --follow
        """,
        
        "help": """
        Display help information.
        
        Usage: dkr help [command]
        
        Arguments:
          command    (Optional) Name of the command to get help for
        
        This command:
        1. If a command is specified, displays detailed help for that command
        2. If no command is specified, displays general help information
        
        Example: dkr help build
        """
    }
    
    # Check if the command exists in our help dictionary
    if command_name in command_help:
        print(f"\n=== Help: dkr {command_name} ===\n")
        # Print the dedented help text
        print(textwrap.dedent(command_help[command_name]).strip())
        print()
    else:
        print(f"\nNo detailed help available for '{command_name}'.")
        print("Run 'dkr help' for a list of available commands.\n")


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
