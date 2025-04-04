# Dev Environment

A containerized development environment for seamless cross-platform software development with C++, Rust, Go, Python, and more.

## Features

- **Containerized Development**: Keep your host system clean while having all development tools available
- **Consistent Experience**: Same environment across macOS, Linux, or Windows
- **Pre-installed Tools**: C++, Rust, Go, Python, Node.js, and more
- **Cloud Development**: Google Cloud SDK with all major components pre-installed
- **Version Controlled Config**: Share the same dotfiles and settings across all your machines
- **Project Isolation**: Each project gets its own container with proper directory mounting
- **Modern Tools**: NeoVim configuration with LSP, Treesitter, and more
- **Helper Functions**: Productivity utilities for various languages and tasks

## Installation

### Prerequisites
- Docker
- Python 3
- Git

### Setup Steps

1. **Clone the repository to your home directory**
   ```bash
   git clone https://github.com/christimahu/dev.git ~/dev
   ```

2. **Run the setup script**
   ```bash
   cd ~/dev/scripts
   python3 setup.py
   ```
   This will:
   - Create necessary symlinks for configurations
   - Build local development tools
   - Set up the `dev` command alias

3. **Source your shell configuration**
   ```bash
   # For Bash users
   source ~/.bashrc
   
   # For Zsh users (macOS default)
   source ~/.zshrc
   ```

4. **Build the Docker container**
   ```bash
   # Use the dev command to build the container
   dev build
   ```

5. **Start using the development environment**
   ```bash
   # Navigate to any project directory
   cd ~/your-project
   
   # Enter the development environment
   dev
   ```

## Usage

The `dev` command provides a seamless way to work with your development environment:

- `dev` - Enter a shell in the development container at your current directory
- `dev build` - Build the development container image
- `dev status` - Show container status information
- `dev exec [command]` - Execute a command in the container
- `dev stop` - Stop the running container
- `dev delete` - Delete the container

When you exit the container's shell, it will automatically shut down and remove the container to free up resources.

## Directory Structure

```
~/dev/
├── container/           # Docker container definitions
├── config/              # Configuration files
│   ├── init.lua         # NeoVim configuration
│   ├── shell_functions  # Shared shell functions
│   ├── bashrc           # Bash bootstrap config
│   └── zshrc            # Zsh bootstrap config
├── tools/               # Development tools
│   └── srv/             # Simple HTTP server
├── scripts/             # Management scripts
│   ├── dev.py           # Main launcher script
│   └── setup.py         # Setup script
└── web/                 # Project website
```

## Working with Projects

The development environment is designed to work with your existing project structure:

1. Your entire home directory is mounted into the container at `/home/me`
2. When you run `dev` from any directory:
   - That directory is the container's working directory
   - You can access all files from your home directory
   - Changes made inside the container are reflected on your host system

This makes it easy to work with multiple projects without having to reconfigure the environment.

## Custom Settings

### Port Mappings

Configure custom port mappings in `custom.env` based on the provided example file:

```bash
# Create your custom environment file
cp custom_example.env custom.env

# Edit with your preferred ports
vim custom.env
```

### Environment Variables

Add project-specific environment variables to your `custom.env` file:

```
NODE_ENV=development
DEBUG=true
API_KEY=your_api_key
```

## Helper Functions

The environment includes numerous helper functions:

- `srv [port] [dir]` - Serve files from a directory using a HTTP server
- `tree [dir]` - Enhanced tree command with file sizes
- `tarfolder [dir]` - Create a tar archive from a directory
- `untarfolder [file]` - Extract a tar file into a directory
- `ghprune` - Prune git branches that no longer exist on remote
- `dockerstop` - Stop all running Docker containers
- `dockerrm` - Remove all Docker containers
- `dockerrmi` - Remove all Docker images

## Customization

The environment is designed to be easily customizable:

1. Edit `config/init.lua` to customize your NeoVim setup
2. Add your own functions to `config/shell_functions`
3. Modify the `Dockerfile` to add or remove tools
4. Create your own `custom.env` file for environment variables

## Troubleshooting

### Container Won't Start

If the container fails to start, check:
- Docker is running
- No port conflicts in your `custom.env`
- You have sufficient permissions

To clean up and start fresh:
```bash
dockerstop  # Stop all containers
dockerrm    # Remove all containers
dev build   # Rebuild your dev container
```

### NeoVim Plugins Not Working

If NeoVim plugins aren't loading, run:

```bash
# Inside the container
mkdir -p ~/.local/share/nvim/site/pack/packer/start
git clone --depth 1 https://github.com/wbthomason/packer.nvim ~/.local/share/nvim/site/pack/packer/start/packer.nvim
nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'
```

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0).
See the LICENSE file for details.

---

For more detailed information, please visit [the project website](https://christimahu.dev/).
