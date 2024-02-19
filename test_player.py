from player import Player
import numpy as np

if __name__ == "__main__":
    p = Player(3, 3)

    array = np.array([[1, 0, 1, 2, 2, 0, 4, 5],
                  [1, 0, 2, 2, 2, 4, 0, 5],
                  [1, 0, 2, 2, 2, 4, 0, 5],
                  [1, 0, 2, 2, 2, 4, 4, 5],
                  [1, 0, 2, 2, 2, 4, 4, 5],
                  [1, 0, 2, 2, 2, 4, 4, 5],
                  [1, 0, 2, 2, 2, 4, 4, 5]])

    p.play(array)