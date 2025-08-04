import re, os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from tqdm import tqdm

from util import (
    SMALL_SHIP_LEN, MIDDLE_1_SHIP_LEN, MIDDLE_2_SHIP_LEN,
    BIG_SHIP_LEN, BIGGEST_SHIP_LEN
)
from parallel import run_in_parallel

BOARD_X = 10
BOARD_Y = 10
NUM_THREADS = 8
    
def __repr_can_ship_be_placed(
    placed: list[tuple[int, int, int, bool]],
    ship_len: int,
    start_x: int,
    start_y: int,
    is_vertical: bool,
    missed_coords: set[tuple[int, int]] = set()
) -> bool:
    combos_pos = __combo_pos_maker(ship_len, start_x, start_y, is_vertical)
    if len(list(zip(*combos_pos))) == 0:
        return False
    # print(combos_pos)
    # print(len(list(zip(*combos_pos))))
    # print(list(zip(*combos_pos))[0])
    # exit(1)
    # print(ship_len, "xy", start_x, start_y, is_vertical, len(missed_coords))
    for x, y in zip(*combos_pos):
        # print(f"> {x}, {y}")
        # print("__repr_can_ship_be_placed checking", "len", ship_len, "xy", start_x, start_y, is_vertical, x, y)
        # import time; time.sleep(0.1)  # Simulate some processing delay
        if (x, y) in missed_coords:
            # print("> > Nope")
            return False
        for p in placed:
            for xo, yo in zip(*__combo_pos_maker(p[0], p[1], p[2], p[3])):
                if x == xo and y == yo:
                    return False
    return True


def __combo_maker(ship_len: int) -> list[tuple[int, int, bool]]:
    combos = []
    for start_x in range(0, BOARD_X - ship_len):
        for start_y in range(0, BOARD_Y):
            combos.append((start_x, start_y, False))  # Horizontal
    for start_x in range(0, BOARD_X):
        for start_y in range(0, BOARD_Y - ship_len):
            combos.append((start_x, start_y, True))  # Vertical
    return combos

def __combo_pos_maker(ship_len: int, start_x: int, start_y: int, is_vertical: bool) -> tuple[list[int], list[int]]:
    if is_vertical:
        # Check if start_x + ship_len exceeds BOARD_X
        if start_x + ship_len > BOARD_X:
            return [], []
        return list(range(start_x, start_x + ship_len)), [start_y] * ship_len
    else:
        # Check if start_y + ship_len exceeds BOARD_Y
        if start_y + ship_len > BOARD_Y:
            return [], []
        return [start_x] * ship_len, list(range(start_y, start_y + ship_len))

def __heatmap_runner(data_points):
    worker_heatmap = np.zeros((BOARD_X, BOARD_Y)).astype(np.int64)
    for data_point in data_points:
        board = data_point["suggested_board"]
        worker_heatmap[board == 1] += 1
    return worker_heatmap

