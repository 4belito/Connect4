from player import Player
import random
import numpy as np

class minimaxPlayer(Player):
    '''
    Drop the disc randomly on any of the columns of the board
    '''
    
    def __init__(self, rows, columns):
        self.rows=rows
        self.cols=columns

    def setup(self):
        self.search_level = 1 # Set up search level to limit search depth

    def play(self, board: np.ndarray):
        """
        Given a 2D array representing the game board, return an integer value (0,1,2,...,number of columns-1) corresponding to
        the column of the board where you want to drop your disc.
        The coordinates of the board increase along the right and down directions. 

        Parameters
        ----------
        board : np.ndarray
            A 2D array where 0s represent empty slots, +1s represent your pieces,
            and -1s represent the opposing player's pieces.

                `index   0   1   2   . column` \\
                `--------------------------` \\
                `0   |   0.  0.  0.  top` \\
                `1   |   -1  0.  0.  .` \\
                `2   |   +1  -1  -1  .` \\
                `.   |   -1  +1  +1  .` \\
                `row |   left        bottom/right`

        Returns
        -------
        integer corresponding to the column of the board where you want to drop your disc.
        """
        available_actions = np.where(np.any(board==0, axis=0))[0]

        # No available action to explore and no result is returned 
        if len(available_actions) == 0:
            raise NotImplementedError()

        # We are maximizing player, so the next play is by non-maximizing player
        scores = [self.minimax(self.get_board_after_action(action, board, 1), self.search_level, False, -float('inf'), float('inf')) for action in available_actions] 
        return available_actions[np.argmax(scores)]        

    def minimax(self, board, depth, isMaximizingPlayer, alpha, beta):
        if depth == 0:
            return self.heuristic(board, isMaximizingPlayer)   

        available_actions = np.where(board[0] == 0)[0]

        if isMaximizingPlayer:
            # Player who maximize the score
            best_score = -float("inf")
            for action in available_actions:
                score = self.minimax(self.get_board_after_action(action, board, 1), depth - 1, False, alpha, beta)
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score 
        else:
            # Player who minimize the score
            best_score = float("inf")
            for action in available_actions:
                score = self.minimax(self.get_board_after_action(action, board, -1), depth - 1, True, alpha, beta)
                best_score = min(score, best_score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best_score 

    def get_board_after_action(self, action, board, player):
        """
        Returns the board after action. Assume action and board are valid.
        """
        board_after_action = board.copy()
        c = board[:, action]
        zeros = np.where(c==0)[0]
        change_index = np.max(zeros)
        
        board_after_action[change_index][action] = player

        return board_after_action

    def heuristic(self, board, player):
        # We implement the heuristic where we give higher score to more pieces in a row
        scores = self.count_consecutive_pieces(board, player)
        opponent_scores = self.count_consecutive_pieces(board, -player)

        # (# of 4 consecutive * 10^4) + (# of 3 consecutive * 10^3) + (# of 2 consecutive * 10^2)
        score = sum((10**k) * v for k, v in scores.items()) - sum((10**k) * v for k, v in opponent_scores.items())
        return score

    def count_consecutive_pieces(self, board, player):
        # We will only count vertical and horizontals for this programming assignment
        scores = {4: 0, 3: 0, 2: 0}
        
        # Horizontal check
        for row in range(self.rows):
            for col in range(self.cols):
                for length in [2, 3, 4]:  # Check for lengths 2, 3, 4
                    if all((board[row, (col + i) % self.cols] == player) for i in range(length)):
                        scores[length] += 1

        # Vertical
        for col in range(self.cols):
            for row in range(self.rows - 1):  # No need for wraparound in vertical check
                if row == self.rows - 2:
                    length = [2]
                if row == self.rows - 3:
                    length = [2, 3]
                if row < self.rows - 3:
                    length = [2, 3, 4]
                for len in length:  # Check for lengths 2, 3, 4 
                    if all((board[row + i, col] == player) for i in range(len)):
                        scores[len] += 1

        return scores