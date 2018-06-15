from .sokobanLogic import Board
import numpy as np
from torch.nn import Sigmoid


class Sokoban():
    def __init__(self, fname):
        with open(fname) as fr:
            self.fcontent = fr.read()
        self.height = None
        self.width = None
        
    def get_initial_board(self):
        """
        Returns an initial state of a board
        """
        board = Board(self.fcontent)
        self.height = board.height
        self.width = board.width
        
        return board

    def get_board_size(self):
        """
        Height and width of the board state.
        """
        return (self.height, self.width)

    def get_action_size(self):
        """
        Returns the size of the state search space.
        """
        return self.height * self.width + 1

    def get_valid_moves(self, board):
        """
        Returns the valid moves in the current game state.
        """
        valid_moves = [0] * self.get_action_size()
        legal_moves = board.get_moves()

        if not legal_moves:
            valid_moves[-1] = 1
        else:
            for (x, y) in legal_moves:
                valid_moves[self.width * x + y] = 1
        
        return np.array(valid_moves)

    def get_next_state(self, board, action):
        """
        Produces the next state derived from an action.
        """
        if action == (self.height * self.width):
            return board
        
        move = (int(action / self.width), action % self.height)
        board.execute_move(move)

        return board

    def has_puzzle_ended(self, board):
        """
        Returns a 1 if the puzzle has been solved and a 0 if it hasn't.
        """
        test = board.end_test()

        if test:
            return 1
        return 0

    def get_symmetries(self, board, pi):
        """
        Rotates the matrix.
        """
        assert(len(pi) == self.height**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.height, self.width))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def string_representation(self, board):
        """
        Returns a string representation of the puzzle state.
        """
        return str(board)

    def get_score(self, board):
        score = board.count_stars()
        median_distance = board.median_distance()
        normalized_distance = Sigmoid(median_distance)
        score += int((1 - normalized_distance) * 100)  # 100 is an arbitrary multiplier to the score
        
        return score

def display(board):
    print(board)
