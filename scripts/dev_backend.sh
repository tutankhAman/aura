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

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_red "Virtual environment not found. Please run install.sh first"
    exit 1
fi

# Start the FastAPI backend
print_green "Starting Aura Backend Server..."
cd backend

# Activate virtual environment and show activation
print_yellow "Activating virtual environment..."
nano venv/bin/activate
# Strip out all Cursor-related garbage from PATH
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v 'Cursor' | grep -v '/tmp/.mount_Cursor' | tr '\n' ':' | sed 's/:$//')
hash -r
source venv/bin/activate
print_green "Virtual environment activated: $(pwd)/venv"
alias python=./venv/bin/python
alias pip=./venv/bin/pip

# Start the server
print_yellow "Server running at http://localhost:8000"
print_yellow "Press Ctrl+C to stop the server"
python -m uvicorn main:app --reload --port 8000 