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

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_message "red" "Node.js not found. Please install Node.js"
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

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_message "red" "Frontend directory not found"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    print_message "yellow" "Frontend dependencies not found. Installing..."
    cd frontend
    if ! npm install; then
        print_message "red" "Failed to install frontend dependencies"
        exit 1
    fi
    cd ..
fi

# Start the Tauri frontend
print_message "green" "Starting Aura Frontend..."
cd frontend
npm run tauri dev 