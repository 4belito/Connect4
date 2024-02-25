import time
import random
import numpy as np

from player import Player 


rows, cols = 7, 8


class Random(Player):
    '''
    Drop the disc randomly on any of the columns of the board
    '''
    
    def __init__(self, rows=rows, columns=cols):
        self.rows=rows
        self.cols=columns

    def setup(self):
        pass

    def play(self, board: np.ndarray) -> int:
        return np.random.randint(self.cols)
    

class SmartRandom(Player):
    '''
    Randomly drop the disc into any column on the board that is not full.
    '''
    def __init__(self, rows=rows, columns=cols):
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
    

class LazySmartRandom(Player):
    '''
    Similar to SmartRandom, but wait for some time before each move and during the setup.
    '''

    def __init__(self, rows=rows, columns=cols):
        self.rows=rows
        self.cols=columns

    
    def setup(self):
        self.moves=np.arange(self.cols)
        time.sleep(0.99)
        print(self.__class__.__name__ + ': ...Hmm?')


    def play(self, board: np.ndarray) -> int:
        time.sleep(random.random() + 0.05)
        valid_moves = self.valid_moves(board)
        i = np.random.randint(0, len(valid_moves))
        return valid_moves[i]
    
    def valid_moves(self, board: np.ndarray) -> np.ndarray:
        return self.moves[board[0,:]==0]


class DropLowest(Player):
    '''
    Drop the disc in the column with fewer discs, breaking ties by choosing the leftmost column
    '''
    def __init__(self, rows=rows, columns=cols):
        self.rows=rows
        self.cols=columns
    
    
    def setup(self):
        pass

    def play(self, board: np.ndarray) -> int:
        col_filled=self.cols_filled(board)
        return np.argmin(col_filled)
    

    def cols_filled(self, board: np.ndarray) -> np.ndarray:
        return np.sum(board!=0,axis=0)








