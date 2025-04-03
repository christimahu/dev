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

2. **Set up shell configuration**
   
   For Zsh users (macOS default):
   ```bash
   # Backup your existing configuration (recommended)
   cp ~/.zshrc ~/.zshrc.backup
   
   # Option 1: Replace your configuration (recommended for new users)
   cp ~/dev/config/zshrc ~/.zshrc
   
   # Option 2: Append to your existing configuration
   cat ~/dev/config/zshrc >> ~/.zshrc
   
   # Apply the changes
   source ~/.zshrc
   ```

   For Bash users:
   ```bash
   # Backup your existing configuration (recommended)
   cp ~/.bashrc ~/.bashrc.backup
   
   # Option 1: Replace your configuration (recommended for new users)
   cp ~/dev/config/bashrc ~/.bashrc
   
   # Option 2: Append to your existing configuration
   cat ~/dev/config/bashrc >> ~/.bashrc
   
   # Apply the changes
   source ~/.bashrc
   ```

3. **Make scripts executable**
   ```bash
   chmod +x ~/dev/scripts/dev.py
   chmod +x ~/dev/scripts/setup.py
   ```

4. **Run the setup script**
   ```bash
   cd ~/dev/scripts
   ./setup.py
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