def __runner(
        biggest_ship_start_x: int, 
        biggest_ship_start_y: int,
        biggest_ship_is_vertical: bool,
        hits_coords: set[tuple[int, int]],
        missed_coords: set[tuple[int, int]] = set()
) -> pd.DataFrame:
    data_piece = []

    # Quick check if we can place the smallest ship on each row, col
    misses = np.array([
        [1 if (x, y) in missed_coords else 0 for y in range(BOARD_Y)] 
        for x in range(BOARD_X)
    ])
    can_small_fit_vertically_based_on_start_pos = np.zeros((BOARD_X, BOARD_Y)).astype(bool)
    can_small_fit_horizontally_based_on_start_pos = np.zeros((BOARD_X, BOARD_Y)).astype(bool)
    for row in range(BOARD_X):
        s = ''.join('O' if (row, col) in missed_coords else '.' for col in range(BOARD_Y))
        all_start_positions_of_dot_dot = [m.start() for m in re.finditer(r'\.\.', s)]
        for col in all_start_positions_of_dot_dot:
            can_small_fit_horizontally_based_on_start_pos[row, col] = True
    for col in range(BOARD_Y):
        s = ''.join('O' if (row, col) in missed_coords else '.' for row in range(BOARD_X))
        all_start_positions_of_dot_dot = [m.start() for m in re.finditer(r'\.\.', s)]
        for row in all_start_positions_of_dot_dot:
            can_small_fit_vertically_based_on_start_pos[row, col] = True



    placed = [ (BIGGEST_SHIP_LEN, biggest_ship_start_x, biggest_ship_start_y, biggest_ship_is_vertical) ]

    for big_ship_start_x, big_ship_start_y, big_ship_is_vertical in __combo_maker(BIG_SHIP_LEN):
        if not __repr_can_ship_be_placed(placed, BIG_SHIP_LEN, 
                                         big_ship_start_x, big_ship_start_y, big_ship_is_vertical,
                                         missed_coords):
            # print("Skipping chonk")
            continue
        # print(f"[INFO] Placing big ship at ({big_ship_start_x}, {big_ship_start_y}) {'vertically' if big_ship_is_vertical else 'horizontally'}")
        placed.append((BIG_SHIP_LEN, big_ship_start_x, big_ship_start_y, big_ship_is_vertical))
        
        for middle_2_ship_start_x, middle_2_ship_start_y, middle_2_ship_is_vertical in __combo_maker(MIDDLE_2_SHIP_LEN):
            if not __repr_can_ship_be_placed(placed, MIDDLE_2_SHIP_LEN, 
                                            middle_2_ship_start_x, middle_2_ship_start_y, 
                                            middle_2_ship_is_vertical,
                                            missed_coords):
                continue
            placed.append((MIDDLE_2_SHIP_LEN, middle_2_ship_start_x, middle_2_ship_start_y, middle_2_ship_is_vertical))

            for middle_1_ship_start_x, middle_1_ship_start_y, middle_1_ship_is_vertical in __combo_maker(MIDDLE_1_SHIP_LEN):
                if not __repr_can_ship_be_placed(placed, MIDDLE_1_SHIP_LEN, 
                                                middle_1_ship_start_x, middle_1_ship_start_y, 
                                                middle_1_ship_is_vertical,
                                                missed_coords):
                    continue
                placed.append((MIDDLE_1_SHIP_LEN, middle_1_ship_start_x, middle_1_ship_start_y, middle_1_ship_is_vertical))

                for small_ship_start_x, small_ship_start_y, small_ship_is_vertical in __combo_maker(SMALL_SHIP_LEN):
                    if (small_ship_is_vertical and not can_small_fit_vertically_based_on_start_pos[small_ship_start_x, small_ship_start_y]) or \
                       (not small_ship_is_vertical and not can_small_fit_horizontally_based_on_start_pos[small_ship_start_x, small_ship_start_y]):
                        continue
                    if not __repr_can_ship_be_placed(placed, SMALL_SHIP_LEN, 
                                                    small_ship_start_x, small_ship_start_y, 
                                                    small_ship_is_vertical,
                                                    missed_coords):
                        continue

                    placed.append((SMALL_SHIP_LEN, small_ship_start_x, small_ship_start_y, small_ship_is_vertical))

                    # Make sure it works with game so far
                    suggested_board = np.zeros((BOARD_X, BOARD_Y)).astype(bool)
                    for ship_len, start_x, start_y, is_vertical in placed:
                        if is_vertical:
                            suggested_board[start_x:start_x + ship_len, start_y] = True
                        else:
                            suggested_board[start_x, start_y:start_y + ship_len] = True
                    suggested_coords = set([(int(x), int(y)) for x, y in zip(*np.where(suggested_board))])
                    suggested_coords_str = [f"({x}, {y})" for x, y in sorted(suggested_coords)]
                    hits_coords_str = [f"({x}, {y})" for x, y in sorted(hits_coords)]
                    mark_to_skip = False
                    for coord_str in hits_coords_str:
                        if coord_str not in suggested_coords_str:
                            mark_to_skip = True
                            break
                    if mark_to_skip:
                        placed.pop()
                        continue
                    
                    data_piece.append({
                        "suggested_board": suggested_board.astype(int),
                    })

                    # data_piece.append({
                    #     "biggest_x": biggest_ship_start_x,
                    #     "biggest_y": biggest_ship_start_y,
                    #     "biggest_is_vertical": biggest_ship_is_vertical,
                    #     "big_x": big_ship_start_x,
                    #     "big_y": big_ship_start_y,
                    #     "middle2_x": middle_2_ship_start_x,
                    #     "middle2_y": middle_2_ship_start_y,
                    #     "middle1_x": middle_1_ship_start_x,
                    #     "middle1_y": middle_1_ship_start_y,
                    #     "small_x": small_ship_start_x,
                    #     "small_y": small_ship_start_y
                    # })

                    # for x in range(BOARD_X):
                    #     print("\t", end="")
                    #     for y in range(BOARD_Y):
                    #         if (x, y) in hits_coords and (x, y) in suggested_coords:
                    #             print("Q", end="")
                    #         elif (x, y) in suggested_coords:
                    #             print("S", end="")
                    #         elif (x, y) in missed_coords:
                    #             print("O", end="")
                    #         elif (x, y) in hits_coords:
                    #             print("X", end="")
                    #         else:
                    #             print(".", end="")
                    #     print()
                    # print()

                    placed.pop()

                placed.pop()
                    
            placed.pop()

        placed.pop()
        
    return data_piece



