import numpy as np
import importlib
import random

from contextlib import contextmanager
import threading
import _thread


from player import Player


ROWS = 6
COLUMNS = 7

TIMEOUT_MOVE = 1
TIMEOUT_SETUP = 1
MAX_INVALID_MOVES = 0
timed_out = False 




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
        self, rows=ROWS, columns=COLUMNS, timeout_move=TIMEOUT_MOVE,
        timeout_setup=TIMEOUT_SETUP, max_invalid_moves=MAX_INVALID_MOVES, 
        deterministic: bool=True,       
    ):
        """
        rows : int -- number of rows in the game
        columns : int -- number of columns in the game
        time_out_secs : float -- time in seconds after which other player is declared winner
        """

        # collect max and min player vunetids for logging scores
        self.agents = {}
        self.rows = rows
        self.columns = columns
        self.timeout_move = timeout_move
        self.timeout_setup = timeout_setup
        self.max_invalid_moves = max_invalid_moves
        self.deterministic = deterministic

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
        player: Player = player_cls()
        return player
    
    def reset_board(self):
        self._board =  np.zeros((self.rows,self.columns), dtype=int)
    
    def process_move(self, column, board):
        n_spots=sum(board[:,column]==0)
        if n_spots:
            board[n_spots-1,column]=1
            is_valid = True
        else: 
            is_valid = False
        return is_valid,board  
    
    def check_row(self, vec):
        count=0
        for i in range(len(vec)):
            if vec[i]==1:
                count+=1
            else:
                count=0
            if count==4:
                vec[i-3:i+1]=2*np.ones(4, dtype=int)
                return vec
        return None
    
    def check_if_winner(self, board):
        #Horizontal checking
        for row in range(self.rows):
            row_end=self.check_row(board[row,:])
            if row_end is not None:
                board[row,:]=row_end
                return board
        #Vertical checking    
        for column in range(self.columns):
            row_end=self.check_row(board[:,column])
            if row_end is not None:
                board[:,column]=row_end
                return board
        
        #Diagonal checking  
        d_min=min(self.rows,self.columns)
        d_max=max(self.rows,self.columns)
        diag_len=[i for i in range(4,d_min)]+(d_max-d_min+1)*[d_min]+[i for i in range(d_min-1,3,-1)]
        for diag in range(3,self.rows+self.columns-4):
            #main diagonals(decreasing from left to right)
            row=max(0,self.rows-1-diag)
            column=max(0,diag-self.rows+1)
            diagonal=[board[row+i][column+i] for i in range(diag_len[diag-3])]
            row_end=self.check_row(diagonal)
            if row_end is not None:
                for i in range(diag_len[diag-3]):
                    board[row+i][column+i]=row_end[i]
                return board
            # anti-diagonals(increasing from left to right)
            row=min(diag,self.rows-1)
            diagonal=[board[row-i][column+i] for i in range(diag_len[diag-3])]
            row_end=self.check_row(diagonal)
            if row_end is not None:
                for i in range(diag_len[diag-3]):
                    board[row-i][column+i]=row_end[i]
                return board
        return None 

    def play(self, player1, player2):
        global timed_out
        timed_out = False 

        # Randomly swap p1, p2 for first move.
        if self.deterministic:
            p1, p1piece = (player1, +1)
            p2, p2piece = (player2, -1)
        else:
            toss = random.randint(0, 1)
            p1, p1piece = (player1, +1) if toss==1 else (player2, -1)
            p2, p2piece = (player2, -1) if toss==1 else (player1, +1)


        self.reset_board()
        winner, reason, moves = None, '', []
        
        p1_cls = self.load_players(p1)
        p2_cls = self.load_players(p2)


        with time_limit(self.timeout_setup, 'sleep'):
            p1_cls.setup()
        
            
        if timed_out == True:
            winner, reason = p2, 'Setup timeout'
            return winner, reason, moves
         

        with time_limit(self.timeout_setup, 'sleep'):
            p2_cls.setup()
        
        if timed_out == True:
            winner, reason = p1, 'Setup timeout'
            return winner, reason, moves
        
        
        p1_invalid, p2_invalid = 0, 0
        while True:

            p1_board = self._board * p1piece
        

            with time_limit(self.timeout_setup, 'sleep'):
                move = p1_cls.play(p1_board.copy())
                
                is_valid, p1_board = self.process_move(move, p1_board.copy())
                if  is_valid:
                    self._board = p1_board * p1piece
                    moves.append(move)
                else:
                    p1_invalid += 1
                    if p1_invalid >= self.max_invalid_moves:
                        winner, reason = p2, f'Invalid moves exceeded {self.max_invalid_moves}'
                        break 

                board_end=self.check_if_winner(p1_board)
                if board_end is not None:
                    winner, reason,self._board = p1, 'Connect 4!', board_end*p1piece
                    break
                if not np.sum(p1_board==0):
                    winner, reason = None, 'drawn'
                    break
            
            if timed_out == True:
                winner, reason = p2, 'Move timeout'
                break 

            p2_board = self._board * p2piece
 
            with time_limit(self.timeout_setup, 'sleep'):
                move = p2_cls.play(p2_board.copy())

                is_valid, p2_board = self.process_move(move, p2_board.copy())
                if is_valid:
                    self._board = p2_board * p2piece
                    moves.append(move)
                else:
                    p2_invalid += 1
                    if p2_invalid >= self.max_invalid_moves:
                        winner, reason = p1, f'Invalid moves exceeded {self.max_invalid_moves}' 
                        break 
                
                board_end=self.check_if_winner(p2_board)           
                if board_end is not None:
                    winner, reason,self._board = p2, 'Connect 4!', board_end*p2piece
                    break
                if not np.sum(p1_board==0):
                    winner, reason = None, 'drawn'
                    break
            
            if timed_out == True:
                winner, reason = p1, 'Move timeout'
                break 
        
        return winner, reason, moves