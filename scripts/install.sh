#!/bin/bash

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\n[✓] $message" ;;
        "red") echo -e "\n[✗] $message" ;;
        "yellow") echo -e "\n[!] $message" ;;
    esac
}

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    print_message "red" "Python 3.12 not found. Please install Python 3.12 from https://www.python.org/downloads/release/python-3122/"
    exit 1
else
    python_version=$(python3.12 --version)
    print_message "green" "Found Python version: $python_version"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_message "red" "Node.js not found. Please install Node.js from https://nodejs.org/"
    exit 1
else
    node_version=$(node --version)
    print_message "green" "Found Node.js: $node_version"
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_message "red" "npm not found. Please install npm"
    exit 1
else
    npm_version=$(npm --version)
    print_message "green" "Found npm: $npm_version"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    print_message "green" "Creating virtual environment with Python 3.12..."
    python3.12 -m venv backend/venv
    if [ $? -ne 0 ]; then
        print_message "red" "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
print_message "green" "Activating virtual environment..."
source backend/venv/bin/activate
if [ $? -ne 0 ]; then
    print_message "red" "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip first
print_message "green" "Upgrading pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_message "red" "Failed to upgrade pip"
    exit 1
fi

# Install Python dependencies with error handling
print_message "green" "Installing Python dependencies..."
if ! pip install -r backend/requirements.txt; then
    print_message "yellow" "Error installing dependencies. Trying alternative method..."
    if ! pip install --no-cache-dir -r backend/requirements.txt; then
        print_message "red" "Failed to install Python dependencies"
        exit 1
    fi
fi

# Install frontend dependencies
print_message "green" "Installing frontend dependencies..."
cd frontend
if ! npm install; then
    print_message "red" "Failed to install frontend dependencies"
    exit 1
fi
cd ..

print_message "green" "Installation complete!"
print_message "yellow" "You can now run the development environment using: ./scripts/start_dev.sh"
