import chess

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()

    def get_legal_moves(self):
        return [move.uci() for move in self.board.legal_moves]

    def make_move(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except ValueError:
            return False

    def get_fen(self):
        return self.board.fen()

    def get_history(self):
        # Returns standard algebraic notation of the game so far
        board_copy = chess.Board()
        history = []
        for i, move in enumerate(self.board.move_stack):
            if i % 2 == 0:
                history.append(f"{i//2 + 1}. {board_copy.san(move)}")
            else:
                history.append(f"{board_copy.san(move)}")
            board_copy.push(move)
        return " ".join(history)

    def get_pgn_str(self):
        import chess.pgn
        game = chess.pgn.Game.from_board(self.board)
        game.headers["Event"] = "Gemma Chess Match"
        game.headers["Site"] = "Local Desktop App"
        game.headers["White"] = "Human Player"
        game.headers["Black"] = "Gemma 3 4B (Agentic)"
        return str(game)

    def get_last_move_san(self):
        if not self.board.move_stack:
            return "None (Start of game)"
        temp_board = self.board.copy()
        last_move = temp_board.pop()
        return temp_board.san(last_move)

    def is_game_over(self):
        return self.board.is_game_over()
