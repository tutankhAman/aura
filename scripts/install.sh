#!/bin/bash

set -e  # Exit immediately on error

# Go to project root (in case user runs it from subfolder)
cd "$(dirname "$0")/.."

# Define venv path
VENV_PATH="backend/venv"

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found."
    echo "👉 Please install Python 3.12 from: https://www.python.org/downloads/release/python-3122/"
    exit 1
fi

echo "✅ Python version: $(python3.12 --version)"

# Create virtualenv if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "📦 Creating virtual environment..."
    python3.12 -m venv "$VENV_PATH"
else
    echo "✅ Virtual environment already exists."
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Verify we're using the right Python
echo "🐍 Using Python from: $(which python)"
echo "📦 Installing backend dependencies..."

# Upgrade pip
python -m pip install --upgrade pip

# Install Python deps
if ! pip install -r requirements.txt; then
    echo "⚠️ pip install failed. Trying with --no-cache-dir..."
    pip install --no-cache-dir -r requirements.txt
fi

# Install frontend deps
echo "🌐 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "🎉 Setup complete!"
