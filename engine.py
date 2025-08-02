import random, time
import numpy as np
from typing import Callable

from model_base import ModelBase
from model_hardcoded import ModelHardcoded

class Game:
    def __init__(self):
        self.player_1 = ModelBase()
        # self.player_2 = ModelBase()
        # self.player_1 = ModelHardcoded()
        self.player_2 = ModelHardcoded()

        # History
        self.player_1_wins_history = []
        self.player_2_wins_history = []
        self.player_1_boats_history = []
        self.player_2_boats_history = []

    def start_game(self):
        # Current game
        self.player_1_hits = np.zeros((10, 10))
        self.player_2_hits = np.zeros((10, 10))
        self.player_1_misses = np.zeros((10, 10))
        self.player_2_misses = np.zeros((10, 10))

    def end_game(self):
        # Which one has all the boats hit?
        if np.sum(self.player_1_hits) == np.sum(self.player_1_boats):
            self.player_1_wins_history.append(1)
            self.player_2_wins_history.append(0)
        elif np.sum(self.player_2_hits) == np.sum(self.player_2_boats):
            self.player_1_wins_history.append(0)
            self.player_2_wins_history.append(1)
        else:
            raise ValueError("Game not ended or sth??")

        # Add histories
        self.player_1_boats_history.append(self.player_1_boats)
        self.player_2_boats_history.append(self.player_2_boats)

    def loop_play(self,
        report_board_callback: Callable[[bool, np.ndarray, np.ndarray, np.ndarray], None],
        sleep_time: float = 0.5,
    ):
        current_player = random.choice([self.player_1, self.player_2])
        self.player_1_boats = self.player_1.place_boats(self.player_1_boats_history, self.player_2_boats_history, self.player_1_wins_history)
        self.player_2_boats = self.player_2.place_boats(self.player_2_boats_history, self.player_1_boats_history, self.player_2_wins_history)

        # Report
        report_board_callback(True, self.player_1_boats, self.player_1_hits, self.player_1_misses)
        report_board_callback(False, self.player_2_boats, self.player_2_hits, self.player_2_misses)
        time.sleep(sleep_time)

        while np.sum(self.player_1_hits) < np.sum(self.player_1_boats) and np.sum(self.player_2_hits) < np.sum(self.player_2_boats):
            if current_player == self.player_1:
                shoot_pos = self.player_1.play(
                    self.player_1_boats_history,
                    self.player_2_boats_history,
                    self.player_1_wins_history,
                    self.player_1_boats,
                    self.player_1_hits,
                    self.player_1_misses,
                    self.player_2_hits,
                    self.player_2_misses,
                )
                if self.player_2_boats[shoot_pos[0], shoot_pos[1]] == 1:
                    self.player_2_hits[shoot_pos[0], shoot_pos[1]] = 1
                else:
                    self.player_2_misses[shoot_pos[0], shoot_pos[1]] = 1
            else:
                shoot_pos = self.player_2.play(
                    self.player_2_boats_history,
                    self.player_1_boats_history,
                    self.player_2_wins_history,
                    self.player_2_boats,
                    self.player_2_hits,
                    self.player_2_misses,
                    self.player_1_hits,
                    self.player_1_misses,
                )
                if self.player_1_boats[shoot_pos[0], shoot_pos[1]] == 1:
                    self.player_1_hits[shoot_pos[0], shoot_pos[1]] = 1
                else:
                    self.player_1_misses[shoot_pos[0], shoot_pos[1]] = 1
            current_player = self.player_1 if current_player == self.player_2 else self.player_2

            report_board_callback(True, self.player_1_boats, self.player_1_hits, self.player_1_misses)
            report_board_callback(False, self.player_2_boats, self.player_2_hits, self.player_2_misses)
            time.sleep(sleep_time)
        