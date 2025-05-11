#!/bin/bash

# Function to print colored messages
print_green() {
    echo -e "\n[✓] $1"
}

print_red() {
    echo -e "\n[✗] $1"
}

print_yellow() {
    echo -e "\n[!] $1"
}

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    print_red "Python 3.12 not found in PATH. Please install Python 3.12 and add it to PATH"
    exit 1
fi

python_version=$(python3.12 --version)
print_green "Found Python: $python_version"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_red "Virtual environment not found. Please run install.sh first"
    exit 1
fi

# Get the full path to Python in the virtual environment
python_path="$(pwd)/backend/venv/bin/python"
if [ ! -f "$python_path" ]; then
    print_red "Python not found in virtual environment. Please run install.sh first"
    exit 1
fi

# Start the FastAPI backend in a new terminal
print_green "Starting Aura Backend Server..."
gnome-terminal -- bash -c "cd '$(pwd)/backend' && '$python_path' -m uvicorn main:app --reload --port 8000; echo -e '\n[!] Press any key to close this window...'; read -n 1"

# Start the Tauri frontend in the current terminal
print_green "Starting Aura Frontend..."
cd frontend
npm run tauri dev
