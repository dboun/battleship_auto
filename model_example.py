import numpy as np

from model_base import ModelBase

class ModelExample(ModelBase):

    def place_boats(self,
        past_own_boats: list[np.ndarray],
        past_enemy_boats: list[np.ndarray],
        past_wins: list[int],
    ) -> np.ndarray:
        ... # return a 10x10 np.ndarray with 1s for boats and 0s for water
        return np.zeros((10, 10))

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
        ... # return (row, col) coords [0, 9] each, for where you shoot
        return (0, 0)