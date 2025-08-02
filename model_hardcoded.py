import random
import numpy as np
from scipy import ndimage

from model_base import ModelBase

class ModelHardcoded(ModelBase):

    def play(self,
                past_own_boats: list[np.ndarray],
                past_enemy_boats: list[np.ndarray],
                past_wins: list[int],
                own_boats: np.ndarray,
                own_hits: np.ndarray,
                own_misses: np.ndarray,
                enemy_hits: np.ndarray,
                enemy_misses: np.ndarray,
    ) -> tuple[int, int]:
        _enemy_hits = np.zeros((10, 10)).astype(bool)
        _enemy_hits[enemy_hits > 0.5] = True
        _enemy_hits[enemy_hits < 0.5] = False
        _enemy_misses = np.zeros((10, 10)).astype(bool)
        _enemy_misses[enemy_misses > 0.5] = True
        _enemy_misses[enemy_misses < 0.5] = False
        enemy_hits = _enemy_hits
        enemy_misses = _enemy_misses

        # Create a board with hits and misses
        board = np.array([['.' for _ in range(10)] for _ in range(10)])
        board[enemy_hits] = 'X'
        board[enemy_misses] = 'O'
        board = board.tolist()
        
        rows = list(range(10))
        cols = list(range(10))
        random.shuffle(rows)
        random.shuffle(cols)

        # First obvious ones
        for row in rows:
            s = ''.join(board[row][col] for col in range(10))
            if 'XX.' in s:
                print(f"> ModelHardcoded: Found XX. in row {row+1}")
                col = s.index('XX.') + 2
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)
            if '.XX' in s:
                print(f"> ModelHardcoded: Found .XX in row {row+1}")
                col = s.index('.XX')
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)
        for col in cols:
            s = ''.join(board[row][col] for row in range(10))
            if 'XX.' in s:
                print(f"> ModelHardcoded: Found XX. in col {col+1}")
                row = s.index('XX.') + 2
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)
            if '.XX' in s:
                print(f"> ModelHardcoded: Found .XX in col {col+1}")
                row = s.index('.XX')
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)

        # Then next to lone Xs
        for row in rows:
            s = ''.join(board[row][col] for col in range(10))
            if '.X' in s:
                col = s.index('.X')
                X_x, X_y = row, col+1
                if self.__is_lone_X(X_x, X_y, board):
                    print(f"> ModelHardcoded: Found .X in row {row+1}")
                    assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                    return (row, col)
            if 'X.' in s:
                col = s.index('X.') + 1
                X_x, X_y = row, col-1
                if self.__is_lone_X(X_x, X_y, board):
                    print(f"> ModelHardcoded: Found X. in row {row+1}")
                    assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                    return (row, col)
        for col in cols:
            s = ''.join(board[row][col] for row in range(10))
            if '.X' in s:
                row = s.index('.X')
                X_x, X_y = row+1, col
                if self.__is_lone_X(X_x, X_y, board):
                    print(f"> ModelHardcoded: Found .X in col {col+1}")
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)
            if 'X.' in s:
                row = s.index('X.') + 1
                X_x, X_y = row-1, col
                if self.__is_lone_X(X_x, X_y, board):
                    print(f"> ModelHardcoded: Found X. in col {col+1}")
                    assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                    return (row, col)

        # Then with gaps
        for row in rows:
            s = ''.join(board[row][col] for col in range(10))
            if 'X.X' in s or 'X..X' in s or 'X...X' in s or 'X....X' in s:
                print(f"> ModelHardcoded: Found X.X, X..X, X...X, or X....X in row {row+1}")
                col = (
                    s.index('X.X') + 1 if 'X.X' in s else
                    s.index('X..X') + 1 if 'X..X' in s else
                    s.index('X...X') + 1 if 'X...X' in s else
                    s.index('X....X') + 1
                )
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)
        for col in cols:
            s = ''.join(board[row][col] for row in range(10))
            if 'X.X' in s or 'X..X' in s or 'X...X' in s or 'X....X' in s:
                print(f"> ModelHardcoded: Found X.X, X..X, X...X, or X....X in col {col+1}")
                row = (
                    s.index('X.X') + 1 if 'X.X' in s else
                    s.index('X..X') + 1 if 'X..X' in s else
                    s.index('X...X') + 1 if 'X...X' in s else
                    s.index('X....X') + 1
                )
                assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                return (row, col)



        # find the point with the largest distance to the nearest hit/miss
        board_binary = np.zeros((10, 10))
        board_binary[enemy_hits] = 1
        board_binary[enemy_misses] = 1
        # Compute the Manhattan (city block) distance to the nearest non-zero (1) point
        # Invert the array: 1s become 0s (they are sources), and 0s become 1s (targets)
        distance = ndimage.distance_transform_cdt(board_binary == 0, metric='taxicab')

        # If max distance is 1, look for long stretches of dots
        if np.max(distance) == 1:
            for row in rows:
                s = ''.join(board[row][col] for col in range(10))
                if '...' in s:
                    print(f"> ModelHardcoded: Found ... in row {row+1}")
                    col = s.index('...') + 1
                    assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                    return (row, col)
            for col in cols:
                s = ''.join(board[row][col] for row in range(10))
                if '...' in s:
                    print(f"> ModelHardcoded: Found ... in col {col+1}")
                    row = s.index('...') + 1
                    assert enemy_hits[row, col] == 0 and enemy_misses[row, col] == 0, (s, row, col, board[row][col], enemy_hits[row, col], enemy_misses[row, col])
                    return (row, col)

        # Check whether to maximize distance to nearest hit/miss
        if any(enemy_hits.flatten().tolist()) or any(enemy_misses.flatten().tolist()):
            print(f"> ModelHardcoded: Couldn't find a good move, maximizing distance to nearest hit/miss w/ noise")
            # Normalize to 0-1
            distance_norm = distance / np.max(distance)
            # Add noise
            distance_norm = distance_norm + np.random.uniform(-0.2, 0.2, distance_norm.shape)
            # Set know board pieces to distance_norm -100
            distance_norm[enemy_hits] = -1
            distance_norm[enemy_misses] = -1
            highest_distance_coords_tuple = np.unravel_index(distance_norm.argmax(), distance_norm.shape)
            return highest_distance_coords_tuple

        # No good move found, no previous moves made, so we'll just pick a random one
        # Better implementation with coords
        print(f"> ModelHardcoded: Couldn't find a good move, so picking a random one")
        board_hits_or_misses = np.zeros((10, 10))
        board_hits_or_misses[enemy_hits == 1] = 1
        board_hits_or_misses[enemy_misses == 1] = 1
        _unhit_where = np.where(board_hits_or_misses == 0)
        unhit_coords = [(x,y) for x,y in zip(_unhit_where[0], _unhit_where[1])]
        random.shuffle(unhit_coords)
        return unhit_coords[0]



    def __is_lone_X(self, x, y, board):
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                if x_offset == 0 and y_offset == 0:
                    continue
                try:
                    if board[x+x_offset][y+y_offset] == 'X':
                        return False
                except IndexError:
                    continue
        return True