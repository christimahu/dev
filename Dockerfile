# Stage 1: System-level setup (as root)
# This stage installs all system packages and dependencies
FROM ubuntu:22.04 AS system-setup
ENV DEBIAN_FRONTEND=noninteractive

# General updates and tools
# We install a variety of development tools and languages here
RUN apt-get update --fix-missing && \
    apt-get install -y \
    curl wget git vim neovim tmux tree \
    build-essential gcc g++ make cmake ninja-build \
    clang clang-format clang-tidy clangd \
    llvm lldb lld libc++-dev libc++abi-dev \
    python3 python3-pip python3-venv \
    python3-numpy python3-pandas python3-matplotlib python3-scipy python3-sklearn \
    apt-transport-https ca-certificates gnupg \
    ripgrep fd-find zsh \
    pkg-config libssl-dev \
    graphviz doxygen \
    # Add luajit for Neovim plugins
    luajit libluajit-5.1-dev lua5.1 liblua5.1-0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (fixed method)
# This uses the official NodeSource repository
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    rm -rf /var/lib/apt/lists/*

# Install Go
# We download and install the Go binary directly
RUN curl -OL https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz

# Install Google Cloud SDK
# This adds the Google Cloud repositories and installs the SDK with various components
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
    google-api-python-client google-auth google-cloud-storage

# Stage 2: User setup
# This stage creates a non-root user and installs user-specific tools
FROM system-setup AS user-setup

# Copy srv tool files first so we can modify them if needed
COPY --chown=root:root tools/srv/ /tmp/srv/

# Fix the axum serve function in main.rs
RUN sed -i 's/axum::serve(listener, app).await/axum::Server::bind(\&addr).serve(app.into_make_service()).await/g' /tmp/srv/src/main.rs

# Create dev user and necessary directories
RUN useradd -m -s /bin/bash me && \
    mkdir -p /home/me/.dev/config && \
    mkdir -p /home/me/.dev/tools/srv && \
    mkdir -p /home/me/.config/nvim && \
    # Copy srv files to user directory
    cp -r /tmp/srv/* /home/me/.dev/tools/srv/ && \
    # Ensure proper permissions
    chown -R me:me /home/me && \
    # Clean up
    rm -rf /tmp/srv

# Switch to user for user-specific installations
USER me
WORKDIR /home/me

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Rust components and common crates
# Use bash explicitly and the full path to cargo/env
SHELL ["/bin/bash", "-c"]
RUN . /home/me/.cargo/env && \
    rustup component add rustfmt clippy rust-analyzer && \
    cargo install cargo-watch cargo-edit cargo-expand tokio-console

# Install Go tools with CGO_ENABLED=0 to avoid compilation issues
# This disables C dependencies which simplifies installation
ENV CGO_ENABLED=0
RUN /usr/local/go/bin/go install golang.org/x/tools/gopls@v0.14.2 && \
    /usr/local/go/bin/go install github.com/go-delve/delve/cmd/dlv@v1.21.0 && \
    /usr/local/go/bin/go install github.com/fatih/gomodifytags@v1.16.0 && \
    /usr/local/go/bin/go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.55.2

# Build srv tool inside the container using bash to ensure proper environment
RUN /bin/bash -c 'source /home/me/.cargo/env && \
    cd /home/me/.dev/tools/srv && \
    cargo build --release'

# Set up Neovim with Packer
RUN mkdir -p /home/me/.local/share/nvim/site/pack/packer/start && \
    git clone --depth 1 https://github.com/wbthomason/packer.nvim /home/me/.local/share/nvim/site/pack/packer/start/packer.nvim && \
    mkdir -p /home/me/.config/nvim/plugin

# Stage 3: Final environment setup
# This is the final stage that will be used for the actual container
FROM user-setup AS dev-environment
# Expose development ports
EXPOSE 8000 8097 8098 8099 5173

# Environment setup
ENV PATH="/usr/local/go/bin:/home/me/.cargo/bin:/home/me/.local/bin:${PATH}"
ENV TERM=xterm-256color
# Reset CGO for normal operation
ENV CGO_ENABLED=1

# Set up vim -> nvim alias
USER root
RUN ln -sf /usr/bin/nvim /usr/local/bin/vim

# Switch back to user
USER me
RUN echo 'alias vim=nvim' >> /home/me/.bashrc

# Create code directory (if it doesn't exist)
RUN mkdir -p /home/me/code

# Default command
CMD ["/bin/bash"]
