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

## Usage

The `dev` command provides a seamless way to work with your development environment:

- `dev` - Enter a shell in the development container at your current directory
- `dev build` - Build the development container image
- `dev status` - Show container status information
- `dev exec [command]` - Execute a command in the container
- `dev stop` - Stop the running container
- `dev delete` - Delete the container
- `dev logs` - View container logs
- `dev prune` - Clean up unused Docker resources

## Installation Workflow Details

To understand the installation process better:

1. **Setup script (`setup.py`)**:
   - Sets up configuration symlinks (Neovim, shell)
   - Builds local tools like the HTTP server
   - Creates the `dev` command alias
   - Does NOT build the Docker container

2. **Build command (`dev build`)**:
   - Creates the Docker image with all development tools
   - Installs programming languages and tools
   - Configures the development environment

This two-step process allows for better control and separation of concerns.

## Recommended Workflow

For the best experience, we recommend:
1. Keep your development environment in `~/dev`
2. Store your actual projects in a separate directory (e.g., `~/code` or `~/projects`)
3. Run the `dev` command from your project directories

This ensures a clear separation between your development tools and your project code.

## Helper Functions

The environment includes numerous helper functions:

- `srv [port] [dir]` - Serve files from a directory using a HTTP server
- `tree [dir]` - Enhanced tree command with file sizes
- `tarfolder [dir]` - Create a tar archive from a directory
- `untarfolder [file]` - Extract a tar file into a directory
- `ghprune` - Prune git branches that no longer exist on remote
- And many more!

## Customization

The environment is designed to be easily customizable:

1. Edit `config/init.lua` to customize your NeoVim setup
2. Add your own functions to `config/shell_functions`
3. Modify the `Dockerfile` to add or remove tools
4. Changes are automatically applied across all your containers and machines

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0).
See the LICENSE file for details.

---

For more detailed information, please visit [the project website](https://christimahu.dev/).
