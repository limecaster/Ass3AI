import math
import chess
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
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    print(board)
    model = NeuralNet()  # Initialize your neural network here
    model.load_state_dict(torch.load("chess_model.pth"))
    model.eval()
    
    root = Node(board)
    root.expand(model)
    mcts = MCTS(model)
    mcts.search(root)

    best_move = max(root.children.items(), key=lambda item: item[1].visit_count)[0]
    print(f"Best move: {best_move.uci()}")
