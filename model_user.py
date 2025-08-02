from typing import Callable

import numpy as np

from model_base import ModelBase

class ModelUser(ModelBase):

    def __init__(self, fetch_user_move_callback: Callable[[], tuple[int, int]]):
        self.fetch_user_move_callback = fetch_user_move_callback

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
        return self.fetch_user_move_callback()