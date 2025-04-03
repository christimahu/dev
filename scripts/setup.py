#!/usr/bin/env python3
"""
Setup script for the development environment.

This script:
1. Sets up symlinks for configuration files
2. Builds the Docker image
3. Compiles tools
4. Configures shell integration
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Configuration
DEV_DIR = str(Path.home() / "dev")
CONFIG_DIR = os.path.join(DEV_DIR, "config")
TOOLS_DIR = os.path.join(DEV_DIR, "tools")
SRV_DIR = os.path.join(TOOLS_DIR, "srv")

def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Run a shell command and return its output."""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=check, 
            text=True, 
            capture_output=capture_output
        )
        
        if not capture_output:
            # If not capturing output, let it flow to stdout/stderr in real-time
            return result.returncode == 0
        else:
            # If capturing output, print it after the command completes
            if result.stdout:
                print(result.stdout)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"Error message: {e.stderr if e.stderr else str(e)}")
        if check:
            sys.exit(1)
        return False

def create_symlink(source, target):
    """Create a symlink, handling existing files."""
    source_path = os.path.abspath(source)
    target_path = os.path.abspath(target)
    
    # Create target directory if it doesn't exist
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)
    
    # Handle existing file/symlink
    if os.path.exists(target_path) or os.path.islink(target_path):
        if os.path.islink(target_path):
            existing_link = os.readlink(target_path)
            if existing_link == source_path:
                print(f"Symlink already exists: {target_path} -> {source_path}")
                return True
            
        backup_path = f"{target_path}.backup"
        print(f"Backing up existing file to {backup_path}")
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(target_path, backup_path)
        except Exception as e:
            print(f"Failed to backup file: {e}")
            return False
    
    # Create the symlink
    try:
        print(f"Creating symlink: {target_path} -> {source_path}")
        os.symlink(source_path, target_path)
        return True
    except Exception as e:
        print(f"Failed to create symlink: {e}")
        return False

def setup_config_symlinks():
    """Set up symlinks for configuration files."""
    print("\n=== Setting up configuration symlinks ===")
    
    # Determine home directory
    home_dir = str(Path.home())
    
    # Create config directory if it doesn't exist
    nvim_config_dir = os.path.join(home_dir, ".config", "nvim")
    os.makedirs(nvim_config_dir, exist_ok=True)
    
    # Set up Neovim config symlink
    init_lua_source = os.path.join(CONFIG_DIR, "init.lua")
    init_lua_target = os.path.join(nvim_config_dir, "init.lua")
    create_symlink(init_lua_source, init_lua_target)
    
    # Detect shell type
    shell_type = detect_shell()
    
    # Set up shell config
    if shell_type == "zsh":
        shell_source = os.path.join(CONFIG_DIR, "zshrc")
        shell_target = os.path.join(home_dir, ".zshrc")
        create_backup = True
        
        # Check if .zshrc already sources our config
        if os.path.exists(shell_target):
            with open(shell_target, 'r') as f:
                content = f.read()
                if f"source {CONFIG_DIR}/shell_functions" in content:
                    print(f".zshrc already sources shell_functions")
                    create_backup = False
        
        if create_backup:
            # Append to existing .zshrc instead of replacing
            if os.path.exists(shell_target):
                backup_path = f"{shell_target}.backup"
                print(f"Backing up existing .zshrc to {backup_path}")
                shutil.copy2(shell_target, backup_path)
                
                # Append source command to .zshrc
                with open(shell_target, 'a') as f:
                    f.write(f"\n# Added by dev setup script\n")
                    f.write(f"source {CONFIG_DIR}/shell_functions\n")
            else:
                # Create new .zshrc that sources our config
                with open(shell_target, 'w') as f:
                    f.write(f"# Created by dev setup script\n")
                    f.write(f"source {CONFIG_DIR}/shell_functions\n")
    
    elif shell_type == "bash":
        shell_source = os.path.join(CONFIG_DIR, "bashrc")
        shell_target = os.path.join(home_dir, ".bashrc")
        create_backup = True
        
        # Check if .bashrc already sources our config
        if os.path.exists(shell_target):
            with open(shell_target, 'r') as f:
                content = f.read()
                if f"source {CONFIG_DIR}/shell_functions" in content:
                    print(f".bashrc already sources shell_functions")
                    create_backup = False
        
        if create_backup:
            # Append to existing .bashrc instead of replacing
            if os.path.exists(shell_target):
                backup_path = f"{shell_target}.backup"
                print(f"Backing up existing .bashrc to {backup_path}")
                shutil.copy2(shell_target, backup_path)
                
                # Append source command to .bashrc
                with open(shell_target, 'a') as f:
                    f.write(f"\n# Added by dev setup script\n")
                    f.write(f"source {CONFIG_DIR}/shell_functions\n")
            else:
                # Create new .bashrc that sources our config
                with open(shell_target, 'w') as f:
                    f.write(f"# Created by dev setup script\n")
                    f.write(f"source {CONFIG_DIR}/shell_functions\n")
    
    print("Configuration symlinks setup complete.")