def board_heatmap(hits: np.ndarray, misses: np.ndarray) -> np.ndarray:    
    # hits = hits.astype(int)
    # hits[hits > 0.5] = 1
    # misses = misses.astype(int)
    # misses[misses > 0.5] = 1
    # print("->", np.sum(hits), "hits", np.sum(misses), "misses")

    hits_coords = set([(int(x), int(y)) for x, y in zip(*np.where(hits == 1))])
    missed_coords = set([(int(x), int(y)) for x, y in zip(*np.where(misses == 1))])
    print("*>", len(hits_coords), "hits", len(missed_coords), "missed coords")
    print(f"!> {list(hits_coords)[0]} {list(missed_coords)[0]} -- {type(list(missed_coords)[0][0])}")
    work = []
    for biggest_ship_start_x, biggest_ship_start_y, biggest_ship_is_vertical in __combo_maker(BIGGEST_SHIP_LEN):
        if not __repr_can_ship_be_placed([], BIGGEST_SHIP_LEN, biggest_ship_start_x, 
                                         biggest_ship_start_y, biggest_ship_is_vertical,
                                         missed_coords):
            # print(f"[INFO] Skipping biggest ship at ({biggest_ship_start_x}, {biggest_ship_start_y}) {'vertically' if biggest_ship_is_vertical else 'horizontally'}")
            continue
        # print("NOPE")
        # print(sorted(missed_coords))
        # exit(1)
        work.append((
            biggest_ship_start_x, biggest_ship_start_y, biggest_ship_is_vertical,
            hits_coords,
            missed_coords
        ))


    # import os; os.environ["DEBUG"] = "1"  # Enable debug mode for testing
    data_pieces = run_in_parallel(
        worker=__runner,
        work=work,
        num_workers=NUM_THREADS,
        verbose=True
    )

    data = [item for sublist in data_pieces for item in sublist]

    print("COMBINATIONS N =", len(data))

    
    if os.environ.get("DEBUG", "0") == "1" or NUM_THREADS in [-1, 0, 1]:
        heatmap = np.zeros((BOARD_X, BOARD_Y)).astype(np.int64)
        for data_point in (pbar := tqdm(data)):
            board = data_point["suggested_board"]
            pbar.set_description(f"Processing boards")
            heatmap[board == 1] += 1
    else:

        work = [ (data[i:i + 1000],) for i in range(0, len(data), 1000) ]

        print(f"[INFO] Running heatmap worker with {len(work)} chunks of 1000 boards each...")
        heatmaps = run_in_parallel(
            worker=__heatmap_runner,
            work=work,
            num_workers=NUM_THREADS,
            verbose=True
        )

        heatmap = np.zeros((BOARD_X, BOARD_Y)).astype(np.int64)
        for worker_heatmap in (pbar := tqdm(heatmaps)):
            pbar.set_description(f"Combining heatmaps")
            heatmap += worker_heatmap

    print(len(work))
    return heatmap

