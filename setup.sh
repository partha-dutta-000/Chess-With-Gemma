#!/bin/bash

# setup.sh - Automated setup for Chess With Gemma on Linux

echo "Starting setup for Chess With Gemma..."

# 1. Check for Ollama
if ! command -v ollama &> /dev/null
then
    echo "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# 2. Pull Gemma 3 model
echo "Ensuring Gemma 3 4B is available..."
ollama pull gemma3:4b

# 3. Setup Python Virtual Environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python Dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Check for system dependencies (pywebview on Linux)
echo "Checking for system dependencies (webkit2gtk)..."
if command -v apt-get &> /dev/null; then
    echo "Debian/Ubuntu detected. You might need to run: sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0"
elif command -v dnf &> /dev/null; then
    echo "Fedora detected. You might need to run: sudo dnf install python3-gobject webkit2gtk3"
fi

echo "------------------------------------------------"
echo "Setup complete! To run the application, use:"
echo "source venv/bin/activate && python3 server.py"
echo "------------------------------------------------"

# 6. Run the application
python3 server.py
