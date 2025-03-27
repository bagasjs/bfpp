import raylib as rl
import random
import math

WINDOW_TITLE  = b"Game Of Life - Paused (Press Space to Advance Game State)"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 800 

ROWS = 80
COLS = 80
CELL_WIDTH = int(WINDOW_WIDTH/COLS)
CELL_HEIGHT = int(WINDOW_HEIGHT/ROWS)

rl.InitWindow(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
rl.SetTargetFPS(24)
def clamp(x: int, min: int, max: int):
    if x < min:
        return min
    if x > max:
        return max
    return x

class GameOfLife:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [ False for _ in range(rows*cols) ]

    def cell_at(self, row, col) -> bool:
        assert (row >= 0 and row < self.rows) and (col >= 0 and col < self.cols)
        return self.cells[row * self.cols + col]

    def cell_set(self, row, col, state: bool):
        assert (row >= 0 and row < self.rows) and (col >= 0 and col < self.cols)
        self.cells[row * self.cols + col] = state

    def count_nbors(self, row, col) -> int:
        assert (row >= 0 and row < self.rows) and (col >= 0 and col < self.cols)
        n = 0
        for i in range(max(row - 1, 0), min(row + 2, self.rows)):
            for j in range(max(col - 1, 0), min(col + 2, self.cols)):
                if i == row and j == col:
                    continue
                if self.cell_at(i, j):
                    n += 1
        return n

    def reset(self):
        self.cells = [False for _ in range(self.rows * self.cols)]

    def advance_state(self):
        new_cells = [False for _ in range(self.rows * self.cols)]

        for i in range(self.rows):
            for j in range(self.cols):
                current_state = self.cell_at(i, j)
                count_nbors = self.count_nbors(i, j)

                # Any live cell with fewer than two live neighbors dies, as if by underpopulation.
                if current_state == True and count_nbors < 2:
                    new_cells[i * self.cols + j] = False

                # Any live cell with two or three live neighbors lives on to the next generation.
                elif current_state == True and (count_nbors == 2 or count_nbors == 3):
                    new_cells[i * self.cols + j] = True 

                # Any live cell with more than three live neighbors dies, as if by overpopulation.
                elif current_state == True and count_nbors > 3:
                    new_cells[i * self.cols + j] = False

                # Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.
                elif current_state == False and count_nbors == 3:
                    new_cells[i * self.cols + j] = True

        self.cells = new_cells

game = GameOfLife(ROWS, COLS)

continuous_mode = False
erasing_mode = False

print("GAME OF LIFE")
print("Keybindings:")
print("[R]     Reset")
print("[E]     Toggle erase/draw mode")
print("[C]     Toggle continued/paused mode")
print("[Space] Advance the game state on paused mode")

while not rl.WindowShouldClose():
    if rl.IsKeyPressed(rl.KEY_R):
        game.reset()

    if rl.IsKeyPressed(rl.KEY_E):
        erasing_mode = not erasing_mode

    if rl.IsKeyPressed(rl.KEY_C):
        continuous_mode = not continuous_mode
        if continuous_mode:
            rl.SetWindowTitle(b"Game Of Life")
        else:
            rl.SetWindowTitle(b"Game Of Life - Paused (Press Space to Advance Game State)")

    if continuous_mode:
        game.advance_state()
    else:
        if rl.IsKeyPressed(rl.KEY_SPACE):
            game.advance_state()

    if rl.IsMouseButtonDown(rl.MOUSE_BUTTON_LEFT):
        x = rl.GetMouseX()
        y = rl.GetMouseY()
        col = math.floor(x/CELL_WIDTH)
        row = math.floor(y/CELL_HEIGHT)
        game.cell_set(row, col, not erasing_mode)

    rl.BeginDrawing()
    rl.ClearBackground(rl.BLACK)
    for i in range(0, game.rows):
        for j in range(0, game.cols):
            rl.DrawRectangleLines(j*CELL_WIDTH, i*CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT, rl.GRAY)
            if game.cell_at(i, j):
                rl.DrawRectangle(j*CELL_WIDTH, i*CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT, rl.WHITE)
    rl.EndDrawing()

rl.CloseWindow()
