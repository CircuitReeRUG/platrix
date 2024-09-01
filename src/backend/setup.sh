#!/bin/sh
# Build the necessary libraries and install dependencies for backend

# Ask for sudo permissions
echo "For some parts of the installation, sudo permissions are required. Continue? [y/n]"
read -r response
if [ "$response" != "y" ]; then
    echo "Installation aborted."
    exit 1
fi
sudo echo "Thank you!"

# Check for Python 3.12.*
if ! python3 --version 2>&1 | grep -q "3.12"; then
    echo "Python 3.12.* is required for this project."
    echo "Please install Python 3.12.* and try again."
    exit 1
fi

# Check if library for matrix is available
echo "Checking for/updating matrix library..."
if [ ! -f ../.gitmodules ]; then
    git submodule update --init --recursive
else
    git submodule update --recursive
fi

# Install the matrix library
echo "Installing matrix library..."
cd matrix
make build-python
sudo make install-python
cd ..

# Install the dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Ready to go! Now go build the frontend and run the project."
