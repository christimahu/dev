```markdown
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
   git clone https://github.com/christimahu/dev.git ~/dev
   ```

2. **Run the setup script**
   ```bash
   cd ~/dev
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

The `dev` command gives you access to the full container environment:

- `dev` — Enter a shell in the container from the current directory
- `dev build` — Build the container image
- `dev status` — Show status of the dev container
- `dev logs` — View logs from the container
- `dev exec [command]` — Execute a command inside the container
- `dev config` — Print the resolved config from `dev.env`
- `dev stop` — Stop the running container
- `dev delete` — Remove the container

Exiting the shell (`exit`) automatically stops and removes the container.

## Working with Projects

The directory you run `dev` from is mounted into the container at a path defined in `dev.env` (default: `/code`). This gives each project its own isolated environment without touching your host.

```ini
# dev.env
DOCKER_MOUNT_TARGET=code
```

This system supports:
- Mounting any path from the host
- Persistent settings per host
- Lightweight, reproducible tooling

## Helper Functions

- `srv [port] [dir]` — Run the built-in Rust HTTP server (ideal for local HTML/CSS/JS testing)
- `tree [dir]` — Visual tree view of a directory with file sizes
- `ghprune` — Clean up local git branches
- `dockerrm` / `dockerstop` — Remove or stop all containers
- `tarfolder` / `untarfolder` — Archive/unarchive utilities

## Customization

- `config/init.lua` — NeoVim config (Note: NeoVim inside the container is not yet fully working)
- `config/shell_functions` — Add your own bash/zsh helpers
- `custom.env` — Override container mount path, ports, env vars
- `Dockerfile` — Add extra packages or language versions

## Included Tools

- Rust
- Go
- Python 3
- Node.js / npm
- C/C++ toolchains
- Google Cloud SDK
- Git, curl, build-essential, and more

## License

Licensed under the Mozilla Public License 2.0. See the `LICENSE` file for details.
```
