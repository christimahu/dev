#!/usr/bin/env python3
"""
Development Environment Manager
==============================

This script manages a Docker-based development environment, creating a consistent
development experience across different machines.

Common commands:
- dev               : Enter a shell in the development container
- dev build         : Build the development container image
- dev status        : Show status of the development containers
- dev exec [command]: Execute a command in the development container
- dev stop          : Stop the development container
- dev delete        : Delete the development container
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import hashlib

# Configuration
IMAGE_NAME = "christi-dev"
IMAGE_TAG = "latest"
HOME_DIR = str(Path.home())
DEV_DIR = os.path.join(HOME_DIR, "dev")

# Check if running from dev directory
if os.path.basename(os.getcwd()) == "dev" and os.path.exists(os.path.join(os.getcwd(), "scripts", "dev.py")):
    DEV_DIR = os.getcwd()

def run_command(cmd, capture_output=True, text=True, check=True):
    """Run a shell command and return its output."""
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
    """Generate a container name based on the current directory."""
    current_dir = os.getcwd()
    if current_dir != DEV_DIR:
        dir_hash = hashlib.md5(current_dir.encode()).hexdigest()[:8]
        return f"dev-{dir_hash}"
    return "dev-main"

def container_exists(container_name):
    """Check if a container with the given name exists."""
    result = run_command(["docker", "ps", "-a", "-q", "-f", f"name={container_name}"], check=False)
    return bool(result)

def container_running(container_name):
    """Check if a container with the given name is running."""
    result = run_command(["docker", "ps", "-q", "-f", f"name={container_name}"], check=False)
    return bool(result)

def parse_custom_env_file(env_file):
    """Parse a custom environment file for port mappings and environment variables."""
    result = {'ports': [], 'env_vars': {}}
    
    if not os.path.exists(env_file):
        print(f"Notice: {env_file} not found.")
        print(f"Create it based on custom_example.env for custom port mappings.")
        return result
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line:
                key, value = [part.strip() for part in line.split('=', 1)]
                
                if key.startswith('PORT_') and ':' in value:
                    # Special handling for port mappings to avoid any spacing issues
                    host_port, container_port = [p.strip() for p in value.split(':', 1)]
                    # Format directly without spaces
                    port_arg = f"-p{host_port}:{container_port}"
                    result['ports'].append(port_arg)
                else:
                    result['env_vars'][key] = value
    
    return result

def shell_command(args):
    """Enter a shell in the development container."""
    container_name = get_container_name()
    current_dir = os.getcwd()
    
    # If container doesn't exist, create it
    if not container_exists(container_name):
        print(f"Creating new development container: {container_name}")
        
        # Determine bind mount paths
        if current_dir == DEV_DIR:
            work_dir = "/home/me/dev"
            mounts = [
                f"-v {DEV_DIR}:{work_dir}",
                f"-v {HOME_DIR}/.ssh:/home/me/.ssh:ro",
                f"-v {HOME_DIR}/.gitconfig:/home/me/.gitconfig:ro"
            ]
        else:
            work_dir = "/workdir"
            mounts = [
                f"-v {DEV_DIR}:/home/me/dev",
                f"-v {current_dir}:{work_dir}",
                f"-v {HOME_DIR}/.ssh:/home/me/.ssh:ro",
                f"-v {HOME_DIR}/.gitconfig:/home/me/.gitconfig:ro"
            ]
        
        # Initialization script
        init_script = """
        mkdir -p /home/me/.config/nvim
        ln -sf /home/me/dev/config/init.lua /home/me/.config/nvim/init.lua
        echo "source /home/me/dev/config/shell_functions" >> /home/me/.bashrc
        """

        # Read custom environment
        env_file = os.path.join(DEV_DIR, "custom.env")
        custom_env = parse_custom_env_file(env_file)
        
        # Create and start the container
        cmd = ["docker", "run", "-d", "-it", "--name", container_name]
        cmd.extend(mounts)
        if custom_env['ports']:
            cmd.extend(custom_env['ports'])
        cmd.extend(["--network", "bridge", "--cap-add=SYS_PTRACE", "--security-opt", "seccomp=unconfined"])
        
        # Add environment variables
        for key, value in custom_env['env_vars'].items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Set working directory and image
        cmd.extend(["--workdir", work_dir, f"{IMAGE_NAME}:{IMAGE_TAG}"])
        
        # Run the container
        run_command(cmd)
        
        # Run initialization script
        run_command(["docker", "exec", container_name, "bash", "-c", init_script])
    
    # If container exists but is not running, start it
    elif not container_running(container_name):
        print(f"Starting existing container: {container_name}")
        run_command(["docker", "start", container_name])
    
    # Execute interactive shell
    print(f"Connecting to development container: {container_name}")
    os.system(f"docker exec -it {container_name} /bin/bash")

def build_command(args):
    """Build the development container image."""
    build_args = ["docker", "build"]
    
    if args.no_cache:
        build_args.append("--no-cache")
    
    if args.stage == "full":
        build_args.extend(["-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."])
    elif args.stage == "user":
        build_args.extend(["--target", "user-setup", "-t", f"{IMAGE_NAME}:user-stage", "."])
        build_args = ["docker", "build", "--target", "dev-environment", 
                     "--build-arg", "BASE_IMAGE=user-stage",
                     "-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."]
    elif args.stage == "final":
        build_args.extend(["--target", "dev-environment", 
                          "-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."])
    
    print(f"Building container image: {' '.join(build_args)}")
    os.chdir(DEV_DIR)  # Ensure correct build context
    
    result = subprocess.run(build_args)
    
    if result.returncode == 0:
        print("\n✅ Build completed successfully!")
        print("You can now run 'dev' to enter the development environment.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

def stop_command(args):
    """Stop the development container."""
    container_name = args.name if args.name else get_container_name()
    
    if container_running(container_name):
        print(f"Stopping container: {container_name}")
        run_command(["docker", "stop", container_name])
    else:
        print(f"Container {container_name} is not running.")

def delete_command(args):
    """Delete the development container."""
    container_name = args.name if args.name else get_container_name()
    
    if container_exists(container_name):
        if container_running(container_name):
            print(f"Stopping container: {container_name}")
            run_command(["docker", "stop", container_name])
        
        print(f"Removing container: {container_name}")
        run_command(["docker", "rm", container_name])
    else:
        print(f"Container {container_name} does not exist.")

def status_command(args):
    """Show status of the development containers."""
    container_name = args.name if args.name else get_container_name()
    
    print("\nDevelopment Environment Status:")
    print("=" * 40)
    
    # Check image
    image_info = run_command(["docker", "images", "-q", f"{IMAGE_NAME}:{IMAGE_TAG}"], check=False)
    if image_info:
        image_details = run_command(["docker", "image", "inspect", "-f", "{{.Created}}", f"{IMAGE_NAME}:{IMAGE_TAG}"], check=False)
        print(f"Image: {IMAGE_NAME}:{IMAGE_TAG} (Created: {image_details})")
    else:
        print(f"Image: {IMAGE_NAME}:{IMAGE_TAG} (Not found)")
    
    # Check container
    if container_exists(container_name):
        status = "Running" if container_running(container_name) else "Stopped"
        details = run_command([
            "docker", "inspect", 
            "-f", "{{.Config.Image}} | {{.State.StartedAt}} | {{.NetworkSettings.IPAddress}}", 
            container_name
        ], check=False)
        
        if details:
            image, started, ip = details.split(" | ")
            print(f"Container: {container_name} ({status})")
            print(f"Started: {started}")
            print(f"IP Address: {ip}")
            
            # Get port mappings
            port_info = run_command([
                "docker", "inspect", 
                "-f", "{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{println}}{{end}}", 
                container_name
            ], check=False)
            
            if port_info:
                print("Port Mappings:")
                for line in port_info.split("\n"):
                    if line.strip():
                        print(f"  {line}")
    else:
        print(f"Container: {container_name} (Not found)")
    
    print("=" * 40)

def exec_command(args):
    """Execute a command in the development container."""
    container_name = args.name if args.name else get_container_name()
    
    if not container_running(container_name):
        print(f"Container {container_name} is not running.")
        if container_exists(container_name):
            print(f"Starting container {container_name}...")
            run_command(["docker", "start", container_name])
        else:
            print("Please create and start the container first.")
            return
    
    cmd = ["docker", "exec"]
    if args.interactive:
        cmd.append("-it")
    cmd.append(container_name)
    
    if isinstance(args.command, list):
        cmd.extend(args.command)
    else:
        cmd.extend(["bash", "-c", args.command])
    
    subprocess.run(cmd)

def logs_command(args):
    """View logs from the development container."""
    container_name = args.name if args.name else get_container_name()
    
    if container_exists(container_name):
        cmd = ["docker", "logs"]
        if args.follow:
            cmd.append("-f")
        if args.lines:
            cmd.extend(["--tail", str(args.lines)])
        cmd.append(container_name)
        subprocess.run(cmd)
    else:
        print(f"Container {container_name} does not exist.")

def prune_command(args):
    """Clean up unused Docker resources."""
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

def main():
    """Main entry point for the development environment manager."""
    parser = argparse.ArgumentParser(description="Development Environment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Shell command
    subparsers.add_parser("shell", help="Enter a shell in the development container")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build the development container image")
    build_parser.add_argument("--no-cache", action="store_true", help="Build without using cache")
    build_parser.add_argument("--stage", choices=["full", "user", "final"], default="full", 
                            help="Build stage (full, user, or final)")
    
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
    
    args = parser.parse_args()
    
    # If no command is provided, default to shell
    if not args.command:
        shell_command(args)
        return
    
    # Execute the appropriate command
    commands = {
        "shell": shell_command,
        "build": build_command,
        "stop": stop_command,
        "delete": delete_command,
        "status": status_command,
        "exec": exec_command,
        "logs": logs_command,
        "prune": prune_command
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
