#!/usr/bin/env python3
"""
Development Environment Setup Script
====================================

This script prepares your host system for using the containerized development environment.
It does NOT build the Docker container itself - that's handled by the 'dev build' command.

What this script DOES:
1. Sets up symlinks for configuration files (NeoVim, shell configs)
2. Creates a default dev.env file if it doesn't exist
3. Configures shell integration by adding the 'dev' command alias

What this script does NOT do:
1. Build the Docker container (use 'dev build' for that after setup)
2. Install software packages (Docker, Python, Git are prerequisites)

Usage:
    cd ~/.dev/scripts
    python3 setup.py

After running this script, you'll need to:
1. Source your shell configuration: source ~/.bashrc or source ~/.zshrc
2. Build the container: dev build
3. Start using the environment: dev
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Configuration
# These paths define where our files are located and where symlinks should point
DEV_DIR = str(Path.home() / ".dev")  # Main development directory
CONFIG_DIR = os.path.join(DEV_DIR, "config")  # Configuration files

def run_command(cmd, cwd=None, check=True, capture_output=False):
    """
    Run a shell command and return its output.
    
    This is a utility function that handles running external commands
    and provides consistent error handling.
    
    Args:
        cmd: List containing the command and its arguments
        cwd: Working directory to run the command in
        check: Whether to exit on command failure
        capture_output: Whether to capture and return command output
        
    Returns:
        Boolean indicating success or failure
    """
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
    """
    Create a symlink, handling existing files by backing them up.
    
    This allows us to link configuration files without destroying
    existing user configurations.
    
    Args:
        source: Path to the source file
        target: Path where the symlink should be created
        
    Returns:
        Boolean indicating success or failure
    """
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
    """
    Set up symlinks for configuration files.
    
    This includes:
    - NeoVim configuration (init.lua)
    - Shell configuration (.bashrc or .zshrc)
    
    These symlinks ensure that your configurations are used both on the host
    system and inside the container, providing a consistent experience.
    """
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

def setup_dev_env_file():
    """
    Create a default dev.env file if it doesn't exist.
    
    This provides a starting point for users to customize their
    container settings.
    """
    print("\n=== Setting up dev.env configuration ===")
    
    example_env_path = os.path.join(DEV_DIR, "dev_example.env")
    custom_env_path = os.path.join(DEV_DIR, "dev.env")
    
    if os.path.exists(custom_env_path):
        print(f"dev.env already exists at {custom_env_path}")
        print("You may want to check for new options in dev_example.env")
    else:
        if os.path.exists(example_env_path):
            print(f"Creating dev.env from example")
            shutil.copy2(example_env_path, custom_env_path)
            print(f"Created {custom_env_path}")
            print("Review and customize this file for your environment")
        else:
            print(f"Warning: Could not find {example_env_path}")
            print("Please create dev.env manually")
    
    print("Environment configuration setup complete.")

def setup_nvim_packer():
    """
    Set up Neovim's Packer plugin manager if it's not already installed.
    
    This ensures plugins can be installed when Neovim is launched,
    both on the host and in the container.
    """
    print("\n=== Setting up Neovim Packer ===")
    
    home_dir = str(Path.home())
    packer_path = os.path.join(home_dir, ".local", "share", "nvim", "site", "pack", "packer", "start", "packer.nvim")
    
    if os.path.exists(packer_path):
        print("Packer is already installed")
    else:
        print("Installing Packer for Neovim")
        # Create the directory structure
        os.makedirs(os.path.dirname(packer_path), exist_ok=True)
        
        # Clone the Packer repository
        run_command([
            "git", "clone", "--depth", "1",
            "https://github.com/wbthomason/packer.nvim", packer_path
        ])
        
        # Check if nvim is available and attempt a headless plugin installation
        if shutil.which("nvim"):
            print("Installing plugins with Packer (this may take a moment)...")
            try:
                run_command([
                    "nvim", "--headless", 
                    "-c", "autocmd User PackerComplete quitall", 
                    "-c", "PackerSync"
                ], check=False)
                print("Plugin installation initiated. Some plugins may need manual installation.")
            except Exception as e:
                print(f"Could not install plugins automatically: {e}")
                print("Launch nvim and run :PackerSync manually to install plugins.")
        else:
            print("Neovim not found in PATH. Launch nvim and run :PackerSync manually to install plugins.")
    
    print("Neovim Packer setup complete.")

def setup_shell_integration():
    """
    Set up shell integration for easier use of the development tools.
    
    This adds a 'dev' command alias to your shell configuration, allowing you to:
    - Enter the development environment: dev
    - Build the container: dev build
    - Check status: dev status
    - And use other dev commands
    """
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
                print(f"You'll need to run 'source {shell_rc}' to use the alias in this session")
    
    # Make dev.py executable
    dev_py_path = os.path.join(DEV_DIR, "scripts", "dev.py")
    if os.path.exists(dev_py_path):
        os.chmod(dev_py_path, 0o755)
        print(f"Made {dev_py_path} executable")
    
    print("Shell integration setup complete.")

def detect_shell():
    """
    Detect the current shell being used.
    
    Returns:
        'zsh' for Zsh shell, 'bash' for Bash shell, or 'bash' as a fallback
    """
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    else:
        # Default to bash if we can't detect
        return "bash"

def check_prerequisites():
    """
    Check if all prerequisites are installed.
    
    Required software:
    - Docker: For containerized environment
    - Python 3: For running scripts
    - Git: For version control
    
    Returns:
        Boolean indicating if all prerequisites are met
    """
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
        print(f"⚠️ The following prerequisites are missing: {', '.join(missing)}")
        print("Please install them before continuing. See README.md for instructions.")
        return False
    
    print("✓ All prerequisites are installed.")
    return True

def main():
    """
    Main function to run the setup.
    
    This is the entry point for the setup script, which:
    1. Checks prerequisites
    2. Sets up configuration symlinks
    3. Creates a default dev.env if needed
    4. Sets up Neovim with Packer
    5. Configures shell integration
    
    Note: It does NOT build the Docker container - that's done separately with 'dev build'
    """
    print("=== Development Environment Setup ===")
    print("This script prepares your host system for using the development environment.")
    print("After this completes, you'll need to run 'dev build' to build the Docker container.")
    
    # Check if the script is running from the dev directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not script_dir.endswith(os.path.join(".dev", "scripts")):
        print("This script should be run from the .dev/scripts directory.")
        print(f"Current directory: {script_dir}")
        print("Please run: cd ~/.dev/scripts && python3 setup.py")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Perform setup steps
    setup_config_symlinks()
    setup_dev_env_file()
    setup_nvim_packer()
    setup_shell_integration()
    
    print("\n=== 🎉 Setup complete! ===")
    print("\nNext steps:")
    print("1. Source your shell configuration:")
    if detect_shell() == "zsh":
        print("   source ~/.zshrc")
    else:
        print("   source ~/.bashrc")
    print("\n2. Build the development container:")
    print("   dev build")
    print("\n3. Enter the development environment:")
    print("   cd ~/your-project")
    print("   dev")
    print("\nFor more information, see the README.md")

if __name__ == "__main__":
    main()
