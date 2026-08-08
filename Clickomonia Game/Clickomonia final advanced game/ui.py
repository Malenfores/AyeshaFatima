import pygame
import math
from settings import WIDTH, HEIGHT, WHITE


class UI:

    def __init__(self):

        # ==========================
        # Fonts
        # ==========================
        self.title_font = pygame.font.SysFont(
            "arial",
            60,
            bold=True
        )

        self.font = pygame.font.SysFont(
            "arial",
            30
        )

        self.small_font = pygame.font.SysFont(
            "arial",
            22
        )

        # ==========================
        # Right Side Buttons
        # ==========================

        button_x = WIDTH - 220

        self.pause_button = pygame.Rect(
            button_x, 140, 180, 50
        )

        self.shuffle_button = pygame.Rect(
            button_x, 210, 180, 50
        )

        self.hint_button = pygame.Rect(
            button_x, 280, 180, 50
        )

        self.quit_button = pygame.Rect(
            button_x, 350, 180, 50
        )

        self.wand_button = pygame.Rect(
            button_x, 420, 180, 50
        )

        self.mute_button = pygame.Rect(
            button_x, 490, 180, 50
        )

        self.restart_button = pygame.Rect(
            button_x, 560, 180, 50
        )

        self.theme_button = pygame.Rect(
            button_x, 630, 180, 50
        )

        # ==========================
        # Resume Button
        # ==========================

        self.resume_button = pygame.Rect(
            WIDTH // 2 - 100,
            330,
            200,
            60
        )
            # =====================================
    # BUTTON
    # =====================================

    def draw_button(
            self,
            screen,
            rect,
            text,
            color
    ):

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            WHITE,
            rect,
            2,
            border_radius=12
        )

        label = self.font.render(
            text,
            True,
            WHITE
        )

        screen.blit(
            label,
            (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            )
        )

    # =====================================
    # MAGIC WAND BUTTON (glow / pulse / sparkle)
    # =====================================

    def _draw_sparkle(self, surface, cx, cy, size, color):

        pts = [
            (cx, cy - size),
            (cx + size * 0.28, cy - size * 0.28),
            (cx + size, cy),
            (cx + size * 0.28, cy + size * 0.28),
            (cx, cy + size),
            (cx - size * 0.28, cy + size * 0.28),
            (cx - size, cy),
            (cx - size * 0.28, cy - size * 0.28),
        ]

        pygame.draw.polygon(surface, color, pts)

    def draw_wand_button(self, screen, enabled, glow_elapsed_ms):

        rect = self.wand_button

        if not enabled:
            self.draw_button(screen, rect, "Locked", (80, 65, 80))
            return

        t = glow_elapsed_ms / 1000.0

        # Quick attention bounce during the first ~0.6s after unlocking,
        # settling into a steady rest position after that
        bounce_offset = 0
        if glow_elapsed_ms < 600:
            progress = glow_elapsed_ms / 600.0
            bounce_offset = int(-10 * math.sin(progress * math.pi) * (1 - progress))

        draw_rect = rect.move(0, bounce_offset)

        # Pulsing glow behind the button
        pad = 40
        glow_surf = pygame.Surface(
            (rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA
        )
        pulse = 0.5 + 0.5 * math.sin(t * 4)

        for expand, alpha in ((36, 25), (24, 45), (12, 70)):
            a = int(alpha * (0.5 + 0.5 * pulse))
            pygame.draw.rect(
                glow_surf,
                (255, 120, 230, a),
                (
                    pad - expand,
                    pad - expand,
                    rect.width + expand * 2,
                    rect.height + expand * 2,
                ),
                border_radius=18,
            )

        screen.blit(glow_surf, (draw_rect.x - pad, draw_rect.y - pad))

        # Small sparkles orbiting the button to catch the eye
        cx, cy = draw_rect.center
        for i in range(6):
            ang = t * 2.2 + i * (math.tau / 6)
            sx = cx + math.cos(ang) * draw_rect.width * 0.62
            sy = cy + math.sin(ang) * draw_rect.height * 0.9
            twinkle = 0.5 + 0.5 * math.sin(t * 6 + i)
            self._draw_sparkle(screen, sx, sy, 3 + 3 * twinkle, (255, 255, 255))

        # The button itself, its color gently pulsing pink <-> gold
        shift = int(60 * pulse)
        color = (255, 100 + shift, 220 - shift)

        self.draw_button(screen, draw_rect, "Magic Wand", color)

    # =====================================
    # MAGIC WAND AVAILABILITY POPUP
    # =====================================

    def draw_wand_notification(self, screen, text, elapsed_ms, duration_ms):

        fade_in = min(1.0, elapsed_ms / 250.0)
        fade_out = min(1.0, max(0.0, duration_ms - elapsed_ms) / 400.0)
        fade = max(0.0, min(fade_in, fade_out))

        if fade <= 0:
            return

        box_w, box_h = 620, 90
        box_x = WIDTH // 2 - box_w // 2
        box_y = 110
        bob = int(4 * math.sin(elapsed_ms / 260.0))

        card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)

        pygame.draw.rect(
            card, (40, 10, 60, int(225 * fade)), (0, 0, box_w, box_h), border_radius=20
        )
        pygame.draw.rect(
            card,
            (255, 140, 230, int(255 * fade)),
            (0, 0, box_w, box_h),
            width=3,
            border_radius=20,
        )

        for i, side in enumerate((1, -1)):
            self._draw_sparkle(
                card,
                34 if side == 1 else box_w - 34,
                box_h // 2,
                10,
                (255, 225, 130, int(255 * fade)),
            )

        label = self.font.render(text, True, (255, 255, 255))
        label.set_alpha(int(255 * fade))
        card.blit(
            label,
            (box_w // 2 - label.get_width() // 2, box_h // 2 - label.get_height() // 2),
        )

        screen.blit(card, (box_x, box_y + bob))

    # =====================================
    # HUD
    # =====================================

    def draw_hud(
            self,
            screen,
            score,
            high_score,
            difficulty,
            time_left,
            wand_enabled=True,
            wand_glow_elapsed=0
    ):

        # -----------------------------
        # SCORE (Top Left)
        # -----------------------------
        score_text = self.font.render(
            f"Score : {score}",
            True,
            WHITE
        )
        screen.blit(score_text, (30, 20))

        # -----------------------------
        # HIGH SCORE (Center)
        # -----------------------------
        high_text = self.font.render(
            f"High Score : {high_score}",
            True,
            (255, 255, 0)
        )

        high_rect = high_text.get_rect(
            center=(WIDTH // 2, 35)
        )

        screen.blit(high_text, high_rect)

        # -----------------------------
        # TIMER (Top Right)
        # -----------------------------
        color = (80, 255, 120)

        if time_left <= 20:
            color = (255, 80, 80)

        time_text = self.font.render(
            f"Time : {time_left}",
            True,
            color
        )

        time_rect = time_text.get_rect(
            topright=(WIDTH - 30, 20)
        )

        screen.blit(time_text, time_rect)

        # -----------------------------
        # MODE (Below Timer)
        # -----------------------------
        mode_text = self.small_font.render(
            f"Mode : {difficulty}",
            True,
            WHITE
        )

        mode_rect = mode_text.get_rect(
            topright=(WIDTH - 30, 60)
        )

        screen.blit(mode_text, mode_rect)

        # -----------------------------
        # BUTTONS
        # -----------------------------
        self.draw_button(
            screen,
            self.pause_button,
            "Pause",
            (255, 180, 50)
        )

        self.draw_button(
            screen,
            self.shuffle_button,
            "Shuffle",
            (80, 180, 255)
        )

        self.draw_button(
            screen,
            self.hint_button,
            "Hint",
            (80, 220, 120)
        )

        self.draw_button(
            screen,
            self.quit_button,
            "Quit",
            (255, 80, 80)
        )

        self.draw_wand_button(screen, wand_enabled, wand_glow_elapsed)

        self.draw_button(
            screen,
            self.mute_button,
            "Mute",
            (120, 120, 120)
        )

        self.draw_button(
            screen,
            self.restart_button,
            "Restart",
            (180, 120, 255)
        )

        self.draw_button(
            screen,
            self.theme_button,
            "Theme",
            (70, 200, 200)
        )
            # =====================================
    # PAUSE SCREEN
    # =====================================

    def draw_pause_screen(self, screen):

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render(
            "GAME PAUSED",
            True,
            (255, 220, 50)
        )

        title_rect = title.get_rect(center=(WIDTH // 2, 180))
        screen.blit(title, title_rect)

        self.draw_button(
            screen,
            self.resume_button,
            "Resume",
            (80, 220, 120)
        )

    # =====================================
    # GAME OVER SCREEN
    # =====================================

    def draw_game_over(self, screen):

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render(
            "GAME OVER",
            True,
            (255, 80, 80)
        )

        title_rect = title.get_rect(center=(WIDTH // 2, 180))
        screen.blit(title, title_rect)

    # =====================================
    # WIN SCREEN
    # =====================================

    def draw_win_screen(self, screen):

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render(
            "YOU WIN!",
            True,
            (80, 255, 120)
        )

        title_rect = title.get_rect(center=(WIDTH // 2, 180))
        screen.blit(title, title_rect)
        # =====================================
    # MESSAGE
    # =====================================

    def draw_message(self, screen, message):

        if not message:
            return

        # Background Box
        box = pygame.Rect(
            WIDTH // 2 - 260,
            HEIGHT - 85,
            520,
            50
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            box,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            WHITE,
            box,
            2,
            border_radius=10
        )

        # Message Text
        text = self.small_font.render(
            message,
            True,
            WHITE
        )

        text_rect = text.get_rect(center=box.center)

        screen.blit(
            text,
            text_rect
        )