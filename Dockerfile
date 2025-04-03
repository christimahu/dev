# Stage 1: System-level setup (as root)
FROM ubuntu:22.04 AS system-setup
ENV DEBIAN_FRONTEND=noninteractive

# General updates and tools
RUN apt-get update --fix-missing && \
    apt-get install -y \
    curl wget git vim neovim tmux tree \
    build-essential gcc g++ make cmake ninja-build \
    clang clang-format clang-tidy clangd \
    llvm lldb lld libc++-dev libc++abi-dev \
    python3 python3-pip python3-venv \
    python3-numpy python3-pandas python3-matplotlib python3-scipy python3-sklearn \
    nodejs npm \
    graphviz doxygen \
    pkg-config libssl-dev \
    ripgrep fd-find \
    zsh apt-transport-https ca-certificates gnupg \
    && rm -rf /var/lib/apt/lists/*

# Update Node.js to latest LTS
RUN npm install -g n && \
    n lts && \
    npm install -g pnpm

# Install Go
RUN curl -OL https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk \
    google-cloud-sdk-app-engine-python \
    google-cloud-sdk-app-engine-python-extras \
    google-cloud-sdk-app-engine-java \
    google-cloud-sdk-app-engine-go \
    google-cloud-sdk-datastore-emulator \
    google-cloud-sdk-pubsub-emulator \
    google-cloud-sdk-bigtable-emulator \
    google-cloud-sdk-firestore-emulator \
    kubectl && \
    rm -rf /var/lib/apt/lists/*

# Install common global npm packages
RUN npm install -g typescript ts-node eslint prettier

# Install common global Python packages
RUN pip3 install --no-cache-dir \
    black isort mypy pytest jupyterlab ipython \
    pandas numpy matplotlib seaborn scikit-learn \
    tensorflow torch \
    google-api-python-client google-auth google-cloud-storage

# Stage 2: User setup
FROM system-setup AS user-setup
# Create dev user
RUN useradd -m -s /bin/bash me && \
    mkdir -p /home/me/dev/config && \
    mkdir -p /home/me/.config/nvim

# Switch to user for user-specific installations
USER me
WORKDIR /home/me

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Rust components and common crates
RUN source $HOME/.cargo/env && \
    rustup component add rustfmt clippy rust-analyzer && \
    cargo install cargo-watch cargo-edit cargo-expand tokio-console

# Install Go tools
RUN /usr/local/go/bin/go install golang.org/x/tools/gopls@latest && \
    /usr/local/go/bin/go install github.com/go-delve/delve/cmd/dlv@latest && \
    /usr/local/go/bin/go install github.com/fatih/gomodifytags@latest && \
    /usr/local/go/bin/go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Setup Neovim package manager (Packer)
RUN git clone --depth 1 https://github.com/wbthomason/packer.nvim \
    ~/.local/share/nvim/site/pack/packer/start/packer.nvim

# Stage 3: Final environment setup
FROM user-setup AS dev-environment
# Expose development ports
EXPOSE 8000 8097 8098 8099 5173

# Environment setup
ENV PATH="/usr/local/go/bin:/home/me/.cargo/bin:/home/me/.local/bin:${PATH}"
ENV TERM=xterm-256color

# Set working directory to the dev folder
WORKDIR /home/me/dev

# Default command
CMD ["/bin/bash"]
