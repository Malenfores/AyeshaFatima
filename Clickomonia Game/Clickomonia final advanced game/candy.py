import pygame
import math
from settings import *


class Candy:

    def __init__(self, row, col, color):

        self.row = row
        self.col = col
        self.color = color

        # Screen position
        self.x = BOARD_X + col * CELL_SIZE
        self.y = BOARD_Y + row * CELL_SIZE

        # Target position
        self.target_x = self.x
        self.target_y = self.y

        # Falling speed
        self.speed = 10

        # Hover highlight
        self.selected = False

        # Special candy
        self.special_type = None

    # =====================================
    # UPDATE
    # =====================================

    def update(self):

        # Vertical movement
        if self.y < self.target_y:

            self.y += self.speed

            if self.y > self.target_y:
                self.y = self.target_y

        elif self.y > self.target_y:

            self.y -= self.speed

            if self.y < self.target_y:
                self.y = self.target_y

        # Horizontal movement
        if self.x < self.target_x:

            self.x += self.speed

            if self.x > self.target_x:
                self.x = self.target_x

        elif self.x > self.target_x:

            self.x -= self.speed

            if self.x < self.target_x:
                self.x = self.target_x

    # =====================================
    # DRAW
    # =====================================

    def draw(self, screen, colors):

        center_x = int(self.x + CELL_SIZE // 2)
        center_y = int(self.y + CELL_SIZE // 2)

        radius = CELL_SIZE // 2 - 5

        # Hover glow
        if self.selected:

            pygame.draw.circle(
                screen,
                WHITE,
                (center_x, center_y),
                radius + 7,
                3
            )

            radius += 4

        # Main candy
        pygame.draw.circle(
            screen,
            colors[self.color],
            (center_x, center_y),
            radius
        )

        # Shine effect
        pygame.draw.circle(
            screen,
            WHITE,
            (
                center_x - 8,
                center_y - 8
            ),
            radius // 4
        )

        # =====================================
        # DISTINCT SHAPE MARKER (per color)
        # =====================================

        if self.special_type is None:

            self.draw_marker(screen, center_x, center_y, radius)

        # =====================================
        # SPECIAL CANDIES
        # =====================================

        if self.special_type == "bomb":

            pygame.draw.circle(
                screen,
                BLACK,
                (center_x, center_y),
                10
            )

        elif self.special_type == "striped_row":

            pygame.draw.line(
                screen,
                WHITE,
                (center_x - 15, center_y),
                (center_x + 15, center_y),
                4
            )

        elif self.special_type == "striped_column":

            pygame.draw.line(
                screen,
                WHITE,
                (center_x, center_y - 15),
                (center_x, center_y + 15),
                4
            )

        elif self.special_type == "rainbow":

            pygame.draw.circle(
                screen,
                WHITE,
                (center_x, center_y),
                12,
                3
            )

    # =====================================
    # SHAPE MARKER (makes each candy color visually distinct)
    # =====================================

    def draw_marker(self, screen, center_x, center_y, radius):

        marker = self.color % 8

        mark_color = (255, 255, 255)

        if marker == 0:

            # Star
            outer = radius * 0.5
            inner = radius * 0.22
            points = []

            for i in range(10):
                angle = -math.pi / 2 + i * math.pi / 5
                r = outer if i % 2 == 0 else inner
                points.append((
                    center_x + r * math.cos(angle),
                    center_y + r * math.sin(angle)
                ))

            pygame.draw.polygon(screen, mark_color, points, 2)

        elif marker == 1:

            # Square
            size = radius * 0.6
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (center_x, center_y)
            pygame.draw.rect(screen, mark_color, rect, 2)

        elif marker == 2:

            # Triangle
            points = [
                (center_x, center_y - radius * 0.45),
                (center_x - radius * 0.45, center_y + radius * 0.3),
                (center_x + radius * 0.45, center_y + radius * 0.3),
            ]
            pygame.draw.polygon(screen, mark_color, points, 2)

        elif marker == 3:

            # Diamond
            points = [
                (center_x, center_y - radius * 0.45),
                (center_x + radius * 0.45, center_y),
                (center_x, center_y + radius * 0.45),
                (center_x - radius * 0.45, center_y),
            ]
            pygame.draw.polygon(screen, mark_color, points, 2)

        elif marker == 4:

            # Ring
            pygame.draw.circle(
                screen,
                mark_color,
                (center_x, center_y),
                int(radius * 0.45),
                2
            )

        elif marker == 5:

            # Cross
            pygame.draw.line(
                screen, mark_color,
                (center_x - radius * 0.4, center_y),
                (center_x + radius * 0.4, center_y),
                3
            )
            pygame.draw.line(
                screen, mark_color,
                (center_x, center_y - radius * 0.4),
                (center_x, center_y + radius * 0.4),
                3
            )

        elif marker == 6:

            # Hexagon
            points = []
            for i in range(6):
                angle = math.pi / 3 * i
                points.append((
                    center_x + radius * 0.45 * math.cos(angle),
                    center_y + radius * 0.45 * math.sin(angle)
                ))
            pygame.draw.polygon(screen, mark_color, points, 2)

        else:

            # Stripes
            pygame.draw.line(
                screen, mark_color,
                (center_x - radius * 0.4, center_y - radius * 0.2),
                (center_x + radius * 0.4, center_y - radius * 0.2),
                3
            )
            pygame.draw.line(
                screen, mark_color,
                (center_x - radius * 0.4, center_y + radius * 0.2),
                (center_x + radius * 0.4, center_y + radius * 0.2),
                3
            )