#!/usr/bin/env python3
"""
Blueprint System for Development Projects
========================================

This script manages project templates (blueprints) for quickly scaffolding
new development projects with proper structure and configuration.

Common commands:
- blpt list                : List available blueprints
- blpt create <name> <dir> : Create a project from a blueprint
- blpt info <name>         : Show information about a blueprint
- blpt help                : Display helpful information about commands
"""

import argparse
import sys
import os
from pathlib import Path

# Add the script directory to the path so Python can find the blptcmd package
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import commands from modules (will be created next)
# from blptcmd.list import list_command
# from blptcmd.create import create_command
# from blptcmd.info import info_command
# from blptcmd.help import help_command, setup_help_parser

def main():
    """
    Main entry point for the blueprint manager.
    
    Parses command-line arguments and calls the appropriate command function.
    """
    parser = argparse.ArgumentParser(description="Blueprint Manager for Project Scaffolding")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    subparsers.add_parser("list", help="List available blueprints")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a project from a blueprint")
    create_parser.add_argument("blueprint", help="Blueprint name (e.g., cpp, rust, go)")
    create_parser.add_argument("project_dir", help="Project directory name")
    create_parser.add_argument("--output", help="Output directory (default: current directory)")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about a blueprint")
    info_parser.add_argument("blueprint", help="Blueprint name (e.g., cpp, rust, go)")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Display help information")
    help_parser.add_argument("command_name", nargs="?", help="Command to get help for")
    
    args = parser.parse_args()
    
    # If no command is provided, display help
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    commands = {
        "list": lambda _: print("List command - will call list_command(args)"),
        "create": lambda _: print(f"Create command - will call create_command(args) for {args.blueprint} to {args.project_dir}"),
        "info": lambda _: print(f"Info command - will call info_command(args) for {args.blueprint}"),
        "help": lambda _: print("Help command - will call help_command(args)")
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
