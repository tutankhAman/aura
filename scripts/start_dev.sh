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
    print_message "yellow" "Virtual environment not found. Creating one..."
    python3 -m venv backend/venv
    if [ $? -ne 0 ]; then
        print_message "red" "Failed to create virtual environment"
        exit 1
    fi
    print_message "green" "Virtual environment created successfully"
fi

# Get the full path to Python in the virtual environment
python_path="backend/venv/bin/python"
if [ ! -f "$python_path" ]; then
    print_message "red" "Python not found in virtual environment"
    exit 1
fi

# Upgrade pip in the virtual environment
print_message "green" "Upgrading pip..."
$python_path -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_message "red" "Failed to upgrade pip"
    exit 1
fi

# Install requirements if needed
if [ -f "backend/requirements.txt" ]; then
    print_message "green" "Installing Python requirements..."
    $python_path -m pip install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        print_message "red" "Failed to install requirements"
        exit 1
    fi
fi

# Start the FastAPI backend in a new terminal
print_message "green" "Starting Aura Backend Server..."
gnome-terminal -- bash -c "cd $(pwd)/backend && source venv/bin/activate && $python_path -m uvicorn main:app --reload --port 8000; exec bash" || \
xterm -e "cd $(pwd)/backend && source venv/bin/activate && $python_path -m uvicorn main:app --reload --port 8000; exec bash" || \
print_message "yellow" "Could not open new terminal. Please start the backend manually using ./scripts/dev_backend.sh"

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

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    print_message "green" "Installing frontend dependencies..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        print_message "red" "Failed to install frontend dependencies"
        exit 1
    fi
    cd ..
fi

# Start the Tauri frontend in the current window
print_message "green" "Starting Aura Frontend..."
cd frontend
npm run tauri dev
