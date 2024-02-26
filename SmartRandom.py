
import numpy as np


class Player:
    '''
    Randomly drop the disc into any column on the board that is not full.
    '''

    def __init__(self, rows, cols, connect_number, 
                 timeout_setup, timeout_move, max_invalid_moves, 
                 cylinder):
        self.rows = rows
        self.cols = cols
        self.connect_number = connect_number
        self.timeout_setup = timeout_setup
        self.timeout_move = timeout_move
        self.max_invalid_moves = max_invalid_moves
        self.cylinder = cylinder


    def setup(self,piece_color):
        self.piece_color=piece_color
        self.moves=np.arange(self.cols)

    def play(self, board: np.ndarray) -> int:
        valid_moves = self.valid_moves(board)
        i = np.random.randint(0, len(valid_moves))
        return valid_moves[i]
    
    def valid_moves(self, board: np.ndarray) -> np.ndarray:
        return self.moves[board[0,:]==0]