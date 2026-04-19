# Chess With Gemma

A standalone desktop application to play chess against the Gemma 3 LLM using an agentic reasoning workflow.

## Features
- **Agentic Reasoning:** Watch Gemma 3 analyze threats and strategy in real-time.
- **Desktop Experience:** Powered by Python and Pywebview for a native feel.
- **Decision Timers:** Compare human and AI decision speeds.
- **PGN Export:** Download your games for analysis.

## Prerequisites
1. **Ollama:** Install [Ollama](https://ollama.com/).
2. **Gemma 3:** Run `ollama run gemma3:4b` to ensure the model is downloaded.
3. **Python 3.12+**

## Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the venv:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running the App
### Windows
Start the application by running:
```bash
python server.py
```

### Linux (One-Command Setup)
We provide an automated setup script for Linux environments:
```bash
chmod +x setup.sh
./setup.sh
```
This script will check for Ollama, pull the Gemma 3 model, set up the virtual environment, and launch the app.

## Linux System Dependencies
If you are running on Linux, `pywebview` requires GTK and WebKit2. If the app fails to launch, install the following:
- **Ubuntu/Debian:** `sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0`
- **Fedora:** `sudo dnf install python3-gobject webkit2gtk3`

## Architecture
- **Backend:** FastAPI
- **AI Integration:** Ollama (Gemma 3 4B)
- **UI:** HTML/CSS/JS (served via Pywebview)
- **Chess Logic:** python-chess
