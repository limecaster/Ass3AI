import math
import chess
import chess.engine
import torch
from neural_net import NeuralNet
from data_preprocessing import board_to_tensor
from agent import Agent
import numpy as np

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
        
        policy_probs = policy_probs.squeeze().detach().numpy()

        # Map policy probs to legal moves
        legal_policy_probs = np.zeros(len(legal_moves))
        for idx, move in enumerate(legal_moves):
            uci_move = move.uci()
            legal_policy_probs[idx] = policy_probs[idx]  # Assuming the model output aligns with legal move indices

        # Normalize probabilities
        legal_policy_probs /= legal_policy_probs.sum()
        
        self.value_estimate = value_estimate.item()

        for move, prob in zip(legal_moves, legal_policy_probs):
            new_board = self.board.copy()
            new_board.push(move)
            self.children[move] = Node(new_board, parent=self)
            self.children[move].prior_policy = prob

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
            if not node.is_expanded():
                node.expand(self.model)
            value = self.simulate(node)
            self.backpropagate(search_path, value)

    def select(self, node):
        total_visits = sum(child.visit_count for child in node.children.values())
        total_visits += 1e-8  # Avoid division by zero
        log_total = math.log(total_visits)
        best_move, best_child = max(node.children.items(), key=lambda item: self.uct(item[1], log_total))
        return best_move, best_child

    def uct(self, child, log_total):
        if child.visit_count == 0:
            return float('inf')  # Return infinity for unvisited nodes
        exploration_factor = math.sqrt(log_total / child.visit_count)
        return child.total_value / child.visit_count + exploration_factor

    def simulate(self, node):
        return node.value_estimate

    def backpropagate(self, path, value):
        for node in reversed(path):
            node.visit_count += 1
            node.total_value += value

# Example usage
if __name__ == "__main__":
    board = chess.Board()
    print(board)
    model = NeuralNet()
    model.load_state_dict(torch.load("chess_model.pth", map_location=torch.device('cpu')))
    model.eval()
    
    # Demo game Agent vs MCTS
    agent = Agent(chess.WHITE)
    mcts = MCTS(model)
    root = Node(board)
    
    move_count = 0
    # Play a game between Agent and MCTS
    while not board.is_game_over():
        if board.turn == agent.get_color():
            move = agent.get_move(board)
            move_count += 1
            print(f"Agent moves: {move}")
            board.push(move)
            # Update root to reflect the new board state
            if move in root.children:
                root = root.children[move]
            else:
                root = Node(board)
        else:
            mcts.search(root)
            best_move, _ = mcts.select(root)
            move_count += 1
            print(f"MCTS moves: {best_move}")
            board.push(best_move)
            # Update root to reflect the new board state
            if best_move in root.children:
                root = root.children[best_move]
            else:
                root = Node(board)
                
    # Statistic of the game
    print("Game over")
    # Open a file for writing
    with open('statistics.txt', 'w') as file:
        file.write("Agent vs MCTS Game Statistics:\n")
        file.write("Agent's color: {}\n".format('white' if agent.get_color() else 'black'))
        file.write("Agent elo rating: {}\n".format(agent.elo_rating))
        file.write("MCTS's color: {}\n".format('black' if agent.get_color() == chess.BLACK else 'white'))
        file.write("Move count: {}\n".format(move_count))
        file.write("Game result: {}\n".format(board.result()))
        file.write("{}\n".format(board))
        file.write("\n \n")
        file.close()

    print("Agent vs MCTS Game Statistics:\n")
    print("Agent's color: {}\n".format(agent.get_color()))
    print("Agent elo rating: {}\n".format(agent.elo_rating))
    print("MCTS's color: {}\n".format(chess.WHITE if agent.get_color() == chess.BLACK else chess.BLACK))
    print("Move count: {}\n".format(move_count))
    print("Game result: {}\n".format(board.result()))
    print("{}\n".format(board))
