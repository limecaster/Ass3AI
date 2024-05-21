import math
import random
from chessboard import ChessBoard

class Node:
    def __init__(self, game, current_player, parent=None):
        self.game = game
        self.current_player = current_player
        self.parent = parent
        
        self.children = []
        self.expandable_move = self.game.get_all_possible_moves(self.current_player)
        self.visit_count = 0
        self.value_sum = 0
        
    def is_fully_expanded(self):
        return len(self.expandable_move) == 0 and len(self.children) > 0

    def get_ucb(self, child):
        q_value = 1 - ((child.value_sum / child.visit_count) + 1) / 2
        return q_value + math.sqrt(2 * math.log(self.visit_count) / child.visit_count)

    def select(self):
        best_child = None
        best_ucb = -float('inf')
        
        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
        
        return best_child
    
    def expand(self):
        if len(self.expandable_move) == 0:
            return None
        
        move = self.expandable_move.pop()
        new_node = self.game.copy()
        new_node.make_move(move)
        next_turn_player = 'white' if self.current_player == 'black' else 'black'
        
        child = Node(new_node, next_turn_player, self)
        self.children.append(child)
        
        return child

    def simulate(self):
        current_game = self.game.copy()
        current_player = self.current_player
        
        while not current_game.is_game_over():
            possible_moves = current_game.get_all_possible_moves(current_player)
            move = random.choice(possible_moves)
            current_game.make_move(move)
            current_player = 'white' if current_player == 'black' else 'black'
        
        return current_game.get_winner()
    
    def backpropagate(self, value):
        self.visit_count += 1
        if type(value) == str:
            if value == self.current_player:
                value = 1
            elif value == 'draw':
                value = 0
            else:
                value = -1
        self.value_sum += value
        
        if self.parent:
            self.parent.backpropagate(value)

        
class MCTS:
    def __init__(self, game, current_player:str, max_iter=1000):
        self.root = Node(game, current_player)
        self.max_iter = max_iter
    
    def search(self):
        for _ in range(self.max_iter):
            node = self.root
            while not node.game.is_game_over():
                if not node.is_fully_expanded():
                    child = node.expand()
                    if child:
                        value = child.simulate()
                        child.backpropagate(value)
                        break
                else:
                    node = node.select()
            else:
                value = node.simulate()
                node.backpropagate(value)

if __name__ == '__main__':
    game = ChessBoard(draw_board=False)
    mcts = MCTS(game, 'white')
    mcts.search()
    print("Root node")
    for child in mcts.root.children:
        print(child.value_sum, child.visit_count)
        print(child.game.board)
        print()
