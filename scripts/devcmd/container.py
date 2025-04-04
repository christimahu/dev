"""
Container management functions for the development environment.
"""

import os
import subprocess
from .config import DEV_DIR
from .utils import run_command, get_container_name, container_exists, container_running, parse_dev_env_file

def stop_command(args):
    """
    Stop the development container.
    
    Args:
        args: Command-line arguments
    """
    container_name = args.name if args.name else get_container_name()
    
    if container_running(container_name):
        print(f"Stopping container: {container_name}")
        run_command(["docker", "stop", container_name])
    else:
        print(f"Container {container_name} is not running.")

def delete_command(args):
    """
    Delete the development container.
    
    Args:
        args: Command-line arguments
    """
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
    """
    Show status of the development containers.
    
    Args:
        args: Command-line arguments
    """
    from .config import IMAGE_NAME, IMAGE_TAG
    
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
                
            # Get mount info
            mount_info = run_command([
                "docker", "inspect", 
                "-f", "{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}", 
                container_name
            ], check=False)
            
            if mount_info:
                print("Volume Mounts:")
                for line in mount_info.split("\n"):
                    if line.strip():
                        print(f"  {line}")
    else:
        print(f"Container: {container_name} (Not found)")
    
    print("=" * 40)

def exec_command(args):
    """
    Execute a command in the development container.
    
    Args:
        args: Command-line arguments
    """
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
    """
    View logs from the development container.
    
    Args:
        args: Command-line arguments
    """
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
