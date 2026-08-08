import pygame
from settings import *


class Menu:

    def __init__(self):

        self.title_font = pygame.font.SysFont(
            "arial",
            55,
            bold=True
        )

        self.button_font = pygame.font.SysFont(
            "arial",
            35
        )

        self.start_button = pygame.Rect(350,220,300,60)
        self.difficulty_button = pygame.Rect(350,300,300,60)
        self.records_button = pygame.Rect(350,380,300,60)
        self.exit_button = pygame.Rect(350,460,300,60)

    def draw_button(self, screen, rect, text, color):

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=15
        )

        label = self.button_font.render(
            text,
            True,
            WHITE
        )

        screen.blit(
            label,
            (
                rect.centerx-label.get_width()//2,
                rect.centery-label.get_height()//2
            )
        )

    def draw(self, screen, high_score):

        title = self.title_font.render(
            "CANDY CLICKOMANIA DELUXE",
            True,
            (255,220,50)
        )

        screen.blit(
            title,
            (
                WIDTH//2-title.get_width()//2,
                100
            )
        )

        self.draw_button(
            screen,
            self.start_button,
            "START",
            (70,120,255)
        )

        self.draw_button(
            screen,
            self.difficulty_button,
            "DIFFICULTY",
            (255,180,50)
        )

        self.draw_button(
            screen,
            self.records_button,
            "PLAYER RECORDS",
            (120,80,220)
        )

        self.draw_button(
            screen,
            self.exit_button,
            "EXIT",
            (255,80,80)
        )

        text = self.button_font.render(
            f"High Score : {high_score}",
            True,
            WHITE
        )

        screen.blit(text,(370,560))