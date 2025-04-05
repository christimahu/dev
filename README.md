# Dev Environment

A containerized development environment for seamless cross-platform software development with C++, Rust, Go, Python, and more.

## Features

- **Containerized Development**: Keep your host system clean while having all development tools available
- **Consistent Experience**: Same environment across macOS, Linux, or Windows
- **Pre-installed Tools**: C++, Rust, Go, Python, Node.js, and more
- **Cloud Development**: Google Cloud SDK with all major components pre-installed
- **Version Controlled Config**: Share the same dotfiles and settings across all your machines
- **Project Integration**: Mount any project directory and get started immediately
- **Helper Functions**: Productivity utilities for various languages and tasks
- **Built-in Rust Server**: Lightweight static file server (`srv`) written in Rust, ideal for local web development inside the container

## Installation

### Prerequisites
- Docker
- Python 3
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/christimahu/dev.git ~/.dev
   ```

2. **Run the setup script**
   ```bash
   cd ~/.dev/scripts
   python3 setup.py
   ```
   This will:
   - Create symlinks to `zshrc`, `bashrc`, and shared shell functions
   - Set up the `dev` launcher command

3. **Source your shell configuration**
   ```bash
   # For Bash users
   source ~/.bashrc

   # For Zsh users (macOS default)
   source ~/.zshrc
   ```

4. **Build the Docker container**
   ```bash
   dev build
   ```

5. **Start using the development environment**
   ```bash
   cd ~/your-project
   dev
   ```

## Usage

The `dev` command gives you access to the full container environment with these common operations:

### Container Management

- `dev` — Enter a shell in the container from the current directory
- `dev build` — Build the container image
- `dev rebuild` — Rebuild container with updated plugins
- `dev status` — Show status of the dev container

### Container Lifecycle

- `dev stop` — Stop running containers with interactive selection
  - If multiple containers are running, shows a menu for selection
  - Use `--name CONTAINER_NAME` to stop a specific container
  
- `dev delete` — Remove a specific container
  - Use `--name CONTAINER_NAME` to delete a specific container

- `dev cleanup` — Remove all development containers
  - Stops and removes all containers with the `dev-` prefix

### Container Operations

- `dev logs` — View logs from the container
  - Use `-f` to follow logs in real-time
  - Use `--lines N` to show the last N lines of logs

- `dev exec [command]` — Execute a command inside the container
  - Example: `dev exec npm install`
  - Use `-i` for interactive commands

### Maintenance

- `dev prune` — Clean up unused Docker resources
  - Use `--all` to remove all unused resources
  - Use `--volumes` to also remove volumes

- `dev prune-images` — Remove development-related Docker images
  - Shows an interactive menu to select which images to remove
  - Use `-f` to remove all dev images without confirmation

### Container Sessions

When you run `dev` to enter the shell, the container remains running after you exit to allow for multiple sessions. This lets you have multiple terminal windows connected to the same container. To completely stop the container when you're done, use `dev stop`.

## Working with Projects

The directory you run `dev` from is mounted into the container at a path defined in `dev.env` (default: `/code`). This gives each project its own isolated environment without touching your host.

```ini
# dev.env example
MOUNT=~/.dev:/home/me/.dev
MOUNT=~/code:/home/me/code
MOUNT=~/.ssh:/home/me/.ssh:ro
DEFAULT_WORKDIR=/home/me/code
```

The system supports:
- Mounting any path from the host
- Persistent settings per host
- Lightweight, reproducible tooling

## Helper Functions

Once inside the container, you have access to these utility functions:

- `srv [port] [dir]` — Run the built-in Rust HTTP server (ideal for local HTML/CSS/JS testing)
- `tree [dir]` — Visual tree view of a directory with file sizes
- `ghprune` — Clean up local git branches
- `dockerrm` / `dockerstop` — Remove or stop all containers
- `tarfolder` / `untarfolder` — Archive/unarchive utilities

## Customization

- `config/init.lua` — NeoVim config
- `config/shell_functions` — Add your own bash/zsh helpers
- `dev.env` — Configure mounts, working directory, ports, and environment variables
- `Dockerfile` — Add extra packages or language versions

## Included Tools

- Rust with Cargo and common crates
- Go with common tools
- Python 3 with numpy, pandas, etc.
- Node.js / npm
- C/C++ toolchains
- Google Cloud SDK with all major components
- Git, curl, build-essential, and more

## Troubleshooting

- If you see "port already in use" messages, use `dev cleanup` to remove old containers
- If containers aren't appearing in the correct directory, check the `DEFAULT_WORKDIR` in your dev.env file
- For multiple containers, use `dev status` to see what's running and `dev stop` to stop specific ones

## License

Licensed under the Mozilla Public License 2.0. See the `LICENSE` file for details.
