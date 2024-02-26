import numpy as np
import importlib
import random

from contextlib import contextmanager
import threading
import _thread


from player import Player



rows, cols = 7, 8

ROWS = 6
COLS = 7

TIMEOUT_MOVE = 1
TIMEOUT_SETUP = 1
MAX_INVALID_MOVES = 0
CONNECT_NUMBER=5
CYLINDER=False




class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    global timed_out

    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    
    try:
        yield
    except KeyboardInterrupt:
        # raise TimeoutException("Timed out for operation {}".format(msg))
        timed_out = True
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


class Connect4Board():
    def __init__(
        self, rows=ROWS, cols=COLS,connect_number=CONNECT_NUMBER,cylinder=CYLINDER,
        timeout_move=TIMEOUT_MOVE,timeout_setup=TIMEOUT_SETUP, max_invalid_moves=MAX_INVALID_MOVES,
        deterministic: bool=True):
        """
        rows: int -- number of rows in the game
        cols: int -- number of columns in the game
        connect_number: int -- number of discs you need to connect to win the game
        cylinder: bool -- True if the board is a cylinder (left-hand side of the board is connected to the right-hand side)
        timeout_move: float -- time in seconds for a move after which the other player is declared the winner
        timeout_setup: float -- time in seconds each player has to set up the game
        max_invalid_moves: int -- maximum number of invalid moves allowed
        deterministic: bool -- When true, player 1 starts (piece_color=+) and player 2 plays second (piece_color=-). Otherwise, this is chosen randomly.
        """

        assert CONNECT_NUMBER <= rows, 'The number of discs to connect has to be less than or equal to the number of rows.'
        assert CONNECT_NUMBER <= cols, 'The number of discs to connect has to be less than or equal to the number of columns.'

        self.agents = {}
        self.rows = rows
        self.cols = cols
        self.timeout_move = timeout_move
        self.timeout_setup = timeout_setup
        self.max_invalid_moves = max_invalid_moves
        self.deterministic = deterministic
        self.connect_number=connect_number
        self.cylinder=cylinder
        self.reset_board()

        
    def __str__(self) -> str:
        board = self._board.copy().astype(int)
        return np.array2string(board)
    
    def load_players(self, p_path):
        class_name = 'Player'
        try:
            components = p_path.split('/')
            module_name = components[0]
            player_module = importlib.import_module(module_name)

            if len(components) == 2:
                class_name = components[1]

        except Exception as exc:
            print(f'Could not load player {p_path} due to: {exc}')
            return -1
        player_cls = getattr(player_module, class_name)
        player: Player = player_cls(rows=self.rows, cols=self.cols, connect_number=self.connect_number, timeout_setup=self.timeout_setup, timeout_move=self.timeout_move, max_invalid_moves=self.max_invalid_moves, cylinder=self.cylinder)
        return player
    
    def reset_board(self):
        self.move=None
        self._board =  np.zeros((self.rows,self.cols), dtype=int)
    
    def process_move(self, column, board):
        is_valid = False
        if isinstance(column, (int,np.int32,np.int64)) and 0 <= column < self.cols:
            n_spots=sum(board[:,column]==0)
            if n_spots:
                board[n_spots-1,column]=1
                is_valid = True            
        return is_valid,board  
    
    def check_config(self, board,config):
        b1,b2=board.shape
        c1,c2=config.shape
        for i in range(b1-c1+1):
            for j in range(b2-c2+1):
                if np.sum(board[i:i+c1,j:j+c2]*config)==self.connect_number:
                    board[i:i+c1,j:j+c2][config==1]=2
                    if self.cylinder:
                        board[:,:self.connect_number-1][board[:,-self.connect_number+1:]==2]=2
                        board=board[:,:-self.connect_number+1]
                    return True,board
        return False,board

    def check_if_winner(self, board):
        if self.cylinder:
            board=np.concatenate((board, board[:,:self.connect_number-1]),axis=1)

        #Horizontal checking
        config=np.ones((1,self.connect_number), dtype=int)
        end,board=self.check_config(board,config)
        if end:
            return board
        
        #Vertical checking
        config=np.ones((self.connect_number,1), dtype=int)
        end,board=self.check_config(board,config) 
        if end:
            return board
        
        #Diagonal checking
        config=np.eye(self.connect_number,dtype=int)
        end,board=self.check_config(board,config) 
        if end:
            return board
        
        #Diagonal checking
        config=np.flipud(np.eye(self.connect_number,dtype=int))
        end,board=self.check_config(board,config) 
        if end:
            return board
        
        return None

    def play(self, player1, player2):
        global timed_out
        timed_out = False 

        # Randomly swap p1, p2 for first move.
        if self.deterministic:
            p1= player1
            p2= player2
        else:
            toss = random.randint(0, 1)
            p1 = player1 if toss==1 else player2
            p2 = player2 if toss==1 else player1


        self.reset_board()
        winner, reason, moves = None, '', []
        
        p1_cls = self.load_players(p1)
        p2_cls = self.load_players(p2)


        with time_limit(self.timeout_setup, 'sleep'):
            p1_cls.setup(piece_color='+')
        
            
        if timed_out == True:
            winner, reason = p2, 'Setup timeout'
            return winner, reason, moves
         

        with time_limit(self.timeout_setup, 'sleep'):
            p2_cls.setup(piece_color='-')
        
        if timed_out == True:
            winner, reason = p1, 'Setup timeout'
            return winner, reason, moves
        
        
        p1_invalid, p2_invalid = 0, 0
        while True:
            p1_board = self._board            
            try:
                with time_limit(self.timeout_move, 'sleep'):
                    self.move = p1_cls.play(p1_board.copy())
                is_valid, p1_board = self.process_move(self.move, p1_board.copy())
            except Exception as exc:
                is_valid=False
                print(f"Error {exc} has occurred with player {p1}:")
            if  is_valid:
                self._board = p1_board 
                moves.append(self.move)
            else:
                p1_invalid += 1
                if p1_invalid >= self.max_invalid_moves:
                    winner, reason = p2, f'Invalid moves exceeded {self.max_invalid_moves}'
                    break 

            board_end=self.check_if_winner(p1_board)
            if board_end is not None:
                winner, reason,self._board = p1, f'Connect {self.connect_number}!', board_end
                break
            if not np.sum(self._board==0):
                winner, reason = None, 'draw'
                break
                
            if timed_out == True:
                winner, reason = p2, 'Move timeout'
                break 

            p2_board = self._board * (-1)
 
            
            try:
                with time_limit(self.timeout_move, 'sleep'):
                    self.move = p2_cls.play(p2_board.copy())
                is_valid, p2_board = self.process_move(self.move, p2_board.copy())
            except Exception as exc:
                is_valid=False
                print(f"Error {exc} has occurred with player {p2}:")
            if is_valid:
                self._board = p2_board * (-1)
                moves.append(self.move)
            else:
                p2_invalid += 1
                if p2_invalid >= self.max_invalid_moves:
                    winner, reason = p1, f'Invalid moves exceeded {self.max_invalid_moves}' 
                    break 
                
            board_end=self.check_if_winner(p2_board)           
            if board_end is not None:
                winner, reason,self._board = p2, f'Connect {self.connect_number}!', board_end*(-1)
                break
            if not np.sum(self._board==0):
                winner, reason = None, 'draw'
                break
                
            if timed_out == True:
                winner, reason = p1, 'Move timeout'
                break 
        
        return winner, reason, moves