import pygame
import math


class ShrinkAnimation:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        self.color = color

        self.radius = 25

        self.finished = False

    def update(self):

        self.radius -= 2

        if self.radius <= 0:

            self.finished = True

    def draw(self, screen):

        if not self.finished:

            pygame.draw.circle(

                screen,

                self.color,

                (int(self.x), int(self.y)),

                int(self.radius)

            )


class GlowAnimation:

    def __init__(self):

        self.angle = 0

    def update(self):

        self.angle += 0.1

    def get_size_bonus(self):

        return abs(math.sin(self.angle)) * 4


class RingBurstAnimation:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        self.color = color

        self.radius = 10
        self.max_radius = 75

        self.alpha = 255

        self.finished = False

    def update(self):

        self.radius += 4

        self.alpha -= 9

        if self.radius >= self.max_radius or self.alpha <= 0:

            self.finished = True

    def draw(self, screen):

        if self.finished:
            return

        size = self.max_radius * 2 + 20

        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)

        alpha = max(0, min(255, self.alpha))

        ring_color = (
            self.color[0],
            self.color[1],
            self.color[2],
            alpha
        )

        pygame.draw.circle(
            surf,
            ring_color,
            center,
            int(self.radius),
            5
        )

        screen.blit(
            surf,
            (self.x - center[0], self.y - center[1])
        )


class AnimationManager:

    def __init__(self):

        self.shrink_effects = []

        self.ring_bursts = []

        self.glow = GlowAnimation()

    # =====================================

    def add_shrink_effect(self, x, y, color):

        self.shrink_effects.append(

            ShrinkAnimation(
                x,
                y,
                color
            )

        )

    # =====================================
    # NICE POP RING BURST
    # =====================================

    def add_ring_burst(self, x, y, color):

        self.ring_bursts.append(
            RingBurstAnimation(x, y, color)
        )

    # =====================================
    # NEW POP FUNCTION
    # =====================================

    def pop(self, group):

        # group received successfully
        # actual animation is added from game.py
        pass

    # =====================================

    def update(self):

        self.glow.update()

        for effect in self.shrink_effects[:]:

            effect.update()

            if effect.finished:

                self.shrink_effects.remove(effect)

        for effect in self.ring_bursts[:]:

            effect.update()

            if effect.finished:

                self.ring_bursts.remove(effect)

    # =====================================

    def draw(self, screen):

        for effect in self.shrink_effects:

            effect.draw(screen)

        for effect in self.ring_bursts:

            effect.draw(screen)

    # =====================================

    def get_glow_bonus(self):

        return self.glow.get_size_bonus()