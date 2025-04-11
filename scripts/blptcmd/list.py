"""
List command module for the blueprint system.

This module handles the 'list' command which displays all available blueprints.
"""

from .utils import get_available_blueprints
from .config import BLUEPRINTS_DIR
import os

def list_command(args):
    """
    List all available blueprints.
    
    This command scans the blueprints directory and displays all available
    project templates with basic information about each.
    
    Args:
        args: Command-line arguments (not used in this command)
    """
    print("\n=== Available Blueprints ===\n")
    
    # Get all available blueprints
    blueprints = get_available_blueprints()
    
    if not blueprints:
        print("No blueprints found. Create blueprints in:")
        print(f"  {BLUEPRINTS_DIR}\n")
        return
    
    # Display blueprints in a formatted table
    print(f"{'Name':<15} {'Description':<50}")
    print(f"{'-' * 15} {'-' * 50}")
    
    for name, path in blueprints.items():
        # Try to get description from README or metadata file
        description = get_blueprint_description(path)
        print(f"{name:<15} {description:<50}")
    
    print("\nUse 'blpt info <name>' for more details about a specific blueprint.")
    print("Use 'blpt create <name> <project_dir>' to create a new project.\n")

def get_blueprint_description(blueprint_path):
    """
    Extract a short description from a blueprint's documentation.
    
    Args:
        blueprint_path (str): Path to the blueprint directory
        
    Returns:
        str: Short description or generic message if not found
    """
    # Check for a README file
    readme_path = os.path.join(blueprint_path, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as file:
                # Read the first few lines
                lines = [line.strip() for line in file.readlines()[:5]]
                
                # Try to find a description line
                for line in lines:
                    if line and not line.startswith('#'):
                        return line[:50]
        except Exception:
            pass
    
    # Check for metadata file (could be added later)
    
    # Default generic description based on directory name
    blueprint_name = os.path.basename(blueprint_path)
    return f"{blueprint_name.capitalize()} project template"
