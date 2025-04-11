"""
Help command module for the blueprint system.

This module provides comprehensive help information for all blueprint commands,
including general help and command-specific details.
"""

import argparse
import textwrap
from typing import Dict, Optional


def help_command(args):
    """
    Display help information for the blueprint system.
    
    This command provides detailed help for all commands or for a specific
    command when requested. It's designed to make the blueprint system
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
    
    This includes a brief overview of the blueprint system and
    a list of all available commands with their descriptions.
    """
    # Header text
    print("\n=== Blueprint Project Generator ===")
    print("A tool for quickly scaffolding new projects from templates.\n")
    
    # Main commands section
    print("COMMON COMMANDS:")
    print_command_help("blpt list", "List all available blueprints")
    print_command_help("blpt create <blueprint> <project_dir>", "Create a new project from a blueprint")
    print_command_help("blpt info <blueprint>", "Show detailed information about a blueprint")
    
    # Additional information
    print("\nEXAMPLES:")
    print("  Create a C++ project:    blpt create cpp_lite my_app")
    print("  Create a Rust project:   blpt create rust my_rust_project")
    print("  Create a Go project:     blpt create go my_go_service")
    
    # Help section
    print("\nHELP:")
    print_command_help("blpt help", "Display this help message")
    print_command_help("blpt help <command>", "Display detailed help for a specific command")
    
    # Footer text
    print("\nBluprints are stored in ~/.dev/blueprints")
    print("For more information on a specific command, run 'blpt help <command>'.")
    print("Example: blpt help create\n")


def display_command_help(command_name: str):
    """
    Display detailed help for a specific command.
    
    Args:
        command_name: The name of the command to show help for
    """
    # Dictionary mapping command names to their detailed help
    command_help: Dict[str, str] = {
        "list": """
        List all available blueprints.
        
        Usage: blpt list
        
        This command scans the blueprints directory (~/.dev/blueprints) and
        displays all available project templates with a brief description of each.
        
        The output includes:
        - Blueprint name
        - Short description (extracted from README if available)
        
        No arguments are required for this command.
        """,
        
        "create": """
        Create a new project from a blueprint.
        
        Usage: blpt create <blueprint> <project_dir> [--output <path>]
        
        Arguments:
          blueprint      The name of the blueprint to use
          project_dir    The name of the project directory to create
        
        Options:
          --output     Specify an output directory (default: current directory)
        
        This command:
        1. Copies the blueprint files to a new project directory
        2. Replaces template variables with project-specific values
        3. Creates a Dockerfile if the blueprint includes a template
        4. Displays next steps based on the project type
        
        Example: blpt create cpp_lite my_app
        """,
        
        "info": """
        Show detailed information about a blueprint.
        
        Usage: blpt info <blueprint>
        
        Arguments:
          blueprint    The name of the blueprint to get information about
        
        This command displays comprehensive information about a specific blueprint:
        - Description (from README if available)
        - File structure
        - Build system and requirements
        - Available customization options
        - Usage instructions and next steps
        
        Example: blpt info rust
        """,
        
        "help": """
        Display help information.
        
        Usage: blpt help [command]
        
        Arguments:
          command     (Optional) Command to get help for
        
        If a command is specified, displays detailed help for that command.
        If no command is specified, displays general help information.
        
        Example: blpt help create
        """
    }
    
    # Check if the command exists in our help dictionary
    if command_name in command_help:
        print(f"\n=== Help: blpt {command_name} ===\n")
        # Print the dedented help text
        print(textwrap.dedent(command_help[command_name]).strip())
        print()
    else:
        print(f"\nNo detailed help available for '{command_name}'.")
        print("Run 'blpt help' for a list of available commands.\n")


def print_command_help(command: str, description: str):
    """
    Print a formatted command and its description.
    
    Args:
        command: The command syntax
        description: The command description
    """
    print(f"  {command.ljust(40)} {description}")


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
