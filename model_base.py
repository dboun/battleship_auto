import random
import numpy as np
from util import (
    SMALL_SHIP_LEN, MIDDLE_1_SHIP_LEN, 
    MIDDLE_2_SHIP_LEN, BIG_SHIP_LEN, 
    BIGGEST_SHIP_LEN
)


class ModelBase:
    def __init__(self):
        pass

    def is_boat_placement_valid(self,
        already_placed_boats: np.ndarray,
        pos_start: tuple[int, int],
        pos_end: tuple[int, int],
        ) -> bool:
        try:
            if already_placed_boats[pos_start[0], pos_start[1]] == 1 or already_placed_boats[pos_end[0], pos_end[1]] == 1:
                return False
            orientation = "horizontal" if pos_start[0] == pos_end[0] else "vertical"
            if orientation == "horizontal":
                for i in range(pos_start[1], pos_end[1]):
                    if already_placed_boats[pos_start[0], i] == 1:
                        return False
            else:
                for i in range(pos_start[0], pos_end[0]):
                    if already_placed_boats[i, pos_start[1]] == 1:
                        return False
        except IndexError:
            return False
        return True

    def place_boats(self, 
        past_own_boats: list[np.ndarray],
        past_enemy_boats: list[np.ndarray],
        past_wins: list[int],
        ) -> np.ndarray:
        """
        Randomly places the 5 battleships on a 10×10 board.

        The `past_*` parameters are part of the public API but are not
        required for this simple random strategy, so they are ignored.
        A value of 1 denotes a ship cell, 0 denotes water.
        """
        # Initialise empty board
        boats = np.zeros((10, 10), dtype=int)

        ship_lengths = [
            SMALL_SHIP_LEN,
            MIDDLE_1_SHIP_LEN,
            MIDDLE_2_SHIP_LEN,
            BIG_SHIP_LEN,
            BIGGEST_SHIP_LEN,
        ]

        for ship_len in ship_lengths:
            placed = False
            while not placed:
                horizontal = random.choice([True, False])

                if horizontal:
                    row = random.randint(0, 9)
                    col_start = random.randint(0, 9 - ship_len + 1)
                    pos_start = (row, col_start)
                    pos_end = (row, col_start + ship_len - 1)
                else:
                    col = random.randint(0, 9)
                    row_start = random.randint(0, 9 - ship_len + 1)
                    pos_start = (row_start, col)
                    pos_end = (row_start + ship_len - 1, col)

                # Ensure the ship fits on the board and does not overlap
                if self.is_boat_placement_valid(boats, pos_start, pos_end):
                    if horizontal:
                        boats[pos_start[0], pos_start[1]:pos_start[1] + ship_len] = 1
                    else:
                        boats[pos_start[0]:pos_start[0] + ship_len, pos_start[1]] = 1
                    placed = True

        return boats

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
        print(f"If this is printed, you are using random play. Override.")

        # Choose a random position on enemy board that is not already hit/missed
        pos = (np.random.randint(0, 10), np.random.randint(0, 10))
        while enemy_hits[pos] == 1 or enemy_misses[pos] == 1:
            pos = (np.random.randint(0, 10), np.random.randint(0, 10))
        return pos