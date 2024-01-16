# Connect 4 Game

![Game Animation](https://upload.wikimedia.org/wikipedia/commons/a/ad/Connect_Four.gif)


This repository contains code for the Connect 4 game. It provides the interface for each player to program game logic, and then for players to be pitted against each other. 

## Rules

1. The board is a 6-row, 7-column grid erected vertically.
2. Each column is a shaft, such that a piece dropped in a column will fall to the bottom (or on top of the previous piece.)
3. Players take turns choosing which column to drop their piece in.
4. The objective of the game is to drop pieces such that and 4 of your pieces are connected horizintally, vertically, or diagonally first.
5. If there are no more empty spots left, and no player has connected 4 of their pieces, the game is a draw.

## Installing
The code requires python=3.9 numpy. You can pip install or conda install these packages. It is recommended to use a virtual environment.

## Interface
This repository provides the Player class which includes their game logic. It is in turn used by the Connect4Board class to run the game.

The Player class has two methods which may be overridden:

setup() is called at the beginning of the game, and may be used to set up any game logic (loading stuff etc.). It is a timed method, and taking too long will cause the player to lose by default.
play(self, board: np.ndarray) -> int takes the current state of the board, and returns the column index to put the piece in. If the move is invalid, the player loses by default. A move is invalid if the column index is out of bounds, or if the column has no more space left.
When writing up your player, you may subclass the Player class, or write your own, but with these method signatures.

The Connect4Board class plays matches between two players. It has the play(p1, p2) -> str, str, list[int] method that returns the winner, reason for win, and the list of moves as a list of column indices.

p1, p2 are the string names of the modules containing the player object.

* If you have your own Player class in a file myplayer.py in the working directory, you can simply pass myplayer.
* If your player is named something else, then specify the class name like myplayer/Playa
* If the player is in a nested module. For example if you'd need to write from players.simple import Dumbo, then specify the player as players.simple/Dumbo.

A Jupiter Notebook, play.ipynb, is provided along with some dummy players to learn how to use the Connect4Board class to set up a game between two players.