def build_docker_image():
    """Build the Docker image for the development environment."""
    print("\n=== Building Docker image ===")
    
    # Check if Docker is installed
    if not shutil.which("docker"):
        print("Docker is not installed. Please install Docker first.")
        return False
    
    # Build the Docker image - capture_output=False to show output in real-time
    build_cmd = ["docker", "build", "-t", "christi-dev:latest", "."]
    return run_command(build_cmd, cwd=DEV_DIR, capture_output=False)

def build_tools():
    """Build the tools needed for the development environment."""
    print("\n=== Building tools ===")
    
    # Build the srv tool if it exists
    if os.path.exists(SRV_DIR):
        print("Building srv tool...")
        # Check if Cargo is installed
        if not shutil.which("cargo"):
            print("Cargo is not installed. Please install Rust first.")
            return False
        
        # Build the srv tool - capture_output=False to show output in real-time
        return run_command(["cargo", "build", "--release"], cwd=SRV_DIR, capture_output=False)
    else:
        print("srv tool directory not found, skipping build.")
        return True

def setup_shell_integration():
    """Setup shell integration for easier use of the dev tools."""
    print("\n=== Setting up shell integration ===")
    
    # Create alias for dev.py
    shell_type = detect_shell()
    shell_rc = os.path.join(str(Path.home()), f".{shell_type}rc")
    
    if os.path.exists(shell_rc):
        with open(shell_rc, 'r') as f:
            content = f.read()
            if "alias dev=" in content:
                print(f"dev alias already exists in {shell_rc}")
            else:
                # Append alias to shell rc file
                with open(shell_rc, 'a') as f:
                    f.write(f"\n# Added by dev setup script\n")
                    f.write(f'alias dev="python3 {os.path.join(DEV_DIR, "scripts", "dev.py")}"\n')
                print(f"Added dev alias to {shell_rc}")
    
    # Make dev.py executable
    dev_py_path = os.path.join(DEV_DIR, "scripts", "dev.py")
    if os.path.exists(dev_py_path):
        os.chmod(dev_py_path, 0o755)
        print(f"Made {dev_py_path} executable")
    
    print("Shell integration setup complete.")

def detect_shell():
    """Detect the current shell."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    else:
        # Default to bash if we can't detect
        return "bash"

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("\n=== Checking prerequisites ===")
    
    missing = []
    
    # Check for Docker
    if not shutil.which("docker"):
        missing.append("Docker")
    
    # Check for Python 3
    if not shutil.which("python3"):
        missing.append("Python 3")
    
    # Check for Git
    if not shutil.which("git"):
        missing.append("Git")
    
    if missing:
        print(f"The following prerequisites are missing: {', '.join(missing)}")
        print("Please install them before continuing.")
        return False
    
    print("All prerequisites are installed.")
    return True

def main():
    """Main function to run the setup."""
    print("=== Development Environment Setup ===")
    
    # Check if the script is running from the dev directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not script_dir.endswith(os.path.join("dev", "scripts")):
        print("This script should be run from the dev/scripts directory.")
        print(f"Current directory: {script_dir}")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Perform setup steps
    setup_config_symlinks()
    if build_docker_image():
        build_tools()
        setup_shell_integration()
        
        print("\n=== Setup complete! ===")
        print("You can now use the development environment by running:")
        print("  dev")
        print("From any directory on your system.")
    else:
        print("\n=== Setup incomplete ===")
        print("Docker image build failed. Please check the error messages and try again.")

if __name__ == "__main__":
    main()
