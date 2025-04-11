"""
Info command module for the blueprint system.

This module handles the 'info' command which displays detailed information
about a specific blueprint.
"""

import os
import sys
from pathlib import Path
from .utils import get_available_blueprints, suggest_similar_blueprints
from .config import BLUEPRINTS_DIR

def info_command(args):
    """
    Display detailed information about a specific blueprint.
    
    This command:
    1. Verifies the blueprint exists
    2. Displays detailed information about the blueprint:
       - Description
       - Structure
       - Files
       - Build process
       - Requirements
    
    Args:
        args: Command-line arguments containing:
            - blueprint: The blueprint name to get info about
    """
    # Get available blueprints
    available_blueprints = get_available_blueprints()
    
    # Validate blueprint exists
    if args.blueprint not in available_blueprints:
        print(f"Error: Blueprint '{args.blueprint}' not found.")
        
        # Suggest similar blueprints
        suggestions = suggest_similar_blueprints(args.blueprint, available_blueprints)
        if suggestions:
            print("\nDid you mean one of these?")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        
        print("\nAvailable blueprints:")
        for blueprint in available_blueprints:
            print(f"  - {blueprint}")
        
        return False
    
    # Get the blueprint path
    blueprint_path = available_blueprints[args.blueprint]
    
    print(f"\n=== {args.blueprint.upper()} Blueprint ===\n")
    
    # Get description from README if available
    description = get_blueprint_description(blueprint_path)
    print(f"Description: {description}\n")
    
    # Display file structure
    print("File Structure:")
    show_directory_structure(blueprint_path)
    
    # Display specific information based on blueprint type
    print_blueprint_specific_info(args.blueprint, blueprint_path)
    
    # Check for custom Dockerfile
    if os.path.exists(os.path.join(blueprint_path, "Dockerfile.template")):
        print("\nDockerfile: Custom Dockerfile template available")
    
    print("\nUsage:")
    print(f"  blpt create {args.blueprint} <project_name>")
    print("  cd <project_name>")
    
    # Show common next steps based on blueprint type
    show_next_steps(args.blueprint)
    
    return True

def get_blueprint_description(blueprint_path):
    """
    Extract a detailed description from a blueprint's documentation.
    
    Args:
        blueprint_path (str): Path to the blueprint directory
        
    Returns:
        str: Description or generic message if not found
    """
    # Check for a README file
    readme_path = os.path.join(blueprint_path, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                # Skip header and find first paragraph
                found_header = False
                description_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):
                        found_header = True
                    elif found_header and line:
                        description_lines.append(line)
                    elif description_lines and not line:  # End of paragraph
                        break
                
                if description_lines:
                    return ' '.join(description_lines)
        except Exception:
            pass
    
    # Default generic description based on directory name
    blueprint_name = os.path.basename(blueprint_path)
    return f"A template for {blueprint_name} projects"

def show_directory_structure(directory, indent=0):
    """
    Display the directory structure in a tree-like format.
    
    Args:
        directory (str): Path to the directory
        indent (int): Current indentation level
    """
    # Don't show hidden files or directories
    items = sorted([item for item in os.listdir(directory) if not item.startswith('.')])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        item_path = os.path.join(directory, item)
        
        # Create the line prefix based on depth and whether this is the last item
        prefix = '    ' * indent
        if indent > 0:
            prefix = prefix[:-4] + ('└── ' if is_last else '├── ')
        
        if os.path.isdir(item_path):
            print(f"{prefix}{item}/")
            # Next level indent - changes based on whether this was the last item
            next_indent = indent + 1
            show_directory_structure(item_path, next_indent)
        else:
            print(f"{prefix}{item}")

def print_blueprint_specific_info(blueprint_type, blueprint_path):
    """
    Print information specific to the blueprint type.
    
    Args:
        blueprint_type (str): Type of blueprint
        blueprint_path (str): Path to the blueprint directory
    """
    print("\nProject Information:")
    
    if blueprint_type == "cpp" or blueprint_type == "cpp_lite":
        print("  Type: C++ Project")
        print("  Build System: CMake")
        if blueprint_type == "cpp":
            print("  Testing Framework: Google Test")
        else:
            print("  Testing Framework: CppUnitLite")
    
    elif blueprint_type == "rust":
        print("  Type: Rust Project")
        print("  Build System: Cargo")
        print("  Testing: Built-in Rust testing framework")
        
        # Check for cargo.toml to extract dependencies
        cargo_path = os.path.join(blueprint_path, "Cargo.toml")
        if os.path.exists(cargo_path):
            try:
                with open(cargo_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if "[dependencies]" in content:
                        print("  Dependencies:")
                        dependencies_section = content.split("[dependencies]")[1].split("[")[0]
                        for line in dependencies_section.strip().split("\n"):
                            if line.strip():
                                print(f"    - {line.strip()}")
            except Exception:
                pass
    
    elif blueprint_type == "go":
        print("  Type: Go Project")
        print("  Structure: Modern Go project layout")
        print("  Testing: Built-in Go testing")
        
        # Check for go.mod to extract dependencies
        go_mod_path = os.path.join(blueprint_path, "go.mod")
        if os.path.exists(go_mod_path):
            try:
                with open(go_mod_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    module_line = next((line for line in content.split("\n") if line.startswith("module ")), None)
                    if module_line:
                        print(f"  Module: {module_line.replace('module ', '')}")
            except Exception:
                pass

def show_next_steps(blueprint_type):
    """
    Display next steps based on blueprint type.
    
    Args:
        blueprint_type (str): Type of blueprint
    """
    print("\nCommon Next Steps:")
    
    if blueprint_type == "cpp" or blueprint_type == "cpp_lite":
        print("  # Build with CMake:")
        print("  mkdir -p build && cd build")
        print("  cmake ..")
        print("  make")
        print("")
        print("  # Or build with the dev environment:")
        print("  dev")
        print("  mkdir -p build && cd build")
        print("  cmake .. && make")
        print("")
        print("  # Run with Docker:")
        print("  dkr buildrun")
    
    elif blueprint_type == "rust":
        print("  # Build with Cargo:")
        print("  cargo build")
        print("  cargo run")
        print("")
        print("  # Run tests:")
        print("  cargo test")
        print("")
        print("  # Or build with the dev environment:")
        print("  dev")
        print("  cargo build --release")
        print("")
        print("  # Run with Docker:")
        print("  dkr buildrun")
    
    elif blueprint_type == "go":
        print("  # Build with Go:")
        print("  go build ./...")
        print("  go run ./cmd/...")
        print("")
        print("  # Run tests:")
        print("  go test ./...")
        print("")
        print("  # Or build with the dev environment:")
        print("  dev")
        print("  go build -o ./bin/app ./cmd/...")
        print("")
        print("  # Run with Docker:")
        print("  dkr buildrun")
