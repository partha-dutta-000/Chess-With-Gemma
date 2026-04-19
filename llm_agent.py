import requests
import re
import json
import logging
import os
from prompts import get_chess_prompt

# Configure logging
log_path = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

class LLMAgent:
    def __init__(self):
        self.last_prompt = ""
        
    def get_last_prompt(self):
        return self.last_prompt

    def stream_move(self, move_history, legal_moves, last_move):
        prompt = get_chess_prompt(move_history, legal_moves, last_move)

        self.last_prompt = prompt
        logging.info("--- NEW TURN ---")
        logging.info(f"Generated Prompt:\n{prompt}")

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": True
        }
        
        try:
            logging.info("Sending streaming request to Ollama...")
            # Timeout is high to allow model to load into memory
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)
            
            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk_data = json.loads(line)
                    word = chunk_data.get("response", "")
                    full_text += word
                    
                    yield {"type": "chunk", "content": word}
                    
            logging.info(f"Raw Output:\n{full_text}")
            
            # Extract move
            match = re.search(r'<move>(.*?)</move>', full_text, re.IGNORECASE)
            extracted_move = match.group(1).strip() if match else None
            
            if extracted_move:
                logging.info(f"Successfully extracted move: {extracted_move}")
            else:
                logging.warning("Failed to extract move from tags.")
                
            yield {"type": "done", "move": extracted_move}
                
        except Exception as e:
            logging.error(f"Ollama Request Failed: {e}")
            yield {"type": "error", "message": str(e)}
