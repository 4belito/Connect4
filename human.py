
import numpy as np
import sys

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

    def play(self, board: np.ndarray) -> int:
        print(f'board:\n{board}')
        sys.stdout.flush()
        return int(input(f'Colum Move[0-{self.cols-1}]: '))
    
