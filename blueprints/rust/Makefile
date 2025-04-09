# Blueprint for new Rust projects
# Author: Christi Mahu – https://christimahu.dev
# Part of the dev repo: https://github.com/christimahu/dev/
# This file is part of a minimal idiomatic Rust blueprint for creating new applications.
#
# This Makefile is a convenience wrapper around common Cargo commands.
# It makes it easier to remember how to build, run, and test your Rust code.

# 🏃 Run the chatbot app
run:
	cargo run

# 🧪 Run all tests (unit + integration)
# Includes inline tests in `chatbot.rs` and external ones in `tests/`
test:
	cargo test

# 🛠️ Compile the project into a debug binary (doesn't run it)
build:
	cargo build

# 🧼 Remove compiled artifacts (target/ folder)
clean:
	cargo clean

# 📚 Build local HTML documentation and open it in your browser
# This includes public doc comments and API-level help
docs:
	cargo doc --open
