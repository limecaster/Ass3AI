import random
import chess.engine
import chess

class Agent:
    def __init__(self, color, elo_rating=0):
        self.color = color
        self.elo_rating = elo_rating
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish\stockfish-windows-x86-64-avx2.exe")
        self.depth = self.elo_to_skill_level()
        
    def get_color(self):
        return self.color
    
    def elo_to_skill_level(self):
        if self.elo_rating < 500:
            return 0
        elif self.elo_rating < 800:
            return 5
        elif self.elo_rating < 1200:
            return 10
        elif self.elo_rating < 1800:
            return 15
        elif self.elo_rating < 2200:
            return 20
        else:
            return 25
    
    def get_move(self, board):
        result = self.engine.play(board, chess.engine.Limit(depth=self.depth))
        return result.move
    
    def __del__(self):
        self.engine.quit()