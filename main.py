import tkinter as tk
import random

CELL_SIZE = 60
BOARD_SIZE = 8
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE

BLACK = "black"
WHITE = "white"
EMPTY = None

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

class OthelloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("オセロ（対CPU）")

        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg='green')
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.info_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.info_label.grid(row=1, column=0, sticky="w", padx=10)

        self.reset_button = tk.Button(root, text="リセット", command=self.reset_game)
        self.reset_button.grid(row=1, column=1, sticky="e", padx=10)

        self.reset_game()

        self.canvas.bind("<Button-1>", self.on_click)

    def reset_game(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = BLACK
        self.canvas.delete("all")
        self.draw_board()
        self.draw_initial_stones()
        self.update_info()

    def draw_board(self):
        self.canvas.delete("hint")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
        self.draw_hints()

    def draw_stone(self, row, col, color):
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 4
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color
        )

    def draw_initial_stones(self):
        self.place_stone(3, 3, WHITE)
        self.place_stone(3, 4, BLACK)
        self.place_stone(4, 3, BLACK)
        self.place_stone(4, 4, WHITE)

    def place_stone(self, row, col, color):
        self.board[row][col] = color
        self.draw_stone(row, col, color)

    def is_valid_pos(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_opponent_color(self, color):
        return BLACK if color == WHITE else WHITE

    def would_flip_any(self, row, col, color):
        if self.board[row][col] is not EMPTY:
            return False
        opponent = self.get_opponent_color(color)
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            stones_to_flip = []

            while self.is_valid_pos(r, c) and self.board[r][c] == opponent:
                stones_to_flip.append((r, c))
                r += dr
                c += dc

            if stones_to_flip and self.is_valid_pos(r, c) and self.board[r][c] == color:
                return True
        return False

    def get_valid_moves(self, color):
        return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.would_flip_any(r, c, color)]

    def has_valid_moves(self, color):
        return any(self.would_flip_any(r, c, color) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def flip_stones(self, row, col, color):
        opponent = self.get_opponent_color(color)
        flipped = []

        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            stones_to_flip = []

            while self.is_valid_pos(r, c) and self.board[r][c] == opponent:
                stones_to_flip.append((r, c))
                r += dr
                c += dc

            if self.is_valid_pos(r, c) and self.board[r][c] == color:
                flipped.extend(stones_to_flip)

        for r, c in flipped:
            self.place_stone(r, c, color)

        return len(flipped) > 0

    def count_stones(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        return black, white

    def update_info(self):
        black, white = self.count_stones()
        self.info_label.config(text=f"黒: {black}　白: {white}　次の手番: {'黒' if self.turn == BLACK else '白'}")
        self.draw_hints()

    def check_game_over(self):
        if not self.has_valid_moves(BLACK) and not self.has_valid_moves(WHITE):
            black, white = self.count_stones()
            if black > white:
                winner = "黒の勝ち！"
            elif white > black:
                winner = "白の勝ち！"
            else:
                winner = "引き分け！"
            self.info_label.config(text=f"黒: {black}　白: {white}　{winner}")
            return True
        return False

    def draw_hints(self):
        self.canvas.delete("hint")
        for row, col in self.get_valid_moves(self.turn):
            x = col * CELL_SIZE + CELL_SIZE // 2
            y = row * CELL_SIZE + CELL_SIZE // 2
            radius = 5
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="yellow", tags="hint"
            )

    def cpu_move(self):
        moves = self.get_valid_moves(self.turn)
        if not moves:
            return False
        row, col = random.choice(moves)
        self.flip_stones(row, col, self.turn)
        self.place_stone(row, col, self.turn)
        self.turn = self.get_opponent_color(self.turn)
        return True

    def on_click(self, event):
        if self.check_game_over():
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if not self.is_valid_pos(row, col) or not self.would_flip_any(row, col, self.turn):
            return

        self.flip_stones(row, col, self.turn)
        self.place_stone(row, col, self.turn)
        self.turn = self.get_opponent_color(self.turn)

        self.update_info()

        # CPUのターン（白）
        if self.turn == WHITE:
            if self.has_valid_moves(WHITE):
                self.root.after(500, self.cpu_turn)
            else:
                self.turn = BLACK
                self.update_info()

    def cpu_turn(self):
        if self.check_game_over():
            return

        moved = self.cpu_move()
        if not moved:
            self.turn = BLACK
        self.update_info()
        self.check_game_over()

if __name__ == "__main__":
    root = tk.Tk()
    app = OthelloApp(root)
    root.mainloop()