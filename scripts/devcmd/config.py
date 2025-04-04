"""
Configuration variables for the development environment.
"""

import os
from pathlib import Path

# Configuration
IMAGE_NAME = "christi-dev"
IMAGE_TAG = "latest"
HOME_DIR = str(Path.home())
DEV_DIR = os.path.join(HOME_DIR, ".dev")

# Check if running from .dev directory
if os.path.basename(os.getcwd()) == ".dev" and os.path.exists(os.path.join(os.getcwd(), "scripts", "dev.py")):
    DEV_DIR = os.getcwd()
