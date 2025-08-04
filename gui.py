import tkinter as tk
from tkinter import ttk
import numpy as np
import threading

from engine import Game
from model_base import ModelBase
from model_user import ModelUser
from model_hardcoded import ModelHardcoded
from model_heatmap import ModelHeatmap

CELL_SIZE = 30  # pixel size of a single board cell
grid_size = 10


class BattleshipGUI:
    """Simple Tkinter visualisation for the Battleships game"""

    # ---- user interaction state -------------------------------------------
    _waiting_for_click: bool = False  # whether we are currently expecting a user move
    _click_event: 'threading.Event | None' = None  # event used to signal from UI thread to game thread
    _click_result: 'tuple[int, int] | None' = None  # coordinates selected by the user

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Battleships")

        self.show_boats = False

        # Game
        self.game = Game(
            # player_1=ModelUser(fetch_user_move_callback=self.fetch_user_move_callback), 
            # player_1=ModelHardcoded(),
            # player_2=ModelHardcoded()
            player_1=ModelBase(),
            player_2=ModelHeatmap(),
        )
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

    def fetch_user_move_callback(self) -> tuple[int, int]:
        """Block the calling thread until the user clicks a cell on the enemy board.

        This method is executed from the background game loop thread. We cannot
        directly wait for Tk events on that thread, so we use a threading.Event
        to bridge between the Tk main (UI) thread and the game thread. When the
        game expects a move from the human player we:

        1. Create/clear an event and schedule enabling of click handling on the
           Tk thread via `root.after`.
        2. Block on the event until a click happens.
        3. Return the chosen board coordinates (row, col).
        """
        # Prepare synchronisation primitives
        if self._click_event is None:
            self._click_event = threading.Event()
        else:
            self._click_event.clear()

        # Schedule enabling of click mode on UI thread
        self.root.after(0, self._enable_click_mode)

        # Wait until UI thread signals a click has happened
        self._click_event.wait()

        # At this point, _click_result should be populated
        assert self._click_result is not None, "Click result should have been set before event was signalled"
        return self._click_result

    # ---------------------------------------------------------------------
    # Internal helpers for handling user clicks (run on the Tk thread)
    def _enable_click_mode(self):
        """Enable click handling on the enemy board (canvas_p2)."""
        # Only enable if not already waiting – guards against double enable
        if self._waiting_for_click:
            return
        self._waiting_for_click = True
        # Bind mouse click on enemy board (player 2's canvas)
        self.canvas_p2.bind("<Button-1>", self._on_board_click)

    def _on_board_click(self, event):
        """Handle a click on the enemy board – executed on Tk thread."""
        if not self._waiting_for_click:
            return  # Ignore stray clicks

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        # Ensure click is inside the 10x10 board
        if row < 0 or row >= grid_size or col < 0 or col >= grid_size:
            return

        # Store result for game thread and clean-up
        self._click_result = (row, col)
        self._waiting_for_click = False
        self.canvas_p2.unbind("<Button-1>")

        # Signal the waiting game thread that the move is ready
        if self._click_event is not None:
            self._click_event.set()

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
        # _total_hits_or_misses = np.sum(hits) + np.sum(misses)
        # print(f"> gui: Drawing board for player {'player 1' if is_player_1 else 'player 2'} (hits/misses: {_total_hits_or_misses})")
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

        try:
            is_game_over = np.sum(self.game.player_1_hits) == np.sum(self.game.player_1_boats) or np.sum(self.game.player_2_hits) == np.sum(self.game.player_2_boats)
        except:
            is_game_over = False

        # draw contents
        for row in range(grid_size):
            for col in range(grid_size):
                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

                # highlight the latest move with a light yellow square
                if last_move_mask[row, col]:
                    canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill="#ffff99", outline="")

                # underlying boat (grey oval)
                if (self.show_boats or is_game_over) and boats[row, col] == 1:
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
