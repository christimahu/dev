"""
Create command module for the blueprint system.

This module handles the 'create' command which generates new projects from templates.
"""

import os
import sys
import shutil
from pathlib import Path
from .config import BLUEPRINTS_DIR, BASE_DOCKERFILE
from .utils import (
    get_available_blueprints,
    validate_project_name,
    copy_directory,
    process_files_recursively,
    suggest_similar_blueprints
)

def create_command(args):
    """
    Create a new project from a blueprint.
    
    This command:
    1. Validates the blueprint exists
    2. Checks the project name is valid
    3. Copies the blueprint to the target directory
    4. Processes template variables
    5. Creates the Dockerfile
    6. Displays next steps
    
    Args:
        args: Command-line arguments containing:
            - blueprint: The blueprint name
            - project_dir: The project directory name
            - output: Optional output directory path
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
    
    # Validate project name
    is_valid, error_message = validate_project_name(args.project_dir)
    if not is_valid:
        print(f"Error: {error_message}")
        return False
    
    # Determine output directory
    if args.output:
        output_base_dir = os.path.abspath(args.output)
    else:
        output_base_dir = os.getcwd()
    
    project_path = os.path.join(output_base_dir, args.project_dir)
    
    # Check if directory already exists
    if os.path.exists(project_path):
        print(f"Error: Directory '{project_path}' already exists.")
        return False
    
    # Get the blueprint path
    blueprint_path = available_blueprints[args.blueprint]
    
    print(f"\nCreating {args.blueprint} project in {project_path}...")
    
    # Copy the blueprint to the target directory
    print("Copying template files...")
    if not copy_directory(blueprint_path, project_path, ignore_patterns=['.git', '__pycache__']):
        print("Error: Failed to copy blueprint files.")
        return False
    
    # Create replacements dictionary
    replacements = {
        "{PROJECT_NAME}": args.project_dir,
        "{PROJECT_NAME_UPPER}": args.project_dir.upper(),
        "{PROJECT_NAME_LOWER}": args.project_dir.lower(),
        "{PROJECT_NAME_CAMEL}": ''.join(word.capitalize() for word in args.project_dir.split('_')),
    }
    
    # Process files for replacements
    print("Processing template files...")
    file_extensions = ['.cpp', '.h', '.py', '.md', '.txt', '.html', '.css', '.js', 
                      '.json', '.toml', '.yaml', '.yml', '.rs', '.go', 'CMakeLists.txt']
    
    files_processed = process_files_recursively(project_path, replacements, file_extensions)
    print(f"Processed {files_processed} files.")
    
    # Generate Dockerfile if needed
    if os.path.exists(os.path.join(blueprint_path, "Dockerfile.template")):
        print("Generating Dockerfile...")
        generate_dockerfile(blueprint_path, project_path, args.project_dir)
    
    # Display next steps based on blueprint type
    print("\n✅ Project created successfully!\n")
    print(f"Your new {args.blueprint} project is ready in:")
    print(f"  {project_path}\n")
    
    # Display blueprint-specific next steps
    display_next_steps(args.blueprint, args.project_dir, project_path)
    
    return True

def generate_dockerfile(blueprint_path, project_path, project_name):
    """
    Generate a Dockerfile for the project.
    
    Args:
        blueprint_path (str): Path to the blueprint directory
        project_path (str): Path to the project directory
        project_name (str): Name of the project
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Final Dockerfile path
    dockerfile_path = os.path.join(project_path, "Dockerfile")
    
    # Start with base Dockerfile if it exists
    if os.path.exists(BASE_DOCKERFILE):
        try:
            with open(BASE_DOCKERFILE, 'r', encoding='utf-8') as f:
                dockerfile_content = f.read()
        except Exception as e:
            print(f"Warning: Could not read base Dockerfile: {e}")
            dockerfile_content = "FROM ubuntu:22.04\n\n# Base Dockerfile for {PROJECT_NAME}\n"
    else:
        dockerfile_content = "FROM ubuntu:22.04\n\n# Base Dockerfile for {PROJECT_NAME}\n"
    
    # Check for blueprint-specific template
    template_path = os.path.join(blueprint_path, "Dockerfile.template")
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Insert template content into base Dockerfile
            if "# {BLUEPRINT_SPECIFIC}" in dockerfile_content:
                dockerfile_content = dockerfile_content.replace(
                    "# {BLUEPRINT_SPECIFIC}", 
                    template_content
                )
            else:
                dockerfile_content += "\n\n# Blueprint specific additions\n" + template_content
        except Exception as e:
            print(f"Warning: Could not process Dockerfile template: {e}")
    
    # Replace variables
    replacements = {
        "{PROJECT_NAME}": project_name,
        "{PROJECT_NAME_UPPER}": project_name.upper(),
        "{PROJECT_NAME_LOWER}": project_name.lower(),
    }
    
    for search, replace in replacements.items():
        dockerfile_content = dockerfile_content.replace(search, replace)
    
    # Write the final Dockerfile
    try:
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        return True
    except Exception as e:
        print(f"Error writing Dockerfile: {e}")
        return False

def display_next_steps(blueprint_type, project_name, project_path):
    """
    Display next steps based on blueprint type.
    
    Args:
        blueprint_type (str): Type of blueprint
        project_name (str): Name of the project
        project_path (str): Path to the project directory
    """
    print("Next steps:")
    
    # Common steps
    print("  cd", project_name)
    
    # Blueprint-specific steps
    if blueprint_type == "cpp" or blueprint_type == "cpp_lite":
        print("  # Build with CMake:")
        print("  mkdir -p build && cd build")
        print("  cmake ..")
        print("  make")
        print("\n  # Or using the dev environment:")
        print("  dev")
        print("  mkdir -p build && cd build")
        print("  cmake ..")
        print("  make")
    
    elif blueprint_type == "rust":
        print("  # Build with Cargo:")
        print("  cargo build")
        print("  cargo run")
        print("\n  # Or using the dev environment:")
        print("  dev")
        print("  cargo build")
        print("  cargo run")
    
    elif blueprint_type == "go":
        print("  # Build with Go:")
        print("  go build ./cmd/...")
        print("  go run ./cmd/...")
        print("\n  # Or using the dev environment:")
        print("  dev")
        print("  go build ./cmd/...")
        print("  go run ./cmd/...")
    
    # Docker steps
    print("\n  # Build and run with Docker:")
    print("  dkr build")
    print("  dkr run")
    print("  # Or in one command:")
    print("  dkr buildrun")
