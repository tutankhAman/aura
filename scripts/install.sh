#!/bin/bash

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 not found. Please install Python 3.12 from https://www.python.org/downloads/release/python-3122/"
    exit 1
fi

# Print Python version
python3.12 --version

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    python3.12 -m venv backend/venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source backend/venv/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies with error handling
echo "Installing dependencies..."
if ! pip install -r requirements.txt; then
    echo "Error installing dependencies. Trying alternative method..."
    pip install --no-cache-dir -r requirements.txt
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

echo "Installation complete!"

# Uncomment the following line to automatically start the development environment
# ./scripts/start_dev.sh
