import math
import chess
import chess.engine
import torch
from neural_net import NeuralNet
from data_preprocessing import board_to_tensor

class Node:
    def __init__(self, board, parent=None):
        self.board = board
        self.parent = parent
        self.children = {}
        self.visit_count = 0
        self.total_value = 0.0
        self.prior_policy = None
        self.value_estimate = 0.0

    def is_expanded(self):
        return len(self.children) > 0

    def expand(self, model):
        legal_moves = list(self.board.legal_moves)
        board_tensor = board_to_tensor(self.board)
        with torch.no_grad():
            policy_probs, value_estimate = model(board_tensor.unsqueeze(0))
        self.prior_policy = policy_probs.squeeze().detach().numpy()
        self.value_estimate = value_estimate.item()

        for i, move in enumerate(legal_moves):
            new_board = self.board.copy()
            new_board.push(move)
            self.children[move] = Node(new_board, parent=self)
            self.children[move].prior_policy = self.prior_policy[i]

class MCTS:
    def __init__(self, model, simulations=800):
        self.model = model
        self.simulations = simulations

    def search(self, root):
        for _ in range(self.simulations):
            node = root
            search_path = [node]
            while node.is_expanded():
                move, node = self.select(node)
                search_path.append(node)
            value = self.simulate(node)
            self.backpropagate(search_path, value)

    def select(self, node):
        total_visits = sum(child.visit_count for child in node.children.values())
        
        # Add a small epsilon to total_visits to avoid division by zero
        total_visits += 1e-8
        
        log_total = math.log(total_visits)
        best_move, best_child = max(node.children.items(), key=lambda item: self.uct(item[1], log_total))
        return best_move, best_child


    def uct(self, child, log_total):
        if child.visit_count == 0:
            return float('inf')  # Return infinity for unvisited nodes
        exploration_factor = math.sqrt(log_total / child.visit_count)
        return child.total_value / child.visit_count + exploration_factor


    def simulate(self, node):
        if not node.is_expanded():
            node.expand(self.model)
        return node.value_estimate

    def backpropagate(self, path, value):
        for node in reversed(path):
            node.visit_count += 1
            node.total_value += value

# Example usage
if __name__ == "__main__":
    board = chess.Board("rn1q1rk1/1pp1bppp/p1b1pn2/8/P1QP4/5NP1/1P2PPBP/RNB2RK1 w - - 1 10")
    print(board)
    model = NeuralNet()  # Initialize your neural network here
    model.load_state_dict(torch.load("chess_model.pth", map_location=torch.device('cpu')))
    model.eval()
    
    root = Node(board)
    root.expand(model)
    mcts = MCTS(model)
    mcts.search(root)

    best_move = max(root.children.items(), key=lambda item: item[1].visit_count)[0]
    
    # best move from chess engine stockfish
    # Download stockfish engine from https://stockfishchess.org/download/
    engine = chess.engine.SimpleEngine.popen_uci("stockfish\stockfish-windows-x86-64-avx2.exe")
    result = engine.play(board, chess.engine.Limit(time=0.1))
    
    # Compare the best move from MCTS and the best move from the engine
    print(f"Engine's best move: {result.move.uci()}")
    print(f"Best move: {best_move.uci()}")
    engine.quit()
