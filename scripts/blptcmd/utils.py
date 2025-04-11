"""
Utility functions for the blueprint system.

This module provides helper functions for blueprint operations like:
- Blueprint discovery
- File operations
- String processing
- Template rendering
"""

import os
import sys
import shutil
import re
from pathlib import Path
from .config import BLUEPRINTS_DIR

def get_available_blueprints():
    """
    Scan the blueprints directory and return available blueprints.
    
    Returns:
        dict: Dictionary of blueprint names mapped to their full paths
    """
    blueprints = {}
    
    # Check if blueprints directory exists
    if not os.path.exists(BLUEPRINTS_DIR):
        print(f"Warning: Blueprints directory not found at {BLUEPRINTS_DIR}")
        return {}
    
    # List all subdirectories in the blueprints directory
    for item in os.listdir(BLUEPRINTS_DIR):
        full_path = os.path.join(BLUEPRINTS_DIR, item)
        if os.path.isdir(full_path):
            blueprints[item] = full_path
    
    return blueprints

def validate_project_name(name):
    """
    Validate if a project name is valid.
    
    A valid project name must:
    - Contain only alphanumeric characters, hyphens, and underscores
    - Not start with a number, hyphen, or underscore
    - Not be a reserved name
    
    Args:
        name (str): Project name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Empty name
    if not name:
        return False, "Project name cannot be empty"
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        return False, "Project name must start with a letter and contain only letters, numbers, hyphens, and underscores"
    
    # Check for reserved names
    reserved_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 
                      'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 
                      'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
    
    if name.lower() in reserved_names:
        return False, f"'{name}' is a reserved name and cannot be used"
    
    return True, ""

def copy_directory(src, dst, ignore_patterns=None):
    """
    Copy a directory recursively with optional pattern filtering.
    
    Args:
        src (str): Source directory path
        dst (str): Destination directory path
        ignore_patterns (list): List of file patterns to ignore
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if ignore_patterns:
            ignored = shutil.ignore_patterns(*ignore_patterns)
            shutil.copytree(src, dst, ignore=ignored)
        else:
            shutil.copytree(src, dst)
        return True
    except Exception as e:
        print(f"Error copying directory: {e}")
        return False

def replace_in_file(file_path, replacements):
    """
    Replace text in a file according to a dictionary of replacements.
    
    Args:
        file_path (str): Path to the file
        replacements (dict): Dictionary of {search_text: replace_text}
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        for search, replace in replacements.items():
            content = content.replace(search, replace)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return True
    except Exception as e:
        print(f"Error replacing text in {file_path}: {e}")
        return False

def process_files_recursively(directory, replacements, file_extensions=None):
    """
    Process all files in a directory recursively, applying text replacements.
    
    Args:
        directory (str): Directory to process
        replacements (dict): Dictionary of {search_text: replace_text}
        file_extensions (list): List of file extensions to process, or None for all
        
    Returns:
        int: Number of files processed
    """
    count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip files that don't match the desired extensions
            if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                continue
                
            file_path = os.path.join(root, file)
            if replace_in_file(file_path, replacements):
                count += 1
    
    return count

def suggest_similar_blueprints(name, available_blueprints):
    """
    Suggest similar blueprint names when a user enters an invalid one.
    
    Args:
        name (str): The invalid blueprint name
        available_blueprints (dict): Dictionary of available blueprints
        
    Returns:
        list: List of suggested blueprint names
    """
    suggestions = []
    
    # Simple substring matching
    for blueprint in available_blueprints:
        # If the invalid name is contained in a blueprint name or vice versa
        if name in blueprint or blueprint in name:
            suggestions.append(blueprint)
    
    # Calculate Levenshtein distance for more sophisticated matching
    # This could be added for better suggestions
    
    return suggestions
