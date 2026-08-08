import pygame
import sys
from settings import WIDTH, HEIGHT

class EndScreen:

    def __init__(self, score, high_score):

        self.score = score
        self.high_score = high_score

        self.title_font = pygame.font.SysFont("arial", 72, True)
        self.big_font = pygame.font.SysFont("arial", 40, True)
        self.small_font = pygame.font.SysFont("arial", 28)

        self.play_rect = pygame.Rect(WIDTH//2-120, 470, 240, 60)
        self.menu_rect = pygame.Rect(WIDTH//2-120, 550, 240, 60)

    def draw_button(self, screen, rect, text, mouse):

        color = (220,60,60)

        if rect.collidepoint(mouse):
            color = (255,90,90)

        pygame.draw.rect(screen, color, rect, border_radius=15)
        pygame.draw.rect(screen, (255,255,255), rect, 3, border_radius=15)

        txt = self.small_font.render(text, True, (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))

    def show(self, screen):

        clock = pygame.time.Clock()

        while True:

            mouse = pygame.mouse.get_pos()

            screen.fill((35,20,20))

            title = self.title_font.render("GAME OVER", True, (255,80,80))
            screen.blit(title, title.get_rect(center=(WIDTH//2,120)))

            score = self.big_font.render(f"Score : {self.score}", True, (255,255,255))
            screen.blit(score, score.get_rect(center=(WIDTH//2,250)))

            high = self.big_font.render(f"High Score : {self.high_score}", True, (255,255,255))
            screen.blit(high, high.get_rect(center=(WIDTH//2,320)))

            self.draw_button(screen, self.play_rect, "Play Again", mouse)
            self.draw_button(screen, self.menu_rect, "Continue", mouse)

            pygame.display.flip()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        return "play"

                    if event.key == pygame.K_SPACE:
                        return "menu"

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.play_rect.collidepoint(mouse):
                        return "play"

                    if self.menu_rect.collidepoint(mouse):
                        return "menu"

            clock.tick(60)