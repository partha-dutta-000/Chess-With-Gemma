def get_chess_prompt(move_history, legal_moves, last_move):
    """
    Generates the prompt for the Gemma 3 LLM.
    You can add conditional logic here later (e.g., different prompts for opening vs endgame).
    """
    
    # Example conditional logic stub:
    # if len(move_history.split()) < 10:
    #     phase_instructions = "We are in the opening phase. Focus on developing pieces and controlling the center."
    # else:
    #     phase_instructions = "Focus on middle-game tactics and king safety."
        
    return f"""You are a highly strategic chess grandmaster playing at an expert level. 

Move History: {move_history if move_history else 'Start of game.'}
Opponent's Last Move: {last_move if last_move else 'None'}
Your Legal Moves (UCI format): {', '.join(legal_moves)}

You MUST follow this exact thought process before making your move:
1. Threat Analysis: The opponent just played {last_move}. What is their threat? Am I in danger?
2. Positional Evaluation: Who controls the center? Are my pieces developed?
3. Candidate Moves: Pick 3 moves from your Legal Moves list and evaluate their pros/cons.
4. Final Decision: On the very last line, output your chosen move wrapped in <move> tags (e.g., <move>e2e4</move>).

You MUST pick exactly one move from the Legal Moves list provided."""