def board_heatmap_decision(
    hits: np.ndarray, misses: np.ndarray, 
) -> tuple[int, int]:
    """
    Decide whether to run the heatmap based on the number of misses and hits.
    """
    heatmap = board_heatmap(hits, misses)
    # Set hits and misses to 0
    heatmap[hits == 1] = 0
    heatmap[misses == 1] = 0
    # Get the coordinates of the maximum value in the heatmap
    max_coords = np.unravel_index(np.argmax(heatmap, axis=None), heatmap.shape)
    return int(max_coords[0]), int(max_coords[1])


def board_heatmap_should_run(misses: np.ndarray) -> bool:
    # From bool to int
    # misses = misses.astype(int)
    # misses[misses > 0.5] = 1
    missed_coords = set([(int(x), int(y)) for x,y in zip(*np.where(misses == 1))])
    total_coords = BOARD_X * BOARD_Y
    # Always run X%+
    print((round(len(missed_coords) / total_coords * 100, 2), "% missed coords"))
    if len(missed_coords) / total_coords > 0.26-1e-6:
        return True
    return False


if __name__ == "__main__":
    missed_coords = set()
    
    # Tune
    num_hits = 4
    num_missed = int(BOARD_X * BOARD_Y * 0.36)  
    # Don't tune ...

    all_coords = [(x, y) for x in range(BOARD_X) for y in range(BOARD_Y)]
    idxs = np.random.choice(len(all_coords), num_missed, replace=False)
    missed_coords = {all_coords[i] for i in idxs}

    hits_coords = set()
    while len(hits_coords) < num_hits:
        x = np.random.randint(0, BOARD_X)
        y = np.random.randint(0, BOARD_Y)
        if (x, y) not in missed_coords and (x, y) not in hits_coords:
            hits_coords.add((x, y))

    hits = np.zeros((BOARD_X, BOARD_Y)).astype(int)
    for coord in hits_coords:
        x, y = coord
        hits[x, y] = 1

    misses = np.array([
        [1 if (x, y) in missed_coords else 0 for y in range(BOARD_Y)] 
        for x in range(BOARD_X)
    ])
    misses = misses.astype(int)

    for x in range(BOARD_X):
        print("\t", end="")
        for y in range(BOARD_Y):
            if (x, y) in missed_coords:
                print("O", end="")
            elif (x, y) in hits_coords:
                print("X", end="")
            else:
                print(".", end="")
        print()

    print(f"[INFO] Should run?: {board_heatmap_should_run(misses)}")
    print(f"[INFO] {BOARD_X}x{BOARD_Y} Num_hits={num_hits}, Missed coordinates sim: {len(missed_coords)}")

    heatmap = board_heatmap(hits, misses)

    # Normalize
    heatmap = heatmap / np.max(heatmap) if np.max(heatmap) > 0 else heatmap
    heatmap = (heatmap * 10).astype(int)  # Scale to 0-10
    heatmap_txt = heatmap.astype(str)
    heatmap_txt[heatmap_txt == '10'] = 'X'

    for x in range(BOARD_X):
        print("\t", end="")
        for y in range(BOARD_Y):
            print(heatmap_txt[x, y], end="")
        print()