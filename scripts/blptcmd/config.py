"""
Configuration variables for the blueprint system.
"""

import os
from pathlib import Path

# Configuration
HOME_DIR = str(Path.home())
DEV_DIR = os.path.join(HOME_DIR, ".dev")
BLUEPRINTS_DIR = os.path.join(DEV_DIR, "blueprints")
BASE_DOCKERFILE = os.path.join(DEV_DIR, "config", "Dockerfile.base")

# Ensure blueprint directory exists
if not os.path.exists(BLUEPRINTS_DIR):
    try:
        os.makedirs(BLUEPRINTS_DIR, exist_ok=True)
        print(f"Created blueprints directory at {BLUEPRINTS_DIR}")
    except Exception as e:
        print(f"Warning: Could not create blueprints directory: {e}")
