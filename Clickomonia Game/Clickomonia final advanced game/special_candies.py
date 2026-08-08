from settings import *


class SpecialCandyManager:

    def activate_row(self, board, row):

        removed = set()

        for col in range(COLS):

            if board.grid[row][col]:

                removed.add((row, col))

        return removed

    def activate_column(self, board, col):

        removed = set()

        for row in range(ROWS):

            if board.grid[row][col]:

                removed.add((row, col))

        return removed

    def activate_bomb(self, board, row, col):

        removed = set()

        for r in range(row - 1, row + 2):

            for c in range(col - 1, col + 2):

                if (
                        0 <= r < ROWS and
                        0 <= c < COLS
                ):

                    if board.grid[r][c]:

                        removed.add((r, c))

        return removed