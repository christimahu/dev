"""
Configuration variables for the Docker container management system.
"""

import os
from pathlib import Path

# Configuration
HOME_DIR = str(Path.home())
DEV_DIR = os.path.join(HOME_DIR, ".dev")
DOCKER_CONFIG_DIR = os.path.join(DEV_DIR, "config", "docker")

# Default prefix for container/image naming
IMAGE_PREFIX = "app"

# Filter for excluding dev containers (those managed by dev.py)
DEV_CONTAINER_PREFIX = "dev-"

# Default options
DEFAULT_PORTS = ["8080:80"]
DEFAULT_DOCKER_FLAGS = ["--rm"]  # Remove container when it exits

# Environment variables to pass by default
DEFAULT_ENV_VARS = {
    "DOCKER_BUILDKIT": "1"  # Enable BuildKit for faster builds
}

# Function to get default tag for current directory
def get_default_tag():
    """
    Generate a default Docker image tag based on the current directory.
    
    Returns:
        str: Default tag name
    """
    current_dir = os.path.basename(os.getcwd())
    return f"{IMAGE_PREFIX}-{current_dir.lower()}"
