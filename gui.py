import tkinter as tk
from tkinter import ttk
import numpy as np
import threading

from engine import Game

CELL_SIZE = 30  # pixel size of a single board cell
grid_size = 10


class BattleshipGUI:
    """Simple Tkinter visualisation for the Battleships game"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Battleships")

        # Game
        self.game = Game()
        self.game.start_game()

        # Track previous hit/miss states to highlight the latest move
        self.prev_hits_p1 = np.zeros((10, 10))
        self.prev_misses_p1 = np.zeros((10, 10))
        self.prev_hits_p2 = np.zeros((10, 10))
        self.prev_misses_p2 = np.zeros((10, 10))

        # create two canvases (player 1 / player 2)
        board_px = CELL_SIZE * grid_size
        self.canvas_p1 = tk.Canvas(root, width=board_px, height=board_px, bg="white")
        self.canvas_p1.grid(row=0, column=0, padx=10, pady=10)

        self.canvas_p2 = tk.Canvas(root, width=board_px, height=board_px, bg="white")
        self.canvas_p2.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(root, text="Player 1").grid(row=1, column=0)
        ttk.Label(root, text="Player 2").grid(row=1, column=1)

        # draw empty boards to begin with
        self._draw_board(True, np.zeros((10, 10)), np.zeros((10, 10)), np.zeros((10, 10)))
        self._draw_board(False, np.zeros((10, 10)), np.zeros((10, 10)), np.zeros((10, 10)))

        # Start game loop in background thread to keep UI responsive
        threading.Thread(target=self.run_game_loop, daemon=True).start()

    # ---- game loop helpers -------------------------------------------------

    def run_game_loop(self):
        """Run the blocking game loop in a background thread."""
        self.game.loop_play(report_board_callback=self.draw_board)
        self.game.end_game()

    # ---- board drawing -----------------------------------------------------

    def draw_board(self, is_player_1: bool, boats, hits, misses) -> None:
        """Thread-safe board update – schedule the real drawing on the Tk thread."""
        # `after` ensures `_draw_board` runs on the main GUI thread
        self.root.after(0, self._draw_board, is_player_1, boats, hits, misses)

    def _draw_board(self, is_player_1: bool, boats, hits, misses) -> None:
        """Render one 10x10 board on the given canvas. Must run on the Tk thread."""
        canvas = self.canvas_p1 if is_player_1 else self.canvas_p2

        # Determine which cell changed since last frame (i.e. the most recent move)
        prev_hits = self.prev_hits_p1 if is_player_1 else self.prev_hits_p2
        prev_misses = self.prev_misses_p1 if is_player_1 else self.prev_misses_p2
        last_move_mask = ((hits == 1) & (prev_hits == 0)) | ((misses == 1) & (prev_misses == 0))

        # Clear previous frame
        canvas.delete("all")

        # draw grid
        for r in range(grid_size + 1):
            # horizontal grid line
            canvas.create_line(0, r * CELL_SIZE, grid_size * CELL_SIZE, r * CELL_SIZE)
            # vertical grid line
            canvas.create_line(r * CELL_SIZE, 0, r * CELL_SIZE, grid_size * CELL_SIZE)

        # draw contents
        for row in range(grid_size):
            for col in range(grid_size):
                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

                # highlight the latest move with a light yellow square
                if last_move_mask[row, col]:
                    canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill="#ffff99", outline="")

                # underlying boat (grey oval)
                if boats[row, col] == 1:
                    canvas.create_oval(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill="grey", outline="")

                # overlay with hit / miss marks (takes precedence)
                if hits[row, col] == 1:
                    # red oval (slightly smaller) on top of the boat square
                    canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill="red", outline="")
                elif misses[row, col] == 1:
                    # blue square in the middle for a miss
                    canvas.create_rectangle(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill="blue", outline="")

        # Save current state for the next frame so we can find the next move
        if is_player_1:
            self.prev_hits_p1 = hits.copy()
            self.prev_misses_p1 = misses.copy()
        else:
            self.prev_hits_p2 = hits.copy()
            self.prev_misses_p2 = misses.copy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()
