import webview
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from chess_engine import ChessEngine
from llm_agent import LLMAgent
import time
import os
import json

app = FastAPI()
os.makedirs("ui", exist_ok=True)
app.mount("/static", StaticFiles(directory="ui"), name="static")

engine = ChessEngine()
agent = LLMAgent()

@app.get("/")
def read_root():
    return FileResponse("ui/index.html")

class MoveRequest(BaseModel):
    move: str # UCI format

@app.post("/api/human_move")
def human_move(req: MoveRequest):
    success = engine.make_move(req.move)
    return {"success": success, "fen": engine.get_fen(), "game_over": engine.is_game_over()}

@app.get("/api/llm_move_stream")
def llm_move_stream():
    if engine.is_game_over():
        def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Game is over'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    history = engine.get_history()
    legal_moves = engine.get_legal_moves()
    last_move = engine.get_last_move_san()
    
    def event_stream():
        start_time = time.time()
        for event in agent.stream_move(history, legal_moves, last_move):
            if event["type"] == "done":
                move_uci = event.get("move")
                if not move_uci or move_uci.lower().replace(" ", "") not in legal_moves:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Illegal or missing move. Retrying...'})}\n\n"
                    # We just break here. The frontend will hit the endpoint again if it wants to retry.
                    break
                
                move_uci = move_uci.lower().replace(" ", "")
                if engine.make_move(move_uci):
                    elapsed = round(time.time() - start_time, 2)
                    yield f"data: {json.dumps({'type': 'success', 'move': move_uci, 'time': elapsed, 'fen': engine.get_fen(), 'game_over': engine.is_game_over()})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Engine rejected move.'})}\n\n"
            else:
                yield f"data: {json.dumps(event)}\n\n"
                
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/api/debug_logs")
def debug_logs():
    return {"prompt": agent.get_last_prompt()}

@app.get("/api/state")
def get_state():
    return {"fen": engine.get_fen(), "game_over": engine.is_game_over()}

@app.get("/api/download_pgn")
def download_pgn():
    if not webview.windows:
        return {"success": False, "error": "No window found"}
    
    window = webview.windows[0]
    result = window.create_file_dialog(
        webview.FileDialog.SAVE, 
        directory='', 
        save_filename='gemma_match.pgn'
    )
    
    if result:
        file_path = result if isinstance(result, str) else result[0]
        with open(file_path, 'w') as f:
            f.write(engine.get_pgn_str())
        return {"success": True, "path": file_path}
    
    return {"success": False, "error": "Cancelled"}

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == '__main__':
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1)
    
    webview.create_window('Gemma Chess - AI Grandmaster', 'http://127.0.0.1:8000', width=1280, height=850)
    webview.start()
