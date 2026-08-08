import pygame
from settings import *


class DifficultyManager:

    def __init__(self):

        self.current = "Easy"

        # ==============================
        # Difficulty Modes
        # ==============================

        self.modes = {

            "Easy": {
                "colors": 5,
                "time": 130,
                "multiplier": 1.0
            },

            "Medium": {
                "colors": 6,
                "time": 105,
                "multiplier": 1.5
            },

            "Hard": {
                "colors": 7,
                "time": 85,
                "multiplier": 2.0
            }

        }

        self.font = pygame.font.SysFont(
            "arial",
            35,
            bold=True
        )

        self.easy_button = pygame.Rect(350,220,300,60)
        self.medium_button = pygame.Rect(350,320,300,60)
        self.hard_button = pygame.Rect(350,420,300,60)
        self.back_button = pygame.Rect(350,520,300,60)

    # ===================================
    # Set Difficulty
    # ===================================

    def set_mode(self, mode):

        if mode in self.modes:
            self.current = mode

    # ===================================
    # Getters
    # ===================================

    def get_colors(self):
        return self.modes[self.current]["colors"]

    def get_time(self):
        return self.modes[self.current]["time"]

    def get_multiplier(self):
        return self.modes[self.current]["multiplier"]

    def get_mode(self):
        return self.current

    # ===================================
    # Draw Menu
    # ===================================

    def draw(self, screen):

        title = self.font.render(
            "SELECT DIFFICULTY",
            True,
            WHITE
        )

        screen.blit(title, (300,100))

        pygame.draw.rect(screen, (80,220,120), self.easy_button, border_radius=12)
        pygame.draw.rect(screen, (255,180,50), self.medium_button, border_radius=12)
        pygame.draw.rect(screen, (255,80,80), self.hard_button, border_radius=12)
        pygame.draw.rect(screen, (70,120,255), self.back_button, border_radius=12)

        screen.blit(self.font.render("EASY",True,WHITE),(460,235))
        screen.blit(self.font.render("MEDIUM",True,WHITE),(425,335))
        screen.blit(self.font.render("HARD",True,WHITE),(455,435))
        screen.blit(self.font.render("BACK",True,WHITE),(455,535))