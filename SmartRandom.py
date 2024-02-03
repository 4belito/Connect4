
import numpy as np

class Player:
    '''
    Randomly drop the disc into any column on the board that is not full.
    '''

    def __init__(self, rows, columns):
        self.rows=rows
        self.cols=columns


    def setup(self):
        self.moves=np.arange(self.cols)

    def play(self, board: np.ndarray) -> int:
        valid_moves = self.valid_moves(board)
        i = np.random.randint(0, len(valid_moves))
        return valid_moves[i]
    
    def valid_moves(self, board: np.ndarray) -> np.ndarray:
        return self.moves[board[0,:]==0]