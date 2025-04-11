#!/usr/bin/env python3
"""
Docker Container Manager
========================

This script manages Docker containers for application development and deployment,
separate from the development environment containers managed by dev.py.

Common commands:
- dkr build               : Build a Docker image from the current directory
- dkr run [options]       : Run a container based on an image
- dkr buildrun [options]  : Build and run in one command
- dkr shell [image]       : Start an interactive shell in a container
- dkr status              : List all running containers
- dkr stop [name]         : Stop running containers
- dkr rm [name]           : Remove containers
- dkr rmi [name]          : Remove images
- dkr logs [name]         : View container logs
- dkr help                : Display helpful information about commands
"""

import argparse
import sys
import os
from pathlib import Path

# Add the script directory to the path so Python can find the dkrcmd package
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import commands from modules
from dkrcmd.build import build_command
from dkrcmd.run import run_command
from dkrcmd.shell import shell_command
from dkrcmd.status import status_command
from dkrcmd.stop import stop_command
from dkrcmd.rm import rm_command
from dkrcmd.rmi import rmi_command
from dkrcmd.logs import logs_command
from dkrcmd.help import help_command, setup_help_parser
from dkrcmd.config import get_default_tag

def main():
    """
    Main entry point for the Docker container manager.
    
    Parses command-line arguments and calls the appropriate command function.
    """
    parser = argparse.ArgumentParser(description="Docker Container Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build a Docker image from current directory")
    build_parser.add_argument("--tag", help="Image name and tag (default: directory name)")
    build_parser.add_argument("--file", help="Path to Dockerfile (default: ./Dockerfile)")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a container based on an image")
    run_parser.add_argument("--name", help="Container name")
    run_parser.add_argument("--image", help="Image to run (default: directory name)")
    run_parser.add_argument("--port", "-p", action="append", help="Port mapping (e.g., 8080:80)")
    run_parser.add_argument("--env", "-e", action="append", help="Environment variables (e.g., KEY=VALUE)")
    
    # Build and run command
    buildrun_parser = subparsers.add_parser("buildrun", help="Build and run in one command")
    buildrun_parser.add_argument("--tag", help="Image name and tag (default: directory name)")
    buildrun_parser.add_argument("--port", "-p", action="append", help="Port mapping (e.g., 8080:80)")
    buildrun_parser.add_argument("--env", "-e", action="append", help="Environment variables (e.g., KEY=VALUE)")
    
    # Shell command
    shell_parser = subparsers.add_parser("shell", help="Start an interactive shell in a container")
    shell_parser.add_argument("--image", help="Image to use (default: directory name)")
    shell_parser.add_argument("--force", "-f", action="store_true", help="Skip security prompt")
    
    # Status command
    subparsers.add_parser("status", help="List all running containers")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop running containers")
    stop_parser.add_argument("--name", help="Container name")
    
    # Remove container command
    rm_parser = subparsers.add_parser("rm", help="Remove containers")
    rm_parser.add_argument("--name", help="Container name")
    rm_parser.add_argument("--all", action="store_true", help="Remove all containers")
    
    # Remove image command
    rmi_parser = subparsers.add_parser("rmi", help="Remove images")
    rmi_parser.add_argument("--name", help="Image name")
    rmi_parser.add_argument("--all", action="store_true", help="Remove all images")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View container logs")
    logs_parser.add_argument("--name", help="Container name")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
    logs_parser.add_argument("--lines", type=int, default=100, help="Number of lines to show")
    
    # Help command
    help_parser = setup_help_parser(subparsers)
    
    args = parser.parse_args()
    
    # If no command is provided, display help
    if not args.command:
        parser.print_help()
        return
    
    # Handle buildrun command directly here instead of a separate module
    if args.command == "buildrun":
        return buildrun_command(args)
    
    # Handle shell command with safety prompt
    if args.command == "shell" and not args.force:
        print("\n⚠️  SECURITY WARNING:")
        print("Using shell in containers is primarily for debugging and not recommended for production.")
        print("Production containers often (intentionally) don't include shell access for security reasons.")
        
        response = input("Are you intentionally using this for debugging? [y/N]: ").strip().lower()
        if response != 'y' and response != 'yes':
            print("Operation cancelled. If you're sure you want to proceed, use --force flag.")
            return False
    
    # Execute the appropriate command
    commands = {
        "build": build_command,
        "run": run_command,
        "shell": shell_command,
        "status": status_command,
        "stop": stop_command,
        "rm": rm_command,
        "rmi": rmi_command,
        "logs": logs_command,
        "help": help_command
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        parser.print_help()

def buildrun_command(args):
    """
    Build a Docker image and immediately run a container from it.
    
    This command:
    1. Calls the build command to create an image
    2. If successful, calls the run command to start a container
    
    Args:
        args: Command-line arguments containing:
            - tag: Optional image name and tag
            - port: Optional port mappings
            - env: Optional environment variables
    """
    # Create build args by copying the original args
    build_args = argparse.Namespace(
        tag=args.tag,
        file=None  # Use default Dockerfile
    )
    
    print("=== Step 1: Building Docker Image ===")
    
    # Attempt to build the image
    build_success = build_command(build_args)
    
    if not build_success:
        print("\n❌ Build failed. Skipping container creation.")
        return False
    
    print("\n=== Step 2: Running Container ===")
    
    # Create run args
    run_args = argparse.Namespace(
        image=args.tag if args.tag else get_default_tag(),
        name=None,  # Generate a random name
        port=args.port,
        env=args.env
    )
    
    # Run the container
    run_success = run_command(run_args)
    
    if not run_success:
        print("\n❌ Container run failed.")
        return False
    
    return True

if __name__ == "__main__":
    main()
