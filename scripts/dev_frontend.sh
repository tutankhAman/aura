#!/bin/bash

# Function to print colored messages
print_green() {
    echo -e "\n[✓] $1"
}

print_red() {
    echo -e "\n[✗] $1"
}

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_red "Frontend directory not found. Please run setup_frontend.sh first"
    exit 1
fi

# Start the Tauri frontend
print_green "Starting Aura Frontend..."
cd frontend
npm run tauri dev 