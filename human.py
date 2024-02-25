
import numpy as np
import sys

class Player:
    '''
    Randomly drop the disc into any column on the board that is not full.
    '''

    def __init__(self, rows, columns):
        self.rows=rows
        self.cols=columns


    def setup(self):
        pass

    def play(self, board: np.ndarray) -> int:
        print(f'board:\n{board}')
        sys.stdout.flush()
        return int(input(f'Colum Move[0-{self.cols-1}]: '))
    
