import math
import random

import pygame


class MagicPortalEffect:
    """
    A full-screen "AI is conjuring your result" overlay.

    Usage:
        fx = MagicPortalEffect(duration_ms=3000)
        fx.activate(screen)          # call once, right when the wand is clicked
        ...
        fx.draw(screen)              # call every frame while fx.active is True
        if fx.is_finished():
            <apply the real result here>
            fx.deactivate()
    """

    def __init__(self, duration_ms=3000):
        self.duration = duration_ms

        self.active = False
        self.start_time = 0

        self.blurred_bg = None

        self.stars = []
        self.particles = []
        self.trails = []
        self.shooting_stars = []

        # Rotating captions shown while the portal is open, cycled evenly
        # across the animation's duration. Picked per-activation based on
        # which rescue case triggered the wand (see `mode` in activate()).
        self._caption_sets = {
            "rescue": [
                "Casting Magic...",
                "Finding a Solution...",
                "One Last Chance!",
            ],
            "reshape": [
                "Casting Magic...",
                "Reshaping the Colors...",
                "One Last Chance!",
            ],
        }
        self.captions = self._caption_sets["rescue"]

        self._caption_font = pygame.font.SysFont("arial", 44, bold=True)

    # -----------------------------------------------------
    # LIFECYCLE
    # -----------------------------------------------------

    def activate(self, screen, mode="rescue"):
        """Snapshot + blur the current frame and (re)seed the animation.

        mode: "rescue" (one candy left) or "reshape" (two candies being
        recolored to match) - selects which captions are shown.
        """

        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.captions = self._caption_sets.get(mode, self._caption_sets["rescue"])

        w, h = screen.get_size()

        # Cheap gaussian-ish blur: shrink the frame way down, then scale it
        # back up. smoothscale's bilinear filtering does the rest.
        snapshot = screen.copy()
        small = pygame.transform.smoothscale(
            snapshot, (max(1, w // 20), max(1, h // 20))
        )
        self.blurred_bg = pygame.transform.smoothscale(small, (w, h))

        max_reach = max(w, h) * 0.6

        # Slow-drifting background stars
        self.stars = [
            {
                "angle": random.uniform(0, math.tau),
                "dist": random.uniform(30, max_reach),
                "drift": random.uniform(6, 22),
                "size": random.uniform(1.5, 3.5),
                "phase": random.uniform(0, math.tau),
            }
            for _ in range(70)
        ]

        # Glowing particles that spiral inward toward the portal core
        palette = [
            (255, 225, 140),
            (190, 140, 255),
            (140, 210, 255),
            (255, 150, 230),
            (255, 255, 255),
        ]
        self.particles = [
            {
                "angle": random.uniform(0, math.tau),
                "base_dist": random.uniform(90, max_reach),
                "spin": random.uniform(0.6, 2.2) * random.choice([-1, 1]),
                "size": random.uniform(2, 5),
                "color": random.choice(palette),
                "twinkle": random.uniform(0, math.tau),
            }
            for _ in range(80)
        ]

        # Shimmering spiral light trails
        self.trails = [
            {
                "offset": (math.tau / 5) * i,
                "spin": 1.4 if i % 2 == 0 else -1.4,
                "color": random.choice(
                    [(255, 255, 255), (255, 210, 255), (200, 230, 255), (230, 200, 255)]
                ),
            }
            for i in range(5)
        ]

        # Quick shooting stars that streak across the screen at staggered
        # moments throughout the animation
        self.shooting_stars = []
        for _ in range(9):
            edge_angle = random.uniform(0, math.tau)
            start_dist = max(w, h) * 0.65
            start_x = w / 2 + math.cos(edge_angle) * start_dist
            start_y = h / 2 + math.sin(edge_angle) * start_dist * 0.6
            # Aim roughly back across/through the screen, not dead-on center,
            # so it reads as a streaking star rather than a laser to a point
            aim_angle = edge_angle + math.pi + random.uniform(-0.5, 0.5)

            self.shooting_stars.append(
                {
                    "spawn": random.uniform(0, self.duration * 0.75),
                    "life": random.uniform(280, 480),
                    "start": (start_x, start_y),
                    "angle": aim_angle,
                    "speed": random.uniform(900, 1500),
                    "length": random.uniform(70, 140),
                    "color": random.choice(
                        [(255, 255, 255), (255, 240, 200), (210, 220, 255)]
                    ),
                }
            )

    def deactivate(self):
        self.active = False
        self.blurred_bg = None

    # -----------------------------------------------------
    # TIMING
    # -----------------------------------------------------

    def elapsed(self):
        if not self.active:
            return 0
        return pygame.time.get_ticks() - self.start_time

    def progress(self):
        if self.duration <= 0:
            return 1.0
        return max(0.0, min(1.0, self.elapsed() / self.duration))

    def is_finished(self):
        return self.active and self.elapsed() >= self.duration

    # -----------------------------------------------------
    # DRAWING
    # -----------------------------------------------------

    def draw(self, screen):
        if not self.active:
            return

        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        t = self.elapsed() / 1000.0
        p = self.progress()

        # Smooth in/out envelope: fade in over the first ~12%, fade out
        # over the last ~15%, full strength in between.
        fade_in = min(1.0, p / 0.12)
        fade_out = min(1.0, (1.0 - p) / 0.15)
        fade = max(0.0, min(fade_in, fade_out))

        # 1) Blurred, dimmed backdrop so the portal reads as the focus
        if self.blurred_bg is not None:
            screen.blit(self.blurred_bg, (0, 0))

        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((12, 0, 28, int(150 * (0.4 + 0.6 * fade))))
        screen.blit(dim, (0, 0))

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)

        # 2) Floating stars, gently twinkling and drifting outward
        for s in self.stars:
            dist = s["dist"] + t * s["drift"]
            x = cx + math.cos(s["angle"]) * dist
            y = cy + math.sin(s["angle"]) * dist * 0.55
            twinkle = 0.5 + 0.5 * math.sin(t * 4 + s["phase"])
            alpha = int(200 * twinkle)
            pygame.draw.circle(
                overlay, (255, 255, 255, alpha), (int(x), int(y)), max(1, int(s["size"]))
            )

        # 3) Shimmering spiral light trails swirling around the portal
        for trail in self.trails:
            points = []
            steps = 36
            for i in range(steps):
                f = i / steps
                ang = trail["offset"] + f * math.tau * 1.4 + t * trail["spin"]
                r = (1.0 - f) * min(w, h) * 0.4 * (0.35 + 0.65 * p)
                points.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))

            if len(points) > 1:
                col = trail["color"]
                shimmer = int(150 * (0.5 + 0.5 * math.sin(t * 3 + trail["offset"])))
                pygame.draw.lines(overlay, (*col, max(25, shimmer)), False, points, 2)

        # 4) Quick shooting stars streaking across the screen
        elapsed_ms = self.elapsed()
        for star in self.shooting_stars:
            local_t = elapsed_ms - star["spawn"]
            if local_t < 0 or local_t > star["life"]:
                continue

            life_frac = local_t / star["life"]
            travel = local_t / 1000.0 * star["speed"]
            head_x = star["start"][0] + math.cos(star["angle"]) * travel
            head_y = star["start"][1] + math.sin(star["angle"]) * travel
            tail_x = head_x - math.cos(star["angle"]) * star["length"]
            tail_y = head_y - math.sin(star["angle"]) * star["length"]

            # Fade in fast, fade out toward the end of its short life
            star_alpha = int(255 * min(1.0, life_frac * 4) * min(1.0, (1.0 - life_frac) * 2.5))
            if star_alpha > 0:
                col = star["color"]
                pygame.draw.line(
                    overlay, (*col, star_alpha), (tail_x, tail_y), (head_x, head_y), 2
                )
                pygame.draw.circle(
                    overlay, (*col, star_alpha), (int(head_x), int(head_y)), 3
                )

        # 5) Glowing particles pulled inward toward the portal core
        pull = min(1.0, p * 1.3)
        for particle in self.particles:
            dist = particle["base_dist"] * (1.0 - pull) + 12 * pull
            ang = particle["angle"] + t * particle["spin"]
            x = cx + math.cos(ang) * dist
            y = cy + math.sin(ang) * dist

            glow_col = particle["color"]
            radius = particle["size"] + 1.5 * math.sin(t * 6 + particle["twinkle"])

            for layer, (mult, alpha) in enumerate(((2.4, 35), (1.5, 65), (1.0, 140))):
                pygame.draw.circle(
                    overlay,
                    (*glow_col, alpha),
                    (int(x), int(y)),
                    max(1, int(radius * mult)),
                )

        # 6) Pulsing portal ring at the very center
        ring_radius = 34 + 20 * math.sin(t * 5) + p * 26
        ring_alpha = int(210 * (0.6 + 0.4 * math.sin(t * 6)))
        for i in range(4):
            pygame.draw.circle(
                overlay,
                (205, 165, 255, max(0, ring_alpha - i * 45)),
                (cx, cy),
                max(1, int(ring_radius + i * 9)),
                width=3,
            )

        overlay.set_alpha(int(255 * max(0.12, fade)))
        screen.blit(overlay, (0, 0))

        # 7) Animated, pulsing center caption that cycles through phrases
        phrase_count = len(self.captions)
        phrase_index = min(phrase_count - 1, int(p * phrase_count))
        caption_text = self.captions[phrase_index]

        base_label = self._caption_font.render(caption_text, True, (255, 255, 255))

        pulse = 1.0 + 0.06 * math.sin(t * 5.5)
        scaled_size = (
            max(1, int(base_label.get_width() * pulse)),
            max(1, int(base_label.get_height() * pulse)),
        )
        label = pygame.transform.smoothscale(base_label, scaled_size)
        label.set_alpha(int(255 * max(0.2, fade)))

        label_rect = label.get_rect(center=(cx, cy + int(min(w, h) * 0.3)))
        screen.blit(label, label_rect)
