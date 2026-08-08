import random
from settings import *
from candy import Candy


class Board:

    def __init__(self, num_colors):

        self.num_colors = num_colors
        self.grid = []

        self.create_board()

    # =====================================
    # CREATE BOARD
    # =====================================

    def create_board(self):

        while True:

            self.grid = []

            for row in range(ROWS):

                current_row = []

                for col in range(COLS):

                    # Better board generation
                    if row > 0 and random.random() < 0.10:

                        color = self.grid[row - 1][col].color

                    elif col > 0 and random.random() < 0.10:

                        color = current_row[col - 1].color

                    else:

                        color = random.randint(
                            0,
                            self.num_colors - 1
                        )

                    current_row.append(
                        Candy(row, col, color)
                    )

                self.grid.append(current_row)

            # Make sure enough moves exist
            if self.count_possible_groups() >= 4:
                break

    # =====================================
    # DRAW
    # =====================================

    def draw(self, screen):

        for row in range(ROWS):

            for col in range(COLS):

                candy = self.grid[row][col]

                if candy is not None:

                    candy.draw(
                        screen,
                        CANDY_COLORS
                    )

    # =====================================
    # UPDATE
    # =====================================

    def update(self):

        for row in range(ROWS):

            for col in range(COLS):

                candy = self.grid[row][col]

                if candy:

                    candy.update()

    # =====================================
    # CLEAR SELECTION
    # =====================================

    def clear_selection(self):

        for row in range(ROWS):

            for col in range(COLS):

                candy = self.grid[row][col]

                if candy:

                    candy.selected = False

    # =====================================
    # GET GROUP
    # =====================================

    def get_group(self, row, col):

        if row < 0 or row >= ROWS:
            return set()

        if col < 0 or col >= COLS:
            return set()

        if self.grid[row][col] is None:
            return set()

        color = self.grid[row][col].color

        stack = [(row, col)]

        visited = set()

        while stack:

            r, c = stack.pop()

            if (r, c) in visited:
                continue

            if r < 0 or r >= ROWS:
                continue

            if c < 0 or c >= COLS:
                continue

            candy = self.grid[r][c]

            if candy is None:
                continue

            if candy.color != color:
                continue

            visited.add((r, c))

            stack.extend([

                (r + 1, c),
                (r - 1, c),
                (r, c + 1),
                (r, c - 1)

            ])

        return visited

    # =====================================
    # HIGHLIGHT GROUP
    # =====================================

    def highlight_group(self, row, col):

        self.clear_selection()

        group = self.get_group(row, col)

        if len(group) < 2:
            return

        for r, c in group:

            candy = self.grid[r][c]

            if candy:

                candy.selected = True
        # =====================================
    # REMOVE GROUP
    # =====================================

    def remove_group(self, group, force=False):

        if len(group) < 2 and not force:
            return

        for r, c in group:

            self.grid[r][c] = None

        self.apply_gravity()

        # Agar moves khatam ho jayein aur candies bachi hon
        if self.count_remaining() > 0:

            if self.count_possible_groups() == 0:

                self.shuffle()

    # =====================================
    # APPLY GRAVITY
    # =====================================

    def apply_gravity(self):

        for col in range(COLS):

            candies = []

            for row in range(ROWS):

                if self.grid[row][col]:

                    candies.append(
                        self.grid[row][col]
                    )

            empty = ROWS - len(candies)

            new_column = [None] * empty + candies

            for row in range(ROWS):

                self.grid[row][col] = new_column[row]

                candy = self.grid[row][col]

                if candy:

                    candy.row = row
                    candy.col = col

                    candy.target_x = (
                        BOARD_X +
                        col * CELL_SIZE
                    )

                    candy.target_y = (
                        BOARD_Y +
                        row * CELL_SIZE
                    )

        self.shift_columns_left()

    # =====================================
    # SHIFT EMPTY COLUMNS
    # =====================================

    def shift_columns_left(self):

        columns = []

        for col in range(COLS):

            column = []

            has_candy = False

            for row in range(ROWS):

                candy = self.grid[row][col]

                column.append(candy)

                if candy:

                    has_candy = True

            if has_candy:

                columns.append(column)

        while len(columns) < COLS:

            columns.append([None] * ROWS)

        for col in range(COLS):

            for row in range(ROWS):

                candy = columns[col][row]

                self.grid[row][col] = candy

                if candy:

                    candy.row = row
                    candy.col = col

                    candy.target_x = (
                        BOARD_X +
                        col * CELL_SIZE
                    )

                    candy.target_y = (
                        BOARD_Y +
                        row * CELL_SIZE
                    )            
        # =====================================
    # SHUFFLE BOARD
    # =====================================

    def shuffle(self):

        candies = []

        # Collect all remaining colors
        for row in range(ROWS):
            for col in range(COLS):

                candy = self.grid[row][col]

                if candy:
                    candies.append(candy.color)

        random.shuffle(candies)

        index = 0

        # Put shuffled colors back
        for row in range(ROWS):
            for col in range(COLS):

                candy = self.grid[row][col]

                if candy:

                    candy.color = candies[index]

                    candy.row = row
                    candy.col = col

                    candy.target_x = (
                        BOARD_X +
                        col * CELL_SIZE
                    )

                    candy.target_y = (
                        BOARD_Y +
                        row * CELL_SIZE
                    )

                    index += 1

        # Ensure shuffle creates moves
        if self.count_possible_groups() == 0 and self.count_remaining() > 0:

            # Avoid endless dead boards. Create a guaranteed playable pair.
            self.create_guaranteed_move()


    # =====================================
    # GUARANTEED MOVE CREATION
    # =====================================

    def create_guaranteed_move(self):

        candies = [
            self.grid[r][c]
            for r in range(ROWS)
            for c in range(COLS)
            if self.grid[r][c]
        ]

        if len(candies) < 2:
            return

        # Try random swaps until a valid group is created
        for _ in range(300):
            a = random.choice(candies)
            b = random.choice(candies)

            if a is b:
                continue

            old_a = a.color
            old_b = b.color

            a.color = old_b
            b.color = old_a

            if self.count_possible_groups() > 0:
                return

            a.color = old_a
            b.color = old_b

        # Final fallback: make two adjacent candies same color
        for r in range(ROWS):
            for c in range(COLS-1):
                if self.grid[r][c] and self.grid[r][c+1]:
                    self.grid[r][c+1].color = self.grid[r][c].color
                    return

    # =====================================
    # COUNT POSSIBLE GROUPS
    # =====================================

    def count_possible_groups(self):

        checked = set()

        groups = 0

        for row in range(ROWS):

            for col in range(COLS):

                if (row, col) in checked:
                    continue

                group = self.get_group(row, col)

                checked |= group

                if len(group) >= 2:
                    groups += 1

        return groups

    # =====================================
    # HAS MOVES
    # =====================================

    def has_moves(self):

        return self.count_possible_groups() > 0

    # =====================================
    # COUNT REMAINING
    # =====================================

    def count_remaining(self):

        total = 0

        for row in self.grid:

            for candy in row:

                if candy:

                    total += 1

        return total                