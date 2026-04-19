#!/bin/csh

# setup.csh - Automated setup for Chess With Gemma on Linux (C-Shell version)

echo "Starting setup for Chess With Gemma..."

# 1. Check for Ollama
which ollama > /dev/null
if ( $status != 0 ) then
    echo "Ollama not found. Please install Ollama from https://ollama.com/"
else
    echo "Ollama is already installed."
endif

# 2. Pull Gemma 3 model
echo "Ensuring Gemma 3 4B is available..."
ollama pull gemma3:4b

# 3. Setup Python Virtual Environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate.csh

# 4. Install Python Dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "------------------------------------------------"
echo "Setup complete! To run the application, use:"
echo "source venv/bin/activate.csh && python3 server.py"
echo "------------------------------------------------"

# 5. Run the application
python3 server.py
