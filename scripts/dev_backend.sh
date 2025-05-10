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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_message "red" "Python not found in PATH. Please install Python and add it to PATH"
    exit 1
else
    python_version=$(python3 --version)
    print_message "green" "Found Python: $python_version"
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_message "red" "Virtual environment not found. Please run install.sh first"
    exit 1
fi

# Get the full path to Python in the virtual environment
python_path="backend/venv/bin/python"
if [ ! -f "$python_path" ]; then
    print_message "red" "Python not found in virtual environment"
    exit 1
fi

# Start the FastAPI backend
print_message "green" "Starting Aura Backend Server..."
cd backend

# Activate virtual environment and show activation
print_message "green" "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_message "red" "Failed to activate virtual environment"
    exit 1
fi

# Start the server
print_message "green" "Server running at http://localhost:8000"
print_message "yellow" "Press Ctrl+C to stop the server"
$python_path -m uvicorn main:app --reload --port 8000 