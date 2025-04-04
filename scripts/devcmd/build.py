"""
Build command functionality for the development environment.
"""

import os
import subprocess
import shutil
from .config import DEV_DIR, IMAGE_NAME, IMAGE_TAG
from .utils import run_command, get_container_name, container_exists, container_running

def build_command(args):
    """
    Build the development container image.
    
    Args:
        args: Command-line arguments with build options
    """
    build_args = ["docker", "build"]
    
    if args.no_cache:
        build_args.append("--no-cache")
    
    if args.stage == "full":
        build_args.extend(["-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."])
    elif args.stage == "user":
        build_args.extend(["--target", "user-setup", "-t", f"{IMAGE_NAME}:user-stage", "."])
        build_args = ["docker", "build", "--target", "dev-environment", 
                     "--build-arg", "BASE_IMAGE=user-stage",
                     "-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."]
    elif args.stage == "final":
        build_args.extend(["--target", "dev-environment", 
                          "-t", f"{IMAGE_NAME}:{IMAGE_TAG}", "."])
    
    print(f"Building container image: {' '.join(build_args)}")
    os.chdir(DEV_DIR)  # Ensure correct build context
    
    result = subprocess.run(build_args)
    
    if result.returncode == 0:
        print("\n✅ Build completed successfully!")
        print("You can now run 'dev' to enter the development environment.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

def rebuild_command(args):
    """
    Rebuild the development container image and update plugins.
    
    This command is useful when you've updated your Neovim configuration
    or need to refresh the container image with new plugins.
    
    Args:
        args: Command-line arguments
    """
    container_name = args.name if args.name else get_container_name()
    
    # Check if the container exists and stop it if running
    if container_exists(container_name):
        if container_running(container_name):
            print(f"Stopping container: {container_name}")
            run_command(["docker", "stop", container_name])
        
        print(f"Removing container: {container_name}")
        run_command(["docker", "rm", container_name])
    
    # Build the container image
    build_args = ["docker", "build"]
    
    if args.no_cache:
        build_args.append("--no-cache")
    
    if args.with_plugins and os.path.exists(os.path.join(DEV_DIR, "config", "init.lua")):
        print("Preparing custom init.lua for plugin installation...")
        # Create a build context with user's init.lua
        build_context = os.path.join(DEV_DIR, "build_context")
        os.makedirs(build_context, exist_ok=True)
        
        # Copy the user's init.lua for the build
        shutil.copy(
            os.path.join(DEV_DIR, "config", "init.lua"), 
            os.path.join(build_context, "init.lua")
        )
        
        # Add the dockerfile that uses the custom init.lua
        with open(os.path.join(build_context, "Dockerfile"), "w") as f:
            f.write(f"""
FROM {IMAGE_NAME}:{IMAGE_TAG}
COPY init.lua /home/me/.config/nvim/init.lua
RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync' || true
""")
        
        # Build with the custom context
        build_args.extend(["-t", f"{IMAGE_NAME}:{IMAGE_TAG}", build_context])
    else:
        # Standard rebuild without custom plugins
        build_args.extend(["-t", f"{IMAGE_NAME}:{IMAGE_TAG}", DEV_DIR])
    
    print(f"Rebuilding container image: {' '.join(build_args)}")
    result = subprocess.run(build_args)
    
    if result.returncode == 0:
        print("\n✅ Rebuild completed successfully!")
        
        # Clean up build context if we created one
        if args.with_plugins and os.path.exists(os.path.join(DEV_DIR, "build_context")):
            shutil.rmtree(os.path.join(DEV_DIR, "build_context"))
        
        print("You can now run 'dev' to enter the updated development environment.")
    else:
        print("\n❌ Rebuild failed. Please check the error messages above.")
