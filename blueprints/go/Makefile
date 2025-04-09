# Blueprint for new Go projects
# Author: Christi Mahu – https://christimahu.dev
# Part of the dev repo: https://github.com/christimahu/dev/
# This file is part of a minimal idiomatic Go scaffold for creating new applications.

# Makefile - Automation script for development tasks in Go.
# Each target below can be invoked with `make <target-name>`.

# The name of the binary to build
APP := my_go_app

# Runs the main program
run:
	go run ./src/main.go

# Runs all unit tests in the project
test:
	go test ./...

# Builds a binary from the source
build:
	go build -o $(APP) ./src

# Removes the built binary
clean:
	rm -f $(APP)

# Starts local Go documentation server using `godoc`
# Access it at http://localhost:6060 after running this
docs:
	godoc -http=:6060
