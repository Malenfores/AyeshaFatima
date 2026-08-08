import pygame
import random

from settings import *

from board import Board
from score import ScoreManager
from particles import ParticleSystem
from animations import AnimationManager
from sound_manager import SoundManager


class Game:

    def __init__(self, difficulty):

        self.difficulty = difficulty

        self.board = Board(
            difficulty.get_colors()
        )

        self.score_manager = ScoreManager()

        self.particles = ParticleSystem()

        self.animations = AnimationManager()

        self.sound_manager = SoundManager()

        # Background Music
        try:
            self.sound_manager.play_background()
        except:
            pass

        self.start_time = pygame.time.get_ticks()

        self.paused = False

        self.pause_start = 0

        self.total_paused_time = 0

        self.game_over = False

        self.win = False

        self.hint_group = []
        self.wand_message_timer=0
        self.ended_by_wand = False

        # Magic Wand portal animation state: the wand's real effect is
        # computed immediately but only *applied* once the full-screen
        # portal animation (driven from main.py) finishes playing.
        self.wand_active = False
        self.wand_start_time = 0
        self._wand_result = None
        self._wand_mode = None  # "rescue" (1 ball) or "reshape" (2 balls)

        # True once the wand has set up a guaranteed win: either exactly
        # one candy is left, or exactly two candies now share a color.
        # lets handle_click() treat those candies as poppable together
        # even if the normal adjacency/match rules wouldn't allow it.
        self.wand_assist_active = False
        self._wand_rescue_positions = []

        # Availability notification + attention-glow state: fires once
        # when the board flips from "has moves" to "stuck & recoverable",
        # and keeps the button glowing until the wand is actually used.
        self.wand_was_available = False
        self.wand_notify_until = 0
        self.wand_notify_text = ""
        self.wand_glow_since = 0
        self.WAND_NOTIFY_DURATION = 2800
        self.WAND_NOTIFY_MESSAGES = [
            "No more moves available!",
            "You're stuck! Magic Wand is now available.",
            "Use the Magic Wand to continue your adventure!",
            "A magical solution has appeared!",
        ]

    def reset(self):

        self.board = Board(
            self.difficulty.get_colors()
        )

        self.score_manager.reset_game()

        self.start_time = pygame.time.get_ticks()

        self.paused = False

        self.pause_start = 0

        self.total_paused_time = 0

        self.game_over = False

        self.win = False

        self.ended_by_wand = False

        self.wand_active = False
        self.wand_assist_active = False
        self._wand_result = None
        self._wand_mode = None
        self._wand_rescue_positions = []

        self.wand_was_available = False
        self.wand_notify_until = 0
        self.wand_notify_text = ""
        self.wand_glow_since = 0

        self.hint_group.clear()

        try:
            self.sound_manager.play_background()
        except:
            pass

    # =====================================
    # TIMER
    # =====================================

    def get_time_left(self):

        current = pygame.time.get_ticks()

        elapsed = (

            current

            - self.start_time

            - self.total_paused_time

        ) // 1000

        remaining = self.difficulty.get_time() - elapsed

        if remaining <= 0:

            remaining = 0

            self.score_manager.save_high_score()

            self.game_over = True

        return remaining
        # =====================================
    # HANDLE CLICK
    # =====================================

    def handle_click(self, row, col):

        if self.paused:
            return

        if self.game_over:
            return

        if self.win:
            return

        group = self.board.get_group(row, col)

        # Magic Wand rescue: once the wand has set up a guaranteed win
        # (either one lone candy, or two candies it just recolored to
        # match), let the player pop those specific candies together even
        # if the board's normal adjacency/match rules wouldn't allow it.
        is_wand_rescue_pop = (
            self.wand_assist_active
            and self.board.grid[row][col] is not None
            and (row, col) in self._wand_rescue_positions
        )

        if is_wand_rescue_pop:
            # Clear the full rescue set together, regardless of whether
            # they happen to be adjacent on the board
            group = set(self._wand_rescue_positions)

        # Invalid move
        if len(group) < 2 and not is_wand_rescue_pop:

            self.score_manager.reset_combo()

            try:
                self.sound_manager.play_click()
            except:
                pass

            return

        if is_wand_rescue_pop:
            self.wand_assist_active = False
            self._wand_rescue_positions = []

        # ==========================
        # Score
        # ==========================

        points = self.score_manager.add_score(

            len(group),

            self.difficulty.get_multiplier()

        )

        # ==========================
        # Bubble Pop Sound
        # ==========================

        try:

            self.sound_manager.play_pop()

        except:

            pass

        # ==========================
        # Effects
        # ==========================

        for r, c in group:

            x = BOARD_X + c * CELL_SIZE + CELL_SIZE // 2

            y = BOARD_Y + r * CELL_SIZE + CELL_SIZE // 2

            try:

                self.animations.add_shrink_effect(

                    x,

                    y,

                    (255,255,255)

                )

            except:

                pass

            try:

                self.particles.create_explosion(

                    x,

                    y,

                    (255,255,0)

                )

            except:

                pass

            try:

                self.particles.create_score_text(

                    x,

                    y,

                    points

                )

            except:

                pass

        # ==========================
        # Remove Candies
        # ==========================

        self.board.remove_group(group, force=is_wand_rescue_pop)

        # ==========================
        # Nice Pop Celebration (big matches)
        # ==========================

        if len(group) >= NICE_POP_SIZE:

            avg_x = sum(
                BOARD_X + c * CELL_SIZE + CELL_SIZE // 2
                for r, c in group
            ) // len(group)

            avg_y = sum(
                BOARD_Y + r * CELL_SIZE + CELL_SIZE // 2
                for r, c in group
            ) // len(group)

            if len(group) >= AWESOME_POP_SIZE:
                label = "AWESOME!"
                burst_color = (255, 215, 0)
            else:
                label = "NICE!"
                burst_color = (0, 220, 255)

            try:
                self.animations.add_ring_burst(avg_x, avg_y, burst_color)
            except:
                pass

            try:
                self.particles.create_nice_text(avg_x, avg_y, label, burst_color)
            except:
                pass

            try:
                self.sound_manager.play_nice()
            except:
                pass

        # Clear Hint

        self.hint_group.clear()

        # ==========================
        # Win Check
        # ==========================

        self.check_win()

        # ==========================
        # No Moves Left
        # ==========================

        if not self.win:

            if not self.board.has_moves():

                # Shuffle automatically if candies remain

                if self.board.count_remaining() > 0:

                    self.board.shuffle()

                else:

                    # All candies removed: this is a win condition
                    self.check_win()
        # =====================================
    # CHECK WIN
    # =====================================

    def check_win(self):

        # Board completely clear
        if self.board.count_remaining() == 0:

            self.win = True

            # Bonus score
            self.score_manager.score += 1000

            self.score_manager.save_high_score()

            try:
                self.sound_manager.play_win()
            except:
                pass

    # =====================================
    # UPDATE
    # =====================================

    def update(self):

        if self.paused:
            return

        if self.game_over:
            return

        if self.win:
            return

        self.board.update()

        self.animations.update()

        self.particles.update()

        self.get_time_left()

        self._update_wand_notification()

    # =====================================
    # DRAW
    # =====================================

    def draw(self, screen):

        self.board.draw(screen)

        self.animations.draw(screen)

        self.particles.draw(screen)

    # =====================================
    # PAUSE / RESUME
    # =====================================

    def toggle_pause(self):

        if not self.paused:

            self.pause_start = pygame.time.get_ticks()

            self.paused = True

            try:
                pygame.mixer.music.pause()
            except:
                pass

        else:

            self.total_paused_time += (

                pygame.time.get_ticks()

                - self.pause_start

            )

            self.paused = False

            try:
                pygame.mixer.music.unpause()
            except:
                pass
        # =====================================
    # SHUFFLE BOARD
    # =====================================

    def shuffle_board(self):

        self.board.shuffle()

        self.hint_group.clear()

        try:
            self.sound_manager.play_shuffle()
        except:
            pass

    # =====================================
    # FIND HINT
    # =====================================

    def find_hint(self):

        self.hint_group.clear()

        for row in range(ROWS):

            for col in range(COLS):

                group = self.board.get_group(row, col)

                if len(group) >= 2:

                    self.hint_group = list(group)

                    return self.hint_group

        return []

    # =====================================
    # GET HINT
    # =====================================

    def get_hint(self):

        return self.hint_group

    # =====================================
    # GETTERS
    # =====================================

    def get_score(self):

        return self.score_manager.get_score()

    def get_high_score(self):

        return self.score_manager.get_high_score()

    def get_combo(self):

        return self.score_manager.get_combo()

    def get_chain(self):

        return self.score_manager.get_chain()

    def is_game_over(self):

        return self.game_over

    def is_win(self):

        return self.win

    def is_paused(self):

        return self.paused

    # =====================================
    # SAVE SCORE
    # =====================================

    def save_score(self):

        self.score_manager.save_high_score()

    def remaining_balls(self):
        return sum(1 for row in self.board.grid for c in row if c is not None)

    def _stuck_and_recoverable(self):
        """Pure check: is the board in a no-valid-moves state the wand
        knows how to guarantee a win from? (1 candy left, or 2 candies of
        different colors). Doesn't consider whether the wand is currently
        mid-animation - see can_use_wand() for that."""

        if self.board.has_moves():
            return False

        positions = [
            (r, c)
            for r, row in enumerate(self.board.grid)
            for c, v in enumerate(row)
            if v is not None
        ]

        if len(positions) == 1:
            return True

        if len(positions) == 2:
            (r0, c0), (r1, c1) = positions
            return self.board.grid[r0][c0].color != self.board.grid[r1][c1].color

        return False

    def can_use_wand(self):
        """Magic Wand is a stuck-state recovery tool, not an anytime power.
        It's only usable once the player has no valid moves left and the
        board has been whittled down to a case it can guarantee a win from:
        exactly one candy, or exactly two candies of different colors."""

        if self.wand_active:
            return False

        return self._stuck_and_recoverable()

    def _update_wand_notification(self):
        """Detects the moment the board becomes stuck-and-recoverable and
        fires a one-time popup + starts the button's attention glow. Both
        naturally clear themselves once the state is no longer true (the
        wand was used, or the board changed some other way)."""

        stuck = self._stuck_and_recoverable()

        if stuck and not self.wand_was_available and not self.wand_active:
            self.wand_notify_until = pygame.time.get_ticks() + self.WAND_NOTIFY_DURATION
            self.wand_notify_text = random.choice(self.WAND_NOTIFY_MESSAGES)
            self.wand_glow_since = pygame.time.get_ticks()

        if not stuck:
            self.wand_glow_since = 0

        self.wand_was_available = stuck

    def wand_glow_elapsed(self):
        """Milliseconds since the wand button became available (0 if it
        currently isn't) - drives the button's pulse/bounce animation."""

        if not self.wand_glow_since:
            return 0

        return pygame.time.get_ticks() - self.wand_glow_since

    def get_wand_notification(self):
        """Returns {"text", "elapsed", "duration"} while the one-time
        availability popup should still be showing, else None."""

        now = pygame.time.get_ticks()

        if self.wand_notify_until <= 0 or now >= self.wand_notify_until:
            return None

        return {
            "text": self.wand_notify_text,
            "elapsed": self.WAND_NOTIFY_DURATION - (self.wand_notify_until - now),
            "duration": self.WAND_NOTIFY_DURATION,
        }

    def wand_mode(self):
        """'rescue' for the one-candy case, 'reshape' for the two-candy
        case - lets main.py pick a matching caption for the portal effect."""
        return self._wand_mode

    def use_magic_wand(self):
        # Ignore repeat clicks while the portal animation is already playing,
        # and refuse to activate outside the situations it's meant for
        if not self.can_use_wand():
            return

        positions = [
            (r, c)
            for r, row in enumerate(self.board.grid)
            for c, v in enumerate(row)
            if v is not None
        ]

        # Play the activation sound right away so the click feels instant...
        try:
            self.sound_manager.play_wand()
        except:
            pass

        # ...but hold the actual board change until the full-screen portal
        # animation finishes, so the result feels "conjured" rather than
        # applied instantly. main.py plays that animation and then calls
        # finish_wand() once it's done.
        if len(positions) == 1:
            self._wand_mode = "rescue"
            self._wand_result = ("reveal", positions[0])
        else:
            self._wand_mode = "reshape"
            (r0, c0), (r1, c1) = positions
            target_color = self.board.grid[r0][c0].color
            self._wand_result = ("reshape", ((r0, c0), (r1, c1), target_color))

        self.wand_active = True
        self.wand_start_time = pygame.time.get_ticks()

    def is_wand_active(self):
        return self.wand_active

    def finish_wand(self):
        """Apply the Magic Wand's real effect. Call this once the portal
        animation (see portal_effect.MagicPortalEffect) has finished.

        This never ends the game by itself - it only ever leaves the board
        in a state the player can win from with one more click."""

        if not self.wand_active:
            return

        result = self._wand_result
        self._wand_result = None
        self.wand_active = False

        # Show the "MAGIC WAND ACTIVATED!" message once the result is revealed
        self.wand_message_timer = pygame.time.get_ticks() + 2000

        if result is None:
            return

        kind, payload = result

        if kind == "reveal":
            # Exactly one candy remains - nothing needs to change on the
            # board, the player just gets to pop it themselves for the win.
            self.wand_assist_active = True
            self._wand_rescue_positions = [payload]

        elif kind == "reshape":
            (r0, c0), (r1, c1), target_color = payload

            # Recolor the second candy so both visibly match, then let the
            # player clear them together on their next click
            candy = self.board.grid[r1][c1]
            if candy is not None:
                candy.color = target_color

            self.wand_assist_active = True
            self._wand_rescue_positions = [(r0, c0), (r1, c1)]

