import pygame
import random


class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-5, -1)

        self.radius = random.randint(3, 6)

        self.life = 35

        self.color = color

    def update(self):

        self.x += self.dx
        self.y += self.dy

        self.dy += 0.15

        self.life -= 1

    def draw(self, screen):

        if self.life > 0:

            pygame.draw.circle(

                screen,

                self.color,

                (int(self.x), int(self.y)),

                self.radius

            )


class ScoreText:

    def __init__(self, x, y, points):

        self.x = x
        self.y = y

        self.points = points

        self.life = 60

        self.font = pygame.font.SysFont(
            "arial",
            24,
            bold=True
        )

    def update(self):

        self.y -= 1

        self.life -= 1

    def draw(self, screen):

        if self.life > 0:

            text = self.font.render(

                f"+{self.points}",

                True,

                (255, 255, 0)

            )

            screen.blit(
                text,
                (self.x, self.y)
            )


class NiceText:

    def __init__(self, x, y, text, color):

        self.x = x
        self.y = y

        self.text = text
        self.color = color

        self.life = 45

        self.max_life = 45

        self.font = pygame.font.SysFont(
            "arial",
            40,
            bold=True
        )

    def update(self):

        self.y -= 1.4

        self.life -= 1

    def draw(self, screen):

        if self.life > 0:

            # Pop-in scale effect for the first few frames
            progress = 1 - (self.life / self.max_life)
            scale = 1.0 + max(0, (0.3 - progress)) if progress < 0.3 else 1.0

            img = self.font.render(self.text, True, self.color)

            if scale != 1.0:
                w = max(1, int(img.get_width() * scale))
                h = max(1, int(img.get_height() * scale))
                img = pygame.transform.smoothscale(img, (w, h))

            rect = img.get_rect(center=(int(self.x), int(self.y)))

            screen.blit(img, rect)


class ParticleSystem:

    def __init__(self):

        self.particles = []

        self.score_texts = []

        self.nice_texts = []

    # =============================

    def update(self):

        for particle in self.particles[:]:

            particle.update()

            if particle.life <= 0:

                self.particles.remove(particle)

        for text in self.score_texts[:]:

            text.update()

            if text.life <= 0:

                self.score_texts.remove(text)

        for text in self.nice_texts[:]:

            text.update()

            if text.life <= 0:

                self.nice_texts.remove(text)

    # =============================

    def draw(self, screen):

        for particle in self.particles:

            particle.draw(screen)

        for text in self.score_texts:

            text.draw(screen)

        for text in self.nice_texts:

            text.draw(screen)

    # =============================

    def create_explosion(self, x, y, color):

        for _ in range(15):

            self.particles.append(

                Particle(
                    x,
                    y,
                    color
                )

            )

    # =============================

    def create_score_text(
            self,
            x,
            y,
            points
    ):

        self.score_texts.append(

            ScoreText(
                x,
                y,
                points
            )

        )

    # =============================

    def create_nice_text(
            self,
            x,
            y,
            text,
            color
    ):

        self.nice_texts.append(

            NiceText(
                x,
                y,
                text,
                color
            )

        )