import math
import random

import chess
import chess.pgn
import chess.engine

class Node:
    def __init__(self, board):
        self.M = 0
        self.V = 0
        self.board = board
        self.visitedMovesAndNodes = []
        self.nonVisitedLegalMoves = []
        
        self.parent = None
        for move in board.legal_moves:
            self.nonVisitedLegalMoves.append(move)
        
    def isLeaf(self):
        return len(self.nonVisitedLegalMoves) != 0
    
    def isTerminal(self):
        return len(self.nonVisitedLegalMoves) == 0 and len(self.visitedMovesAndNodes) == 0
    
class MCTS:
    def __init__(self, board, maxIter):
        self.root = Node(board)
        self.maxIter = maxIter
        
    def selection(self, node):
        if node.isLeaf() or node.isTerminal():
            return node
        
        maxUCTChild = None
        maxUCTValue = -float('inf')
        for move, child in node.visitedMovesAndNodes:
            uctValue = self.uct(child, node)
            if uctValue > maxUCTValue:
                maxUCTValue = uctValue
                maxUCTChild = child
        if maxUCTChild is None:
            raise ValueError ("Could not identify child with best UCT value ")
        
        return self.selection(maxUCTChild)


    def uct(self, node, parent):
        return node.M + math.sqrt(2 * math.log(parent.V) / node.V)
    

    def expansion(self, node):
        move = random.choice(node.nonVisitedLegalMoves)
        node.nonVisitedLegalMoves.remove(move)
        board = node.board.copy()
        board.push(move)
        child = Node(board)
        child.parent = node
        node.visitedMovesAndNodes.append((move, child))
        return child
    
    def simulation(self, node):
        board = node.board.copy()
        while board.outcome(claim_draw = True) is None:
            move = random.choice(list(board.legal_moves))
            board.push(move)
        
        payout = 0.5
        outcome = board.outcome(claim_draw = True)
        
        if outcome == 1:
            payout = 1
        elif outcome == -1:
            payout = 0
        elif outcome == 0:
            payout = 0.5
        
        return payout
    
    def backpropagation(self, node, result):
        node.M = ((node.M * node.V) + result) / (node.V + 1)
        node.V += 1

        if node.parent is not None:
            self.backpropagation(node.parent, result)
    
if __name__ == "__main__":
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    root = MCTS(board, 200)
    for i in range(root.maxIter):
        node = root.selection(root.root)
        if not node.isTerminal():
            node = root.expansion(node)
        result = root.simulation(node)
        root.backpropagation(node, result)
    root.root.visitedMovesAndNodes.sort(key = lambda x: x[1].V, reverse = True)
    print([(m.uci(), child.M , child.V) for m, child in root.root.visitedMovesAndNodes[0:10]])
        