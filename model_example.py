import numpy as np

from model_base import ModelBase

class ModelExample(ModelBase):

    def place_boats(self,
        past_own_boats: list[np.ndarray],
        past_enemy_boats: list[np.ndarray],
        past_wins: list[int],
    ) -> np.ndarray:
        # This to use random placement, otherwise code w/e you want:
        return super().place_boats(
            past_own_boats=past_own_boats,
            past_enemy_boats=past_enemy_boats,
            past_wins=past_wins,
        )

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