import chess.pgn
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader

class ChessDataset(Dataset):
    def __init__(self, positions, moves):
        self.positions = positions
        self.moves = moves
    
    def __len__(self):
        return len(self.positions)
    
    def __getitem__(self, idx):
        position = self.positions[idx]
        move = self.moves[idx]
        move_encoded = encode_move(move)
        return position, move_encoded

def board_to_tensor(board):
    piece_map = board.piece_map()
    tensor = np.zeros((8, 8, 14), dtype=np.float32)
    piece_channels = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2, chess.ROOK: 3,
        chess.QUEEN: 4, chess.KING: 5
    }
    for square, piece in piece_map.items():
        row, col = 7 - square // 8, square % 8
        channels = piece_channels[piece.piece_type]
        if piece.color == chess.WHITE:
            tensor[row, col, channels] = 1
        else:
            tensor[row, col, channels + 6] = 1
    tensor[:, :, 12] = 1 if board.turn == chess.WHITE else 0
    if board.has_kingside_castling_rights(chess.WHITE): tensor[7, 7, 13] = 1
    if board.has_queenside_castling_rights(chess.WHITE): tensor[7, 0, 13] = 1
    if board.has_kingside_castling_rights(chess.BLACK): tensor[0, 7, 13] = 1
    if board.has_queenside_castling_rights(chess.BLACK): tensor[0, 0, 13] = 1
    if board.ep_square is not None:
        row, col = 7 - board.ep_square // 8, board.ep_square % 8
        tensor[row, col, 13] = 1
    return torch.tensor(tensor).permute(2, 0, 1)

def parse_pgn_to_tensor(pgn_file):
    positions, moves = [], []
    game_count = 0
    with open(pgn_file, "rt", encoding='utf-8') as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None or game_count == 1000:  # Limiting to 1000 games for example
                break
            board = game.board()
            game_count += 1
            for move in game.mainline_moves():
                positions.append(board_to_tensor(board))
                moves.append(move)
                board.push(move)
    return positions, moves

def encode_move(move):
    from_square = move.from_square
    to_square = move.to_square
    return from_square * 64 + to_square

# Example usage
if __name__ == "__main__":
    positions, moves = parse_pgn_to_tensor("preprocessed_db.pgn")
    dataset = ChessDataset(positions, moves)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
