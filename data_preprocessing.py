"""Data source:https://www.chess.com/forum/view/general/chess-pgn-database-over-9-million-games
which contains 9 million chess games in PGN format.
"""

import chess.pgn
import torch
import os
import numpy as np
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader

class ChessDataset(Dataset):
    """Chess dataset class for batch loading PGN files."""
    def __init__(self, positions, moves):
        self.positions = positions
        self.moves = moves
    
    def __len__(self):
        return len(self.positions)
    
    def __getitem__(self, idx):
        position = self.positions[idx]
        move = self.moves[idx]
        move_encoded = encode_move(move)
        # Return class index instead of one-hot encoding
        return position, move_encoded  # Convert to integer
    
    
def board_to_tensor(board):
    """Encode the chess board to a 8x8x14 tensor representation."""
    piece_map = board.piece_map()
    tensor = np.zeros((8, 8, 14), dtype=np.float32)
    
    # Define piece types and their channels
    piece_channels = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5
    }
    
    for square, piece in piece_map.items():
        row = 7 - square // 8
        col = square % 8
        channels = piece_channels[piece.piece_type]
        if piece.color == chess.WHITE:
            tensor[row, col, channels] = 1
        else:
            tensor[row, col, channels + 6] = 1
        
    # Encode the player's turn channel
    tensor[:, :, 12] = 1 if board.turn == chess.WHITE else 0
    
    # Encode castling move
    if board.has_kingside_castling_rights(chess.WHITE):
        tensor[7, 7, 13] = 1  # Kingside castling rights for white
    if board.has_queenside_castling_rights(chess.WHITE):
        tensor[7, 0, 13] = 1  # Queenside castling rights for white
    if board.has_kingside_castling_rights(chess.BLACK):
        tensor[0, 7, 13] = 1  # Kingside castling rights for black
    if board.has_queenside_castling_rights(chess.BLACK):
        tensor[0, 0, 13] = 1  # Queenside castling rights for black
    
    # Encode en passant square
    if board.ep_square is not None:
        row = 7 - board.ep_square // 8
        col = board.ep_square % 8
        tensor[row, col, 13] = 1
    
    return torch.tensor(tensor).permute(2, 0, 1)


def parse_pgn_to_tensor(pgn_file):
    """Parse PGN file and return a list of tensors."""
    positions = []
    moves = []
    with open(pgn_file, mode="rt", encoding='utf-8') as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                positions.append(board_to_tensor(board))
                moves.append(move)
                board.push(move)
    return positions, moves

def encode_move(move):
    """Encode the move to a 0-63 integer."""
    from_square = move.from_square
    to_square = move.to_square
    # Combine the squares into a single index
    return from_square * 64 + to_square

# Example usage
positions, moves = parse_pgn_to_tensor("preprocessed_db.pgn")
dataset = ChessDataset(positions, moves)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)