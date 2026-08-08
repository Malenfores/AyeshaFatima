"""
================================================================================
 MURDER MYSTERY DETECTIVE - ADVANCED EDITION  (detective_game.py)
================================================================================
Run this file to play. Needs Python 3 + Tkinter (already included with a
normal Python install on Windows/macOS; on Linux: sudo apt-get install
python3-tk). No pip installs are required to PLAY.

Project files (keep them together in one folder):
    detective_game.py     <- run this one
    cases_data.py          <- all 8 cases (story/suspects/clues/solution)
    generate_assets.py     <- optional, regenerates images/sounds (needs Pillow)
    assets/images/*.png    <- backgrounds + suspect portraits (pre-generated)
    assets/sounds/*.wav    <- sound effects + ambient music (pre-generated)

WHAT'S NEW IN THIS VERSION
----------------------------
  - Real background artwork + suspect portraits (assets/images) behind
    every screen, themed per case.
  - Smaller default window (auto-fits your screen, never oversized) and
    fully resizable/maximizable.
  - A looping ambient "murder mystery" background track plays during the
    story + investigation screens, on top of short sound effects for
    clicks / clues / correct / wrong / victory.
  - Per-CASE records: every accusation you make (right or wrong) is
    logged, so you can see your attempt history and success rate for
    each individual case - not just your overall score.
  - Player Records leaderboard (name, score, rank, date) for completed
    playthroughs, same as before.
================================================================================
"""

import datetime
import json
import math
import os
import random
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import font as tkfont

from cases_data import cases

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
SND_DIR = os.path.join(BASE_DIR, "assets", "sounds")
SAVE_FILE = os.path.join(BASE_DIR, "detective_save.json")
RECORDS_FILE = os.path.join(BASE_DIR, "player_records.json")
CASE_RECORDS_FILE = os.path.join(BASE_DIR, "case_records.json")
PROFILE_FILE = os.path.join(BASE_DIR, "detective_profile.json")
ACHIEVEMENTS_FILE = os.path.join(BASE_DIR, "achievements.json")
EVIDENCE_LOG_FILE = os.path.join(BASE_DIR, "evidence_log.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# Difficulty controls how much of a case must be investigated before the
# Accuse button unlocks, and the XP multiplier awarded for solving.
DIFFICULTY_CONFIG = {
    "Easy":   {"clue_fraction": 0.5,  "require_interrogation": False, "xp_mult": 0.75},
    "Medium": {"clue_fraction": 0.75, "require_interrogation": False, "xp_mult": 1.0},
    "Hard":   {"clue_fraction": 1.0,  "require_interrogation": True,  "xp_mult": 1.5},
}

# design resolution the background art was generated at
ART_W, ART_H = 1000, 640

# --------------------------------------------------------------------------
# COLORS
# --------------------------------------------------------------------------
INK = "#0f0d0b"
PANEL = "#1c1712"
PANEL_LIGHT = "#26201a"
GOLD = "#d4af37"
GOLD_BRIGHT = "#e8c85a"
GOLD_DIM = "#8a7327"
TEXT_LIGHT = "#f1ece1"
TEXT_DIM = "#b3a996"
RED = "#a3382f"
RED_BRIGHT = "#c2453a"
GREEN = "#3f8c56"
GREEN_BRIGHT = "#5cab72"
BLUE = "#3d6fa8"
BLUE_BRIGHT = "#5a8fce"


# ==========================================================================
# SOUND MANAGER
#   Tier 1: pygame (if installed)         -> full mixer, music + SFX together
#   Tier 2: Windows without pygame        -> winsound loop for ambient music
#            (SFX skipped on this tier to avoid interrupting the loop -
#             visual feedback / toasts still show for every action)
#   Tier 3: macOS / Linux without pygame  -> afplay/paplay/aplay subprocess,
#            which supports true simultaneous playback (music + SFX)
#   Always safe: any failure is caught and the game simply continues silently.
# ==========================================================================
class SoundManager:
    def __init__(self):
        self.enabled = True
        self.backend = None
        self._pygame_mixer = None
        self._winsound = None
        self._linux_player = None
        self._loop_stop_flag = True
        self._loop_proc = None
        self._ambient_active = False
        self._ambient_file = None
        self.music_volume = 0.6
        self.sfx_volume = 0.8

        try:
            import pygame
            pygame.mixer.init()
            self._pygame_mixer = pygame.mixer
            self.backend = "pygame"
        except Exception:
            if sys.platform.startswith("win"):
                try:
                    import winsound
                    self._winsound = winsound
                    self.backend = "winsound"
                except Exception:
                    self.backend = None
            else:
                player = None
                for candidate in ("paplay", "aplay", "afplay", "ffplay"):
                    if shutil.which(candidate):
                        player = candidate
                        break
                if player:
                    self._linux_player = player
                    self.backend = "subprocess"

    def set_music_volume(self, v):
        self.music_volume = max(0.0, min(1.0, v))
        try:
            if self.backend == "pygame" and self._ambient_active:
                self._pygame_mixer.music.set_volume(0.5 * self.music_volume)
        except Exception:
            pass

    def set_sfx_volume(self, v):
        self.sfx_volume = max(0.0, min(1.0, v))

    def _play_file_once(self, path):
        try:
            if self.backend == "subprocess" and self._linux_player:
                args = [self._linux_player, path]
                if self._linux_player == "ffplay":
                    args = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def play(self, filename):
        """One-shot sound effect (respects the SFX volume slider on pygame)."""
        if not self.enabled or self.sfx_volume <= 0:
            return
        path = os.path.join(SND_DIR, filename)
        if not os.path.exists(path):
            return
        try:
            if self.backend == "pygame":
                snd = self._pygame_mixer.Sound(path)
                snd.set_volume(self.sfx_volume)
                snd.play()
            elif self.backend == "subprocess":
                self._play_file_once(path)
            # winsound tier: intentionally skipped so it never interrupts
            # the looping ambient track (visual toasts cover the feedback)
        except Exception:
            pass

    def start_ambient(self, filename="ambient_murder.mp3"):
        if not self.enabled:
            return
        if self._ambient_active and self._ambient_file == filename:
            return  # already playing this exact track
        if self._ambient_active:
            self.stop_ambient()
        path = os.path.join(SND_DIR, filename)
        if not os.path.exists(path):
            return
        self._ambient_active = True
        self._ambient_file = filename
        try:
            if self.backend == "pygame":
                self._pygame_mixer.music.load(path)
                self._pygame_mixer.music.set_volume(0.5 * self.music_volume)
                self._pygame_mixer.music.play(loops=-1)
            elif self.backend == "winsound":
                self._winsound.PlaySound(
                    path,
                    self._winsound.SND_FILENAME | self._winsound.SND_ASYNC | self._winsound.SND_LOOP,
                )
            elif self.backend == "subprocess":
                self._loop_stop_flag = False

                def loop():
                    while not self._loop_stop_flag and self.enabled:
                        try:
                            args = [self._linux_player, path]
                            if self._linux_player == "ffplay":
                                args = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]
                            self._loop_proc = subprocess.Popen(
                                args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            self._loop_proc.wait()
                        except Exception:
                            break

                threading.Thread(target=loop, daemon=True).start()
        except Exception:
            self._ambient_active = False
            self._ambient_file = None

    def stop_ambient(self):
        self._ambient_active = False
        self._ambient_file = None
        try:
            if self.backend == "pygame":
                self._pygame_mixer.music.stop()
            elif self.backend == "winsound":
                self._winsound.PlaySound(None, self._winsound.SND_PURGE)
            elif self.backend == "subprocess":
                self._loop_stop_flag = True
                if self._loop_proc:
                    self._loop_proc.terminate()
        except Exception:
            pass

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_ambient()
        return self.enabled


# ==========================================================================
# IMAGE CACHE (Tk's PhotoImage reads PNG natively - no Pillow needed to run)
# ==========================================================================
class ImageCache:
    def __init__(self):
        self._cache = {}

    def get(self, filename):
        if filename in self._cache:
            return self._cache[filename]
        path = os.path.join(IMG_DIR, filename)
        try:
            img = tk.PhotoImage(file=path)
        except Exception:
            img = None
        self._cache[filename] = img
        return img


IMAGES = ImageCache()


# ==========================================================================
# MAIN APPLICATION
# ==========================================================================
class DetectiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Murder Mystery Detective - Advanced Edition")
        self.root.configure(bg=INK)

        # ---- smaller, responsive window: fits the art size but never
        #      bigger than what comfortably fits the user's screen
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.width = min(ART_W, max(820, screen_w - 140))
        self.height = min(ART_H, max(560, screen_h - 160))
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.minsize(820, 540)
        self.root.resizable(True, True)

        self.sound = SoundManager()
        settings = self.load_settings()
        self.sound.set_music_volume(settings.get("music_volume", 0.6))
        self.sound.set_sfx_volume(settings.get("sfx_volume", 0.8))
        self.difficulty = settings.get("difficulty", "Medium")

        self._session_start = time.time()
        self._case_start_time = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.f_title = tkfont.Font(family="Helvetica", size=26, weight="bold")
        self.f_h1 = tkfont.Font(family="Helvetica", size=17, weight="bold")
        self.f_h2 = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.f_body = tkfont.Font(family="Helvetica", size=11)
        self.f_body_b = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.f_small = tkfont.Font(family="Helvetica", size=9)
        self.f_button = tkfont.Font(family="Helvetica", size=10, weight="bold")

        self.case_index = 0
        self.score = 0
        self.solved_cases = []
        self.evidence = []
        self.selected_suspect = None
        self.interrogated = set()
        self.max_clues = 0

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg=INK)
        self.canvas.pack(fill="both", expand=True)

        self._widgets = []
        self._bg_ref = None
        self._screen_gen = 0

        profile = self.load_profile()
        if profile is None:
            self.show_profile_creation()
        else:
            self.show_title_screen()

    # ------------------------------------------------------------------
    def clear_screen(self):
        self._screen_gen = getattr(self, "_screen_gen", 0) + 1
        self.canvas.delete("all")
        for w in self._widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._widgets = []

    def add_widget(self, w):
        self._widgets.append(w)
        return w

    def W(self):
        self.root.update_idletasks()
        return max(self.canvas.winfo_width(), 400)

    def H(self):
        self.root.update_idletasks()
        return max(self.canvas.winfo_height(), 300)

    def set_background(self, filename):
        img = IMAGES.get(filename)
        w, h = self.W(), self.H()
        if img:
            self._bg_ref = img
            iw, ih = img.width(), img.height()
            # center the art; canvas bg color fills any extra space
            self.canvas.create_image((w - iw) // 2, (h - ih) // 2, image=img, anchor="nw")
        else:
            self.canvas.create_rectangle(0, 0, w, h, fill=INK, outline="")

    def styled_button(self, parent, text, command, bg=PANEL_LIGHT, fg=TEXT_LIGHT,
                       width=26, height=2, wraplength=None):
        kwargs = dict(
            text=text, command=lambda: self._click(command),
            bg=bg, fg=fg, activebackground=GOLD, activeforeground=INK,
            font=self.f_button, relief="flat", bd=0,
            width=width, height=height, cursor="hand2",
            highlightthickness=1, highlightbackground=GOLD_DIM,
        )
        if wraplength:
            kwargs["wraplength"] = wraplength
        btn = tk.Button(parent, **kwargs)

        def on_enter(_):
            btn.configure(bg=GOLD, fg=INK)

        def on_leave(_):
            btn.configure(bg=bg, fg=fg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _click(self, command):
        self.sound.play("click.wav")
        command()

    # ==================================================================
    # SCREEN 1 - TITLE
    # ==================================================================
    def show_title_screen(self):
        self.clear_screen()
        gen = self._screen_gen
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("title_bg.png")

        title_id = self.canvas.create_text(
            w / 2, h * 0.20, text="MURDER MYSTERY",
            fill=GOLD, font=("Helvetica", max(20, int(w / 30)), "bold"))
        self.canvas.create_text(w / 2, h * 0.20 + 36, text="D E T E C T I V E",
                                 fill=TEXT_LIGHT, font=("Helvetica", max(13, int(w / 55)), "bold"))
        self.canvas.create_text(w / 2, h * 0.20 + 60, text="\u2014 Advanced Edition \u2014",
                                 fill=GOLD_DIM, font=("Helvetica", 11, "italic"))
        self.canvas.create_text(
            w / 2, h * 0.20 + 88,
            text=f"{len(cases)} cases. Countless suspects. Only one truth.",
            fill=TEXT_LIGHT, font=("Helvetica", 10, "italic"))

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        grid_y = h * 0.56
        self.canvas.create_window(w / 2, grid_y, window=btn_frame)

        left = tk.Frame(btn_frame, bg=INK)
        mid = tk.Frame(btn_frame, bg=INK)
        right = tk.Frame(btn_frame, bg=INK)
        left.pack(side="left", padx=8)
        mid.pack(side="left", padx=8)
        right.pack(side="left", padx=8)

        self.styled_button(left, "\U0001F50D START NEW INVESTIGATION",
                            self.show_case_select, bg="#173a1f", width=25).pack(pady=4)
        self.styled_button(left, "\U0001F4C2 LOAD SAVED GAME",
                            self.load_game, bg="#152a4a", width=25).pack(pady=4)
        self.styled_button(left, "\U0001F396 SUSPECT DATABASE",
                            self.show_suspect_db_list, bg="#2a1f3a", width=25).pack(pady=4)
        self.styled_button(left, "\U0001F9F0 EVIDENCE LOCKER",
                            self.show_evidence_locker, bg="#2a1f3a", width=25).pack(pady=4)

        self.styled_button(mid, "\U0001F4CA STATISTICS",
                            self.show_statistics_screen, bg="#0f2a3a", width=25).pack(pady=4)
        self.styled_button(mid, "\U0001F4C5 CASE HISTORY",
                            self.show_case_history_screen, bg="#0f2a3a", width=25).pack(pady=4)
        self.styled_button(mid, "\u2699 SETTINGS",
                            self.show_settings_screen, bg="#0f2a3a", width=25).pack(pady=4)
        self.styled_button(mid, "\U0001F3C6 PLAYER RECORDS",
                            self.show_records_screen, bg="#3a2f0f", width=25).pack(pady=4)

        self.styled_button(right, "\U0001F4DC CASE RECORDS",
                            self.show_case_records_screen, bg="#3a2f0f", width=25).pack(pady=4)
        self.styled_button(right, "\U0001F3C5 ACHIEVEMENTS",
                            self.show_achievements_screen, bg="#3a2f0f", width=25).pack(pady=4)
        self.styled_button(
            right,
            "\U0001F50A SOUND: ON" if self.sound.enabled else "\U0001F507 SOUND: OFF",
            self.toggle_sound_title, bg=PANEL_LIGHT, width=25).pack(pady=4)
        self.styled_button(right, "\U0001F6AA QUIT", self._on_close,
                            bg="#3a1414", width=25).pack(pady=4)

        # place the restart button and tagline using the grid's REAL rendered
        # height (not a guessed offset), so they never overlap on any screen size
        self.root.update_idletasks()
        grid_bottom = grid_y + btn_frame.winfo_reqheight() / 2

        restart_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(restart_frame)
        restart_y = grid_bottom + 30
        self.canvas.create_window(w / 2, restart_y, window=restart_frame)
        self.styled_button(
            restart_frame, "\U0001F504 RESTART GAME (ERASE ALL DATA & START FRESH)",
            self.confirm_restart_game, bg="#4a1010", width=50, height=1).pack()

        tagline_y = max(restart_y + 34, h - 16)
        self.canvas.create_text(
            w / 2, tagline_y,
            text="\"Every clue matters. Every suspect lies... or maybe not.\"",
            fill=GOLD_DIM, font=("Helvetica", 9, "italic"))

        self._flicker_title(title_id, gen)
        self._schedule_lightning(gen)

    def _flicker_title(self, item_id, gen):
        if gen != getattr(self, "_screen_gen", -1):
            return
        if not self.canvas.find_withtag(item_id):
            return
        color = random.choice([GOLD, GOLD, GOLD_BRIGHT, GOLD_DIM])
        try:
            self.canvas.itemconfigure(item_id, fill=color)
        except Exception:
            return
        self.root.after(random.randint(180, 500), lambda: self._flicker_title(item_id, gen))

    def _schedule_lightning(self, gen):
        if gen != getattr(self, "_screen_gen", -1):
            return
        delay = random.randint(4000, 9000)

        def flash():
            if gen != getattr(self, "_screen_gen", -1):
                return
            try:
                w, h = self.W(), self.H()
                rect = self.canvas.create_rectangle(0, 0, w, h, fill="#ffffff",
                                                      outline="", stipple="gray25")
                self.root.after(90, lambda: self._end_flash(rect, gen))
            except Exception:
                pass

        self.root.after(delay, flash)

    def _end_flash(self, rect, gen):
        self._safe_canvas_delete(rect)
        self._schedule_lightning(gen)

    def toggle_sound_title(self):
        self.sound.toggle()
        self.show_title_screen()

    # ==================================================================
    # SCREEN 2 - CASE SELECT
    # ==================================================================
    def show_case_select(self):
        self.clear_screen()
        self.sound.start_ambient("menu_theme.wav")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 34, text="SELECT A CASE", fill=GOLD, font=self.f_title)
        self.canvas.create_text(
            w / 2, 62,
            text=f"Score so far: {self.score}   |   Cases solved: {len(self.solved_cases)}/{len(cases)}",
            fill=TEXT_LIGHT, font=self.f_body)

        grid = tk.Frame(self.root, bg=INK)
        self.add_widget(grid)
        self.canvas.create_window(w / 2, h * 0.52, window=grid)

        cols = 4 if w > 820 else 2
        for i, case in enumerate(cases):
            r, c = divmod(i, cols)
            solved = i in self.solved_cases
            label = case["title"].strip()
            bg = "#173a1f" if solved else PANEL_LIGHT
            prefix = "\u2714 " if solved else "\U0001F575 "
            b = self.styled_button(
                grid, prefix + label, lambda idx=i: self.start_case(idx),
                bg=bg, width=22, height=4, wraplength=150)
            b.grid(row=r, column=c, padx=6, pady=6)

        bottom = tk.Frame(self.root, bg=INK)
        self.add_widget(bottom)
        self.canvas.create_window(w / 2, h - 32, window=bottom)
        self.styled_button(bottom, "\u2B05 TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=16).pack(side="left", padx=6)
        self.styled_button(bottom, "\U0001F4BE SAVE", self.save_game,
                            bg="#152a4a", width=16).pack(side="left", padx=6)
        self.styled_button(bottom, "\U0001F4DC CASE RECORDS", self.show_case_records_screen,
                            bg="#2a1f3a", width=18).pack(side="left", padx=6)

    def start_case(self, index):
        self.case_index = index
        self.evidence = []
        self.selected_suspect = None
        self.interrogated = set()
        self._case_start_time = time.time()
        case = cases[self.case_index]
        self.max_clues = len(case["clues"])
        self.show_case_intro()

    # ==================================================================
    # SCREEN 3 - CASE INTRO (typewriter story)
    # ==================================================================
    def show_case_intro(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        case = cases[self.case_index]
        self.set_background(f"case{self.case_index + 1}_bg.png")
        self._transition_wipe()
        self.sound.start_ambient()
        self.sound.play("door.wav")

        panel_w, panel_h = min(w - 80, 760), min(h - 170, 380)
        px0, py0 = (w - panel_w) / 2, (h - panel_h) / 2 - 15
        self.canvas.create_rectangle(px0, py0, px0 + panel_w, py0 + panel_h,
                                      fill="#000000", outline=GOLD, width=2)

        self.canvas.create_text(w / 2, py0 + 30, text=case["title"].strip(),
                                 fill=GOLD, font=self.f_h1, width=panel_w - 50)

        story_id = self.canvas.create_text(
            w / 2, py0 + panel_h / 2 + 8, text="", fill=TEXT_LIGHT,
            font=self.f_body, width=panel_w - 60, justify="center")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, py0 + panel_h + 38, window=btn_frame)

        row = tk.Frame(btn_frame, bg=INK)
        row.pack()

        def begin_investigation():
            self.sound.play("footstep.wav")
            self.show_investigation()

        begin_btn = self.styled_button(row, "BEGIN INVESTIGATION \u25B6",
                                        begin_investigation, bg="#173a1f", width=22)
        begin_btn.configure(state="disabled")
        begin_btn.pack(side="left", padx=5)
        skip_btn = self.styled_button(row, "SKIP \u23ED", lambda: None,
                                       bg=PANEL_LIGHT, width=9)
        skip_btn.pack(side="left", padx=5)

        full_text = case["story"].strip()
        self._typing_active = True

        def finish_now():
            self._typing_active = False
            self.canvas.itemconfigure(story_id, text=full_text)
            begin_btn.configure(state="normal")

        skip_btn.configure(command=lambda: self._click(finish_now))
        self._typewriter(story_id, full_text, 0, begin_btn)

    def _typewriter(self, item_id, full_text, pos, enable_btn):
        if not getattr(self, "_typing_active", False):
            return
        if not self.canvas.find_withtag(item_id):
            return
        pos2 = min(len(full_text), pos + 3)
        self.canvas.itemconfigure(item_id, text=full_text[:pos2])
        if pos2 < len(full_text):
            self.root.after(12, lambda: self._typewriter(item_id, full_text, pos2, enable_btn))
        else:
            self._typing_active = False
            try:
                enable_btn.configure(state="normal")
            except Exception:
                pass

    # ==================================================================
    # SCREEN 4 - INVESTIGATION (main hub)
    # ==================================================================
    def show_investigation(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        case = cases[self.case_index]
        self.set_background(f"case{self.case_index + 1}_bg.png")
        self.sound.start_ambient()

        self.canvas.create_rectangle(0, 0, w, 44, fill="#000000", outline="")
        self.canvas.create_text(14, 22, anchor="w", text=case["title"].strip(),
                                 fill=GOLD, font=self.f_h2)
        self.canvas.create_text(
            w - 14, 22, anchor="e",
            text=f"SCORE: {self.score}   |   CLUES: {len(self.evidence)}/{self.max_clues}",
            fill=TEXT_LIGHT, font=self.f_h2)

        panel_w = w - 60
        panel_h = min(h * 0.48, 290)
        panel = tk.Frame(self.root, bg=PANEL, highlightbackground=GOLD_DIM, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 60 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        tk.Label(panel, text="SUSPECTS", bg=PANEL, fg=GOLD, font=self.f_h2).pack(pady=(8, 2))

        roster = tk.Frame(panel, bg=PANEL)
        roster.pack(pady=2, fill="both", expand=True)

        card_w = max(100, int(panel_w / max(1, len(case["suspects"]))) - 14)
        self.suspect_widgets = {}
        for i, s in enumerate(case["suspects"]):
            card = tk.Frame(roster, bg=PANEL_LIGHT, highlightbackground=GOLD_DIM,
                             highlightthickness=1)
            card.grid(row=0, column=i, padx=5, pady=3, sticky="n")

            av_file = f"avatar_{i % 8}.png"
            av_img = IMAGES.get(av_file)
            if av_img:
                try:
                    av_small = av_img.subsample(4, 4)
                except Exception:
                    av_small = av_img
                lbl_img = tk.Label(card, image=av_small, bg=PANEL_LIGHT)
                lbl_img.image = av_small
                lbl_img.pack(pady=(6, 2))

            tk.Label(card, text=s["name"], bg=PANEL_LIGHT, fg=TEXT_LIGHT,
                     font=self.f_body_b, wraplength=card_w, justify="center").pack(padx=4)
            tk.Label(card, text=s["backstory"], bg=PANEL_LIGHT, fg=TEXT_DIM,
                     font=self.f_small, wraplength=card_w, justify="center").pack(
                padx=5, pady=(2, 4))

            btn_row = tk.Frame(card, bg=PANEL_LIGHT)
            btn_row.pack(pady=(0, 6))
            sel_btn = tk.Button(
                btn_row, text="SELECT", font=self.f_small,
                bg=PANEL_LIGHT, fg=GOLD, relief="flat", cursor="hand2", bd=0,
                command=lambda n=s["name"]: self.select_suspect(n))
            sel_btn.pack(side="left", padx=(0, 3))
            interro_btn = tk.Button(
                btn_row, text="\u2753 ASK", font=self.f_small,
                bg=PANEL_LIGHT, fg="#8fb0d6", relief="flat", cursor="hand2", bd=0,
                command=lambda n=s["name"], st=s["statement"]: self.interrogate_suspect(n, st))
            interro_btn.pack(side="left")
            self.suspect_widgets[s["name"]] = (card, sel_btn)

        notebook_frame = tk.Frame(self.root, bg=PANEL, highlightbackground=GOLD_DIM,
                                   highlightthickness=1)
        self.add_widget(notebook_frame)
        nb_y = 60 + panel_h + 62
        self.canvas.create_window(w / 2, nb_y, window=notebook_frame, width=panel_w, height=90)

        tk.Label(notebook_frame, text="\U0001F4D3 CASE NOTEBOOK", bg=PANEL, fg=GOLD,
                 font=self.f_small).pack(anchor="w", padx=8, pady=(5, 0))
        self.notebook_text = tk.Text(notebook_frame, bg=PANEL, fg=TEXT_LIGHT,
                                      font=self.f_small, height=3, bd=0,
                                      highlightthickness=0, wrap="word")
        self.notebook_text.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        self.refresh_notebook()

        ready, req_text = self.accuse_requirements(case)
        self.canvas.create_text(
            w / 2, nb_y + 58,
            text=req_text, fill=(GREEN_BRIGHT if ready else GOLD_DIM),
            font=self.f_small)

        action_bar = tk.Frame(self.root, bg=INK)
        self.add_widget(action_bar)
        self.canvas.create_window(w / 2, h - 26, window=action_bar)

        self.styled_button(action_bar, "\U0001F50D INVESTIGATE", self.investigate,
                            bg="#173a1f", width=15).pack(side="left", padx=3)
        accuse_btn = self.styled_button(
            action_bar, "\u2696 ACCUSE" if ready else "\U0001F512 ACCUSE", self.accuse,
            bg=("#5a1414" if ready else PANEL_LIGHT), width=13)
        accuse_btn.pack(side="left", padx=3)
        if not ready:
            accuse_btn.configure(state="disabled")
        self.styled_button(action_bar, "\U0001F4BE SAVE", self.save_game,
                            bg="#152a4a", width=10).pack(side="left", padx=3)
        self.styled_button(action_bar, "\u2B05 CASES", self.show_case_select,
                            bg=PANEL_LIGHT, width=10).pack(side="left", padx=3)

        self.highlight_selected_suspect()

    def accuse_requirements(self, case):
        """Returns (ready: bool, message: str) based on the active difficulty."""
        cfg = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["Medium"])
        need_clues = max(1, math.ceil(cfg["clue_fraction"] * len(case["clues"])))
        have_clues = len(self.evidence)
        clue_ok = have_clues >= need_clues

        need_interrogation = cfg["require_interrogation"]
        interro_ok = True
        if need_interrogation:
            interro_ok = len(self.interrogated) >= len(case["suspects"])

        ready = clue_ok and interro_ok
        if ready:
            return True, "\u2696 Enough evidence gathered - you may make your accusation."

        parts = [f"Clues: {have_clues}/{need_clues} needed"]
        if need_interrogation:
            parts.append(f"Suspects interrogated: {len(self.interrogated)}/{len(case['suspects'])} needed")
        return False, f"\U0001F512 Accuse locked ({self.difficulty}) - " + "  \u2022  ".join(parts)

    def select_suspect(self, name):
        self.sound.play("click.wav")
        self.selected_suspect = name
        self.highlight_selected_suspect()

    def highlight_selected_suspect(self):
        for name, (card, btn) in getattr(self, "suspect_widgets", {}).items():
            if name == self.selected_suspect:
                card.configure(highlightbackground=GOLD, highlightthickness=3)
                btn.configure(text="\u2714 SELECTED", fg=GOLD)
            else:
                card.configure(highlightbackground=GOLD_DIM, highlightthickness=1)
                btn.configure(text="SELECT", fg=GOLD)

    def interrogate_suspect(self, name, statement):
        self.sound.play("interrogation.wav")
        self.interrogated.add(name)
        self.show_popup(f"\U0001F5E3 {name.upper()}", f'"{statement}"', accent=BLUE_BRIGHT)
        self.show_investigation()
        self.auto_save()

    def investigate(self):
        case = cases[self.case_index]
        remaining = [c for c in case["clues"] if c not in self.evidence]
        if not remaining:
            self.show_popup("\U0001F50D NO MORE CLUES",
                             "You have uncovered every clue in this location.\n"
                             "Review your notebook and decide who to accuse.", accent=GOLD)
            return
        clue = random.choice(remaining)
        self.evidence.append(clue)
        self.log_evidence(case, clue)
        self.refresh_notebook()
        self.sound.play("clue.wav")

        if random.random() < 0.13:
            self._jump_scare()

        self.show_popup("\U0001F50D CLUE DISCOVERED", clue, accent=GREEN)
        self.show_investigation()
        self.auto_save()

    def _jump_scare(self):
        """A short horror flash + stinger while investigating a scene."""
        try:
            w, h = self.W(), self.H()
            rect = self.canvas.create_rectangle(0, 0, w, h, fill="#3a0000", outline="")
            self.sound.play("horror_stinger.wav")
            self.root.after(130, lambda: self._safe_canvas_delete(rect))
        except Exception:
            pass

    def _safe_canvas_delete(self, item_id):
        try:
            self.canvas.delete(item_id)
        except Exception:
            pass

    def _transition_wipe(self):
        """A brief dark wipe used when moving between major screens, for a
        subtle 'scene change' feel. Safe no-op if the canvas isn't ready."""
        try:
            w, h = self.W(), self.H()
            rect = self.canvas.create_rectangle(0, 0, w, h, fill="#000000", outline="")
            self.root.after(90, lambda: self._safe_canvas_delete(rect))
        except Exception:
            pass

    def refresh_notebook(self):
        if not hasattr(self, "notebook_text"):
            return
        self.notebook_text.delete("1.0", "end")
        if not self.evidence:
            self.notebook_text.insert("end", "No clues collected yet. Click INVESTIGATE to search the scene.")
        else:
            for e in self.evidence:
                self.notebook_text.insert("end", f"\u2022 {e}\n")

    def accuse(self):
        if self.selected_suspect is None:
            self.show_popup("\u26A0 NO SUSPECT SELECTED",
                             "Select a suspect from the roster before making an accusation.",
                             accent=RED)
            return
        case = cases[self.case_index]
        ready, req_text = self.accuse_requirements(case)
        if not ready:
            self.show_popup("\U0001F512 NOT READY TO ACCUSE", req_text, accent=GOLD)
            return

        suspect = self.selected_suspect
        correct = suspect == case["killer"]
        elapsed_seconds = int(time.time() - self._case_start_time) if self._case_start_time else 0

        if correct:
            self.score += 1
            if self.case_index not in self.solved_cases:
                self.solved_cases.append(self.case_index)
            self.sound.play("correct.mp3")
        else:
            self.sound.play("wrong.wav")

        self.record_case_attempt(
            case, suspect, correct,
            clues_collected=len(self.evidence), total_clues=self.max_clues,
            interrogated_count=len(self.interrogated), total_suspects=len(case["suspects"]),
        )

        grade, xp_earned = self.grade_case(case, correct, elapsed_seconds)
        if xp_earned:
            self.award_xp(xp_earned)

        newly_unlocked = self.check_achievements()
        self.auto_save()
        report = {
            "grade": grade, "xp_earned": xp_earned, "elapsed_seconds": elapsed_seconds,
            "clues_collected": len(self.evidence), "total_clues": self.max_clues,
            "interrogated": len(self.interrogated), "total_suspects": len(case["suspects"]),
        }
        self.show_result_screen(correct, suspect, case, newly_unlocked, report)

    def grade_case(self, case, correct, elapsed_seconds):
        """Returns (letter_grade, xp_earned) for the Case Report."""
        cfg = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["Medium"])
        if not correct:
            return "F", max(5, int(10 * cfg["xp_mult"]))  # small XP for the attempt

        clue_ratio = len(self.evidence) / max(1, self.max_clues)
        interro_ratio = len(self.interrogated) / max(1, len(case["suspects"]))
        base = 50
        bonus = 0
        if clue_ratio >= 0.999:
            bonus += 20
        if interro_ratio >= 0.999:
            bonus += 15
        if elapsed_seconds > 0 and elapsed_seconds < 90:
            bonus += 15  # quick solve bonus

        score_pct = min(100, base + bonus)
        if score_pct >= 90:
            grade = "S"
        elif score_pct >= 75:
            grade = "A"
        elif score_pct >= 60:
            grade = "B"
        elif score_pct >= 45:
            grade = "C"
        else:
            grade = "D"

        xp = int((base + bonus) * cfg["xp_mult"])
        return grade, xp

    # ==================================================================
    # SCREEN 5 - RESULT
    # ==================================================================
    def show_result_screen(self, correct, accused, case, newly_unlocked=None, report=None):
        self.clear_screen()
        w, h = self.W(), self.H()
        self.set_background("result_win_bg.png" if correct else "result_lose_bg.png")
        self._transition_wipe()

        if correct:
            self.sound.play("victory_music.wav")
        headline = "CASE SOLVED" if correct else "WRONG ACCUSATION"
        color = GREEN_BRIGHT if correct else RED_BRIGHT
        self.canvas.create_text(w / 2, 46, text=headline, fill=color,
                                 font=("Helvetica", 22, "bold"))
        self.canvas.create_text(w / 2, 76, text=case["title"].strip(),
                                 fill=GOLD, font=self.f_h2)

        panel_w, panel_h = min(w - 100, 700), min(h - 200, 380)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 96 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        text_widget = tk.Text(panel, bg=PANEL, fg=TEXT_LIGHT, bd=0,
                               font=self.f_body, wrap="word", highlightthickness=0)
        text_widget.pack(fill="both", expand=True, padx=16, pady=14)

        def add_line(text, gold=False, bold=False):
            f = self.f_body_b if bold else self.f_body
            tagname = f"tag{text_widget.index('end')}"
            start = text_widget.index("end")
            text_widget.insert("end", text + "\n")
            text_widget.tag_add(tagname, start, "end")
            text_widget.tag_configure(tagname, font=f, foreground=(GOLD_BRIGHT if gold else TEXT_LIGHT))

        if report:
            mins, secs = divmod(report["elapsed_seconds"], 60)
            add_line("\U0001F4CB CASE REPORT", gold=True, bold=True)
            add_line(
                f"Grade: {report['grade']}   \u2022   XP Earned: +{report['xp_earned']}   "
                f"\u2022   Time: {mins}m {secs}s"
            )
            add_line(
                f"Evidence: {report['clues_collected']}/{report['total_clues']}   "
                f"\u2022   Suspects Interrogated: {report['interrogated']}/{report['total_suspects']}"
            )
            add_line("")

        if correct:
            add_line(f"You accused: {accused}", gold=True, bold=True)
            add_line("")
            add_line("This was the correct call. Here's why:", bold=True)
            add_line(case["solution"]["killer_reason"])
        else:
            add_line(f"You accused: {accused}", gold=True, bold=True)
            add_line("")
            reason = case["solution"]["innocent_reasons"].get(
                accused, "No evidence ever connected this suspect to the crime.")
            add_line("Why they're innocent:", bold=True)
            add_line(reason)
            add_line("")
            add_line(f"The real killer was: {case['killer']}", gold=True, bold=True)
            add_line("")
            add_line("Why they're guilty:", bold=True)
            add_line(case["solution"]["killer_reason"])

        if newly_unlocked:
            add_line("")
            add_line("\U0001F3C5 ACHIEVEMENT UNLOCKED:", gold=True, bold=True)
            for a in newly_unlocked:
                add_line(f"  \u2726 {a['title']} - {a['desc']}", gold=True)
            self.sound.play("fanfare.wav")

        text_widget.configure(state="disabled")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 30, window=btn_frame)

        self.styled_button(btn_frame, "\u2B05 CASE LIST", self.show_case_select,
                            bg=PANEL_LIGHT, width=18).pack(side="left", padx=5)

        next_index = self.case_index + 1
        if next_index < len(cases):
            self.styled_button(btn_frame, "NEXT CASE \u25B6",
                                lambda: self.start_case(next_index),
                                bg="#173a1f", width=18).pack(side="left", padx=5)
        else:
            self.styled_button(btn_frame, "\U0001F3C1 FINISH GAME",
                                self.show_game_over, bg="#173a1f", width=18).pack(side="left", padx=5)

    # ==================================================================
    # SCREEN 6 - GAME OVER
    # ==================================================================
    def show_game_over(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        total = len(cases)
        did_well = self.score >= total * 0.5
        self.set_background("result_win_bg.png" if did_well else "result_lose_bg.png")
        self._transition_wipe()
        self.sound.stop_ambient()
        self.sound.play("victory_music.wav" if did_well else "gameover_music.wav")
        self.sound.play("fanfare.wav")

        self.canvas.create_text(w / 2, 58, text="INVESTIGATION COMPLETE",
                                 fill=GOLD, font=("Helvetica", 20, "bold"))
        self.canvas.create_text(
            w / 2, 90,
            text=f"Final Score: {self.score} / {len(cases)} cases solved correctly",
            fill=TEXT_LIGHT, font=self.f_h2)

        rank = self.get_rank()
        cfg = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["Medium"])
        completion_xp = int(100 * cfg["xp_mult"] * (self.score / total if total else 0))
        if completion_xp:
            self.award_xp(completion_xp)
        self.canvas.create_text(w / 2, 118, text=f"Detective Rank: {rank}   \u2022   +{completion_xp} XP",
                                 fill=GOLD_DIM, font=("Helvetica", 11, "italic"))

        form = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(form)
        self.canvas.create_window(w / 2, 175, window=form, width=400, height=88)

        tk.Label(form, text="Enter your detective name to save this result:",
                 bg=PANEL, fg=TEXT_LIGHT, font=self.f_small).pack(pady=(10, 5))
        name_var = tk.StringVar(value="Detective")
        entry = tk.Entry(form, textvariable=name_var, font=self.f_body,
                          justify="center", bg=PANEL_LIGHT, fg=TEXT_LIGHT,
                          insertbackground=TEXT_LIGHT, relief="flat", width=24)
        entry.pack(pady=3)

        def do_save():
            self.record_result(name_var.get().strip() or "Detective", rank)
            save_btn.configure(state="disabled", text="\u2714 SAVED")

        save_btn = self.styled_button(form, "SAVE RESULT", do_save, bg="#173a1f", width=13, height=1)
        save_btn.pack(pady=(0, 4))

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, 300, window=btn_frame)

        self.styled_button(btn_frame, "\U0001F3C6 VIEW RECORDS", self.show_records_screen,
                            bg="#3a2f0f", width=24).pack(pady=4)
        self.styled_button(btn_frame, "\U0001F501 PLAY AGAIN", self.reset_game,
                            bg="#173a1f", width=24).pack(pady=4)
        self.styled_button(btn_frame, "\u2B05 TITLE SCREEN", self.show_title_screen,
                            bg=PANEL_LIGHT, width=24).pack(pady=4)
        self.styled_button(btn_frame, "\U0001F6AA QUIT", self._on_close,
                            bg="#3a1414", width=24).pack(pady=4)

    def get_rank(self):
        total = len(cases)
        frac = self.score / total if total else 0
        if self.score == total:
            return "LEGEND DETECTIVE"
        if frac >= 0.85:
            return "CHIEF INSPECTOR"
        if frac >= 0.70:
            return "INSPECTOR"
        if frac >= 0.55:
            return "SENIOR DETECTIVE"
        if frac >= 0.40:
            return "DETECTIVE"
        if frac >= 0.25:
            return "JUNIOR DETECTIVE"
        if frac >= 0.10:
            return "OFFICER"
        return "TRAINEE"

    def reset_game(self):
        self.case_index = 0
        self.score = 0
        self.solved_cases = []
        self.evidence = []
        self.selected_suspect = None
        self.interrogated = set()
        self.show_title_screen()

    # ==================================================================
    # PLAYER RECORDS (overall leaderboard across full playthroughs)
    # ==================================================================
    def load_records(self):
        if not os.path.exists(RECORDS_FILE):
            return []
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def record_result(self, name, rank):
        records = self.load_records()
        records.append({
            "name": name, "score": self.score, "total": len(cases),
            "rank": rank, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        records.sort(key=lambda r: r["score"], reverse=True)
        records = records[:50]
        try:
            with open(RECORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            self.show_popup("\u26A0 COULD NOT SAVE RECORD", str(e), accent=RED)

    def show_records_screen(self):
        self.clear_screen()
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 32, text="PLAYER RECORDS", fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 58, text="All-time top detective scores",
                                 fill=TEXT_LIGHT, font=self.f_body)

        panel_w, panel_h = min(w - 80, 700), min(h - 170, 380)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        header = tk.Frame(panel, bg=PANEL)
        header.pack(fill="x", padx=14, pady=(10, 3))
        for text, wd in [("#", 3), ("NAME", 14), ("SCORE", 7), ("RANK", 20), ("DATE", 13)]:
            tk.Label(header, text=text, bg=PANEL, fg=GOLD, font=self.f_body_b,
                     width=wd, anchor="w").pack(side="left")

        rows_frame = tk.Frame(panel, bg=PANEL)
        rows_frame.pack(fill="both", expand=True, padx=14)

        records = self.load_records()
        if not records:
            tk.Label(rows_frame,
                     text="No records yet - finish an investigation to set the first score!",
                     bg=PANEL, fg=TEXT_DIM, font=self.f_body).pack(pady=26)
        else:
            for i, r in enumerate(records[:10], start=1):
                row = tk.Frame(rows_frame, bg=PANEL)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=str(i), bg=PANEL, fg=TEXT_LIGHT, font=self.f_small,
                         width=3, anchor="w").pack(side="left")
                tk.Label(row, text=r.get("name", "Detective"), bg=PANEL, fg=TEXT_LIGHT,
                         font=self.f_small, width=14, anchor="w").pack(side="left")
                tk.Label(row, text=f"{r.get('score', 0)}/{r.get('total', len(cases))}",
                         bg=PANEL, fg=GREEN_BRIGHT, font=self.f_small, width=7, anchor="w").pack(side="left")
                tk.Label(row, text=r.get("rank", ""), bg=PANEL, fg=GOLD_DIM,
                         font=self.f_small, width=20, anchor="w").pack(side="left")
                tk.Label(row, text=r.get("date", ""), bg=PANEL, fg=TEXT_DIM,
                         font=self.f_small, width=13, anchor="w").pack(side="left")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # CASE RECORDS (per-case attempt history - every accusation logged)
    # ==================================================================
    def load_case_records(self):
        if not os.path.exists(CASE_RECORDS_FILE):
            return []
        try:
            with open(CASE_RECORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def record_case_attempt(self, case, accused, correct, clues_collected=0, total_clues=0,
                             interrogated_count=0, total_suspects=0):
        records = self.load_case_records()
        records.append({
            "case_title": case["title"].strip(),
            "accused": accused,
            "correct": correct,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "clues_collected": clues_collected,
            "total_clues": total_clues,
            "interrogated_count": interrogated_count,
            "total_suspects": total_suspects,
        })
        try:
            with open(CASE_RECORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(records[-500:], f, indent=2)
        except Exception:
            pass

    def log_evidence(self, case, clue):
        try:
            log = []
            if os.path.exists(EVIDENCE_LOG_FILE):
                with open(EVIDENCE_LOG_FILE, "r", encoding="utf-8") as f:
                    log = json.load(f)
            log.append({
                "case_title": case["title"].strip(),
                "clue": clue,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            with open(EVIDENCE_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(log[-1000:], f, indent=2)
        except Exception:
            pass

    def show_case_records_screen(self):
        self.clear_screen()
        self.sound.start_ambient("menu_theme.wav")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 32, text="CASE RECORDS", fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 58, text="Your attempt history for every case",
                                 fill=TEXT_LIGHT, font=self.f_body)

        panel_w, panel_h = min(w - 80, 760), min(h - 170, 400)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        canvas_scroll = tk.Canvas(panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=PANEL)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        attempts = self.load_case_records()
        header = tk.Frame(inner, bg=PANEL)
        header.pack(fill="x", pady=(0, 4))
        for text, wd in [("CASE", 30), ("ATTEMPTS", 9), ("SOLVED", 8), ("LAST RESULT", 22)]:
            tk.Label(header, text=text, bg=PANEL, fg=GOLD, font=self.f_body_b,
                     width=wd, anchor="w").pack(side="left")

        if not attempts:
            tk.Label(inner, text="No case attempts yet - make an accusation in any case to begin your record.",
                     bg=PANEL, fg=TEXT_DIM, font=self.f_body).pack(pady=20, padx=6, anchor="w")
        else:
            for case in cases:
                title = case["title"].strip()
                case_attempts = [a for a in attempts if a["case_title"] == title]
                if not case_attempts:
                    continue
                total = len(case_attempts)
                solved_count = sum(1 for a in case_attempts if a["correct"])
                last = case_attempts[-1]
                last_text = ("\u2714 Correct" if last["correct"] else "\u2716 Wrong") + f" ({last['accused']})"
                row = tk.Frame(inner, bg=PANEL_LIGHT, highlightbackground=GOLD_DIM, highlightthickness=1)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=title, bg=PANEL_LIGHT, fg=TEXT_LIGHT, font=self.f_small,
                         width=30, anchor="w", wraplength=230, justify="left").pack(side="left", padx=(4, 0), pady=4)
                tk.Label(row, text=str(total), bg=PANEL_LIGHT, fg=TEXT_LIGHT, font=self.f_small,
                         width=9, anchor="w").pack(side="left")
                tk.Label(row, text=str(solved_count), bg=PANEL_LIGHT, fg=GREEN_BRIGHT, font=self.f_small,
                         width=8, anchor="w").pack(side="left")
                tk.Label(row, text=last_text, bg=PANEL_LIGHT,
                         fg=(GREEN_BRIGHT if last["correct"] else RED_BRIGHT),
                         font=self.f_small, width=22, anchor="w").pack(side="left")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # PLAYER STATISTICS
    # ==================================================================
    def show_statistics_screen(self):
        self.clear_screen()
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 34, text="DETECTIVE STATISTICS", fill=GOLD, font=self.f_title)

        profile = self.load_profile() or {}
        case_records = self.load_case_records()
        total_attempts = len(case_records)
        solved = sum(1 for a in case_records if a["correct"])
        failed = total_attempts - solved
        accuracy = (solved / total_attempts * 100) if total_attempts else 0.0

        total_seconds = profile.get("total_play_seconds", 0) + int(time.time() - self._session_start)
        hrs, rem = divmod(total_seconds, 3600)
        mins, secs = divmod(rem, 60)
        play_time_str = f"{hrs}h {mins}m {secs}s" if hrs else f"{mins}m {secs}s"

        level, rank, into_level, per_level = self.xp_progress(profile.get("xp", 0))
        unique_solved = len({a["case_title"] for a in case_records if a["correct"]})

        panel_w, panel_h = min(w - 100, 640), min(h - 170, 380)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        rows = [
            ("Detective", profile.get("name", "Unknown")),
            ("Level / Rank", f"{level}  \u2022  {rank}  ({into_level}/{per_level} XP into level)"),
            ("Total XP", str(profile.get("xp", 0))),
            ("Cases Attempted", str(total_attempts)),
            ("Cases Solved (correct)", str(solved)),
            ("Cases Failed (wrong)", str(failed)),
            ("Unique Cases Cleared", f"{unique_solved} / {len(cases)}"),
            ("Accuracy", f"{accuracy:.1f}%"),
            ("Total Play Time", play_time_str),
            ("Difficulty", self.difficulty),
        ]
        inner = tk.Frame(panel, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=20, pady=16)
        for label, value in rows:
            row = tk.Frame(inner, bg=PANEL)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=PANEL, fg=GOLD_DIM, font=self.f_body,
                     width=22, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=PANEL, fg=TEXT_LIGHT, font=self.f_body_b,
                     anchor="w").pack(side="left")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # CASE HISTORY (Solved / Failed / Locked status per case)
    # ==================================================================
    def show_case_history_screen(self):
        self.clear_screen()
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 34, text="CASE HISTORY", fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 60, text="Status of every case you've encountered",
                                 fill=TEXT_LIGHT, font=self.f_body)

        panel_w, panel_h = min(w - 80, 760), min(h - 170, 400)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        canvas_scroll = tk.Canvas(panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=PANEL)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        case_records = self.load_case_records()
        for case in cases:
            title = case["title"].strip()
            attempts = [a for a in case_records if a["case_title"] == title]
            if not attempts:
                status, color = "LOCKED (not yet attempted)", TEXT_DIM
            elif any(a["correct"] for a in attempts):
                status, color = "\u2714 SOLVED", GREEN_BRIGHT
            else:
                status, color = "\u2716 FAILED (retry available)", RED_BRIGHT

            row = tk.Frame(inner, bg=PANEL_LIGHT, highlightbackground=GOLD_DIM, highlightthickness=1)
            row.pack(fill="x", pady=3, padx=4)
            tk.Label(row, text=title, bg=PANEL_LIGHT, fg=TEXT_LIGHT, font=self.f_body_b,
                     anchor="w", wraplength=panel_w - 260, justify="left").pack(
                side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(row, text=status, bg=PANEL_LIGHT, fg=color, font=self.f_small,
                     anchor="e").pack(side="right", padx=10)

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # SETTINGS (volume controls + difficulty)
    # ==================================================================
    def show_settings_screen(self):
        self.clear_screen()
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 34, text="SETTINGS", fill=GOLD, font=self.f_title)

        panel_w, panel_h = min(w - 100, 480), min(h - 170, 380)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 70 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        inner = tk.Frame(panel, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(inner, text="\U0001F3B5 MUSIC VOLUME", bg=PANEL, fg=GOLD_DIM,
                 font=self.f_small, anchor="w").pack(fill="x", pady=(4, 0))
        music_scale = tk.Scale(
            inner, from_=0, to=100, orient="horizontal", bg=PANEL, fg=TEXT_LIGHT,
            troughcolor=PANEL_LIGHT, highlightthickness=0, font=self.f_small,
            command=lambda v: self.sound.set_music_volume(int(v) / 100))
        music_scale.set(int(self.sound.music_volume * 100))
        music_scale.pack(fill="x")

        tk.Label(inner, text="\U0001F50A SOUND EFFECTS VOLUME", bg=PANEL, fg=GOLD_DIM,
                 font=self.f_small, anchor="w").pack(fill="x", pady=(10, 0))
        sfx_scale = tk.Scale(
            inner, from_=0, to=100, orient="horizontal", bg=PANEL, fg=TEXT_LIGHT,
            troughcolor=PANEL_LIGHT, highlightthickness=0, font=self.f_small,
            command=lambda v: self.sound.set_sfx_volume(int(v) / 100))
        sfx_scale.set(int(self.sound.sfx_volume * 100))
        sfx_scale.pack(fill="x")

        note = "Note: volume sliders fully apply when the optional 'pygame' package is installed."
        if self.sound.backend != "pygame":
            tk.Label(inner, text=note, bg=PANEL, fg=TEXT_DIM, font=self.f_small,
                     wraplength=panel_w - 60, justify="left").pack(fill="x", pady=(6, 0))

        tk.Label(inner, text="\U0001F3AF DIFFICULTY", bg=PANEL, fg=GOLD_DIM,
                 font=self.f_small, anchor="w").pack(fill="x", pady=(14, 2))
        diff_var = tk.StringVar(value=self.difficulty)
        diff_row = tk.Frame(inner, bg=PANEL)
        diff_row.pack(fill="x")
        for level in ("Easy", "Medium", "Hard"):
            tk.Radiobutton(diff_row, text=level, variable=diff_var, value=level,
                            bg=PANEL, fg=TEXT_LIGHT, selectcolor=PANEL_LIGHT,
                            activebackground=PANEL, activeforeground=GOLD,
                            font=self.f_small).pack(side="left", padx=8)

        def apply_and_save():
            self.difficulty = diff_var.get()
            self.save_settings({
                "difficulty": self.difficulty,
                "music_volume": self.sound.music_volume,
                "sfx_volume": self.sound.sfx_volume,
            })
            self.show_popup("\u2699 SETTINGS SAVED",
                             f"Difficulty set to {self.difficulty}. Volume preferences saved.",
                             accent=GREEN)

        self.styled_button(inner, "\U0001F4BE SAVE SETTINGS", apply_and_save,
                            bg="#173a1f", width=22).pack(pady=(18, 0))

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # ACHIEVEMENTS
    # ==================================================================
    ACHIEVEMENT_DEFS = [
        ("first_blood", "First Blood", "Correctly solve your very first case.",
         lambda cr, pr: any(a["correct"] for a in cr)),
        ("five_solved", "Getting Good", "Correctly solve 5 cases across all time.",
         lambda cr, pr: sum(1 for a in cr if a["correct"]) >= 5),
        ("ten_solved", "Seasoned Sleuth", "Correctly solve 10 cases across all time.",
         lambda cr, pr: sum(1 for a in cr if a["correct"]) >= 10),
        ("all_cases_cleared", "Case Closed: All Files",
         "Correctly solve every case at least once.",
         lambda cr, pr: len({a["case_title"] for a in cr if a["correct"]}) >= len(cases)),
        ("perfect_playthrough", "Flawless Detective",
         "Finish a full playthrough with a perfect score.",
         lambda cr, pr: any(r["score"] == r["total"] for r in pr)),
        ("quick_draw", "Quick Draw", "Solve a case correctly using only one clue.",
         lambda cr, pr: any(a["correct"] and a.get("clues_collected") == 1 for a in cr)),
        ("evidence_hound", "Evidence Hound", "Collect every clue in a case before accusing.",
         lambda cr, pr: any(
             a.get("total_clues") and a.get("clues_collected") == a.get("total_clues") for a in cr)),
        ("interrogator", "Master Interrogator",
         "Interrogate every suspect in a case before accusing.",
         lambda cr, pr: any(
             a.get("total_suspects") and a.get("interrogated_count") == a.get("total_suspects") for a in cr)),
        ("wrong_turn", "Learning Curve",
         "Make a wrong accusation - every detective makes mistakes.",
         lambda cr, pr: any(not a["correct"] for a in cr)),
        ("legend_rank", "Living Legend", "Reach Legend Detective rank in a completed playthrough.",
         lambda cr, pr: any(r["rank"] == "LEGEND DETECTIVE" for r in pr)),
        ("dedicated", "Dedicated Detective", "Make 25 total accusations, right or wrong.",
         lambda cr, pr: len(cr) >= 25),
        ("veteran", "Veteran Investigator", "Complete 3 full playthroughs.",
         lambda cr, pr: len(pr) >= 3),
    ]

    def load_achievements(self):
        if not os.path.exists(ACHIEVEMENTS_FILE):
            return []
        try:
            with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def check_achievements(self):
        """Evaluates all achievement conditions against persisted history and
        unlocks any newly-earned ones. Returns the list of newly unlocked."""
        unlocked = self.load_achievements()
        unlocked_ids = {a["id"] for a in unlocked}
        case_records = self.load_case_records()
        player_records = self.load_records()
        newly = []
        for aid, title, desc, check_fn in self.ACHIEVEMENT_DEFS:
            if aid in unlocked_ids:
                continue
            try:
                if check_fn(case_records, player_records):
                    entry = {"id": aid, "title": title, "desc": desc,
                              "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                    unlocked.append(entry)
                    newly.append(entry)
            except Exception:
                continue
        if newly:
            try:
                with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(unlocked, f, indent=2)
            except Exception:
                pass
        return newly

    def show_achievements_screen(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 32, text="ACHIEVEMENTS", fill=GOLD, font=self.f_title)
        unlocked = self.load_achievements()
        unlocked_ids = {a["id"] for a in unlocked}
        self.canvas.create_text(
            w / 2, 58, text=f"{len(unlocked_ids)} / {len(self.ACHIEVEMENT_DEFS)} unlocked",
            fill=TEXT_LIGHT, font=self.f_body)

        panel_w, panel_h = min(w - 80, 720), min(h - 170, 400)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        canvas_scroll = tk.Canvas(panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=PANEL)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        for aid, title, desc, _ in self.ACHIEVEMENT_DEFS:
            got = aid in unlocked_ids
            row = tk.Frame(inner, bg=(PANEL_LIGHT if got else PANEL),
                            highlightbackground=(GOLD if got else GOLD_DIM), highlightthickness=1)
            row.pack(fill="x", pady=3, padx=4)
            icon = "\U0001F3C5" if got else "\U0001F512"
            tk.Label(row, text=icon, bg=row["bg"], fg=(GOLD_BRIGHT if got else TEXT_DIM),
                     font=self.f_h2).pack(side="left", padx=(8, 6), pady=6)
            col = tk.Frame(row, bg=row["bg"])
            col.pack(side="left", fill="x", expand=True, pady=6)
            tk.Label(col, text=title, bg=row["bg"], fg=(GOLD_BRIGHT if got else TEXT_LIGHT),
                     font=self.f_body_b, anchor="w").pack(fill="x")
            tk.Label(col, text=desc, bg=row["bg"], fg=TEXT_DIM, font=self.f_small,
                     anchor="w", wraplength=panel_w - 100, justify="left").pack(fill="x")

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # EVIDENCE LOCKER (all-time discovered clues, grouped by case)
    # ==================================================================
    def load_evidence_log(self):
        if not os.path.exists(EVIDENCE_LOG_FILE):
            return []
        try:
            with open(EVIDENCE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def show_evidence_locker(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 32, text="EVIDENCE LOCKER", fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 58, text="Every clue you've ever uncovered, by case",
                                 fill=TEXT_LIGHT, font=self.f_body)

        panel_w, panel_h = min(w - 80, 760), min(h - 170, 400)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 80 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        canvas_scroll = tk.Canvas(panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=PANEL)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        log = self.load_evidence_log()
        if not log:
            tk.Label(inner, text="No evidence collected yet - investigate a case to fill your locker.",
                     bg=PANEL, fg=TEXT_DIM, font=self.f_body).pack(pady=20, padx=6, anchor="w")
        else:
            for case in cases:
                title = case["title"].strip()
                found = sorted({e["clue"] for e in log if e["case_title"] == title})
                if not found:
                    continue
                header = tk.Label(inner, text=f"\U0001F4C1 {title}  ({len(found)}/{len(case['clues'])})",
                                   bg=PANEL, fg=GOLD, font=self.f_body_b, anchor="w")
                header.pack(fill="x", pady=(8, 2), padx=4)
                for clue in found:
                    tk.Label(inner, text=f"  \u2022 {clue}", bg=PANEL, fg=TEXT_LIGHT,
                             font=self.f_small, anchor="w", wraplength=panel_w - 60,
                             justify="left").pack(fill="x", padx=10)

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 BACK TO TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=22).pack()

    # ==================================================================
    # SUSPECT DATABASE (browse-only reference - never reveals the killer)
    # ==================================================================
    def show_suspect_db_list(self):
        self.clear_screen()
        w, h = self.W(), self.H()
        self.set_background("menu_bg.png")

        self.canvas.create_text(w / 2, 34, text="SUSPECT DATABASE", fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 62, text="Browse suspect files for any case",
                                 fill=TEXT_LIGHT, font=self.f_body)

        grid = tk.Frame(self.root, bg=INK)
        self.add_widget(grid)
        self.canvas.create_window(w / 2, h * 0.52, window=grid)

        cols = 4 if w > 820 else 2
        for i, case in enumerate(cases):
            r, c = divmod(i, cols)
            b = self.styled_button(
                grid, case["title"].strip(), lambda idx=i: self.show_suspect_db_detail(idx),
                bg=PANEL_LIGHT, width=22, height=4, wraplength=150)
            b.grid(row=r, column=c, padx=6, pady=6)

        bottom = tk.Frame(self.root, bg=INK)
        self.add_widget(bottom)
        self.canvas.create_window(w / 2, h - 32, window=bottom)
        self.styled_button(bottom, "\u2B05 TITLE", self.show_title_screen,
                            bg=PANEL_LIGHT, width=16).pack()

    def show_suspect_db_detail(self, index):
        self.clear_screen()
        w, h = self.W(), self.H()
        case = cases[index]
        self.set_background(f"case{index + 1}_bg.png")

        self.canvas.create_rectangle(0, 0, w, 44, fill="#000000", outline="")
        self.canvas.create_text(w / 2, 22, text=case["title"].strip() + " - SUSPECT FILES",
                                 fill=GOLD, font=self.f_h2)

        panel_w, panel_h = min(w - 60, 900), min(h - 130, 460)
        panel = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(panel)
        self.canvas.create_window(w / 2, 55 + panel_h / 2, window=panel, width=panel_w, height=panel_h)

        canvas_scroll = tk.Canvas(panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=PANEL)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        for i, s in enumerate(case["suspects"]):
            occupation = s["name"].split()[0] if s["name"].split() else "Unknown"
            row = tk.Frame(inner, bg=PANEL_LIGHT, highlightbackground=GOLD_DIM, highlightthickness=1)
            row.pack(fill="x", pady=4, padx=4)

            av_file = f"avatar_{i % 8}.png"
            av_img = IMAGES.get(av_file)
            if av_img:
                try:
                    av_small = av_img.subsample(5, 5)
                except Exception:
                    av_small = av_img
                lbl_img = tk.Label(row, image=av_small, bg=PANEL_LIGHT)
                lbl_img.image = av_small
                lbl_img.pack(side="left", padx=8, pady=8)

            col = tk.Frame(row, bg=PANEL_LIGHT)
            col.pack(side="left", fill="x", expand=True, pady=6)
            tk.Label(col, text=f"{s['name']}   \u2022   Role: {occupation}", bg=PANEL_LIGHT, fg=GOLD_BRIGHT,
                     font=self.f_body_b, anchor="w").pack(fill="x")
            tk.Label(col, text=f"Background: {s['backstory']}", bg=PANEL_LIGHT, fg=TEXT_LIGHT,
                     font=self.f_small, anchor="w", wraplength=panel_w - 140, justify="left").pack(
                fill="x", pady=(2, 0))
            tk.Label(col, text=f"Alibi: \u201C{s['statement']}\u201D", bg=PANEL_LIGHT, fg=TEXT_DIM,
                     font=self.f_small, anchor="w", wraplength=panel_w - 140, justify="left").pack(
                fill="x", pady=(2, 6))

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 26, window=btn_frame)
        self.styled_button(btn_frame, "\u2B05 SUSPECT DATABASE", self.show_suspect_db_list,
                            bg=PANEL_LIGHT, width=24).pack()

    # ==================================================================
    # DETECTIVE PROFILE + ID CARD
    # ==================================================================
    def load_settings(self):
        defaults = {"difficulty": "Medium", "music_volume": 0.6, "sfx_volume": 0.8}
        if not os.path.exists(SETTINGS_FILE):
            return defaults
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            defaults.update(data)
            return defaults
        except Exception:
            return defaults

    def save_settings(self, settings):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass

    def _accumulate_play_time(self):
        """Adds elapsed session time to the profile's total play time."""
        profile = self.load_profile()
        if profile is None:
            return
        elapsed = int(time.time() - self._session_start)
        if elapsed <= 0:
            return
        profile["total_play_seconds"] = profile.get("total_play_seconds", 0) + elapsed
        self.save_profile(profile)
        self._session_start = time.time()

    def _on_close(self):
        try:
            self._accumulate_play_time()
        except Exception:
            pass
        try:
            self.sound.stop_ambient()
        except Exception:
            pass
        self.root.destroy()

    def load_profile(self):
        if not os.path.exists(PROFILE_FILE):
            return None
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_profile(self, profile):
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
        except Exception:
            pass

    def show_profile_creation(self):
        self.clear_screen()
        self.sound.start_ambient("ambient_murder.mp3")
        w, h = self.W(), self.H()
        self.set_background("title_bg.png")

        self.canvas.create_text(w / 2, 50, text="DETECTIVE REGISTRATION",
                                 fill=GOLD, font=self.f_title)
        self.canvas.create_text(w / 2, 80, text="Create your profile to receive your badge",
                                 fill=TEXT_LIGHT, font=self.f_body)

        form = tk.Frame(self.root, bg="#000000", highlightbackground=GOLD, highlightthickness=1)
        self.add_widget(form)
        self.canvas.create_window(w / 2, h * 0.54, window=form, width=min(w - 100, 460), height=340)

        def field(label, default=""):
            tk.Label(form, text=label, bg=PANEL, fg=GOLD_DIM, font=self.f_small,
                     anchor="w").pack(fill="x", padx=24, pady=(10, 0))
            var = tk.StringVar(value=default)
            entry = tk.Entry(form, textvariable=var, font=self.f_body, bg=PANEL_LIGHT,
                              fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, relief="flat")
            entry.pack(fill="x", padx=24, pady=(2, 0))
            return var

        name_var = field("DETECTIVE NAME", "")
        agency_var = field("AGENCY NAME", "Metro Investigation Bureau")

        tk.Label(form, text="DIFFICULTY", bg=PANEL, fg=GOLD_DIM, font=self.f_small,
                 anchor="w").pack(fill="x", padx=24, pady=(12, 2))
        diff_var = tk.StringVar(value="Medium")
        diff_row = tk.Frame(form, bg=PANEL)
        diff_row.pack(fill="x", padx=20)
        for level in ("Easy", "Medium", "Hard"):
            tk.Radiobutton(diff_row, text=level, variable=diff_var, value=level,
                            bg=PANEL, fg=TEXT_LIGHT, selectcolor=PANEL_LIGHT,
                            activebackground=PANEL, activeforeground=GOLD,
                            font=self.f_small).pack(side="left", padx=6)

        badge_number = str(random.randint(10000, 99999))

        def do_continue():
            name = name_var.get().strip() or "Unnamed Detective"
            agency = agency_var.get().strip() or "Metro Investigation Bureau"
            profile = {
                "name": name,
                "agency": agency,
                "badge": badge_number,
                "created": datetime.datetime.now().strftime("%Y-%m-%d"),
                "xp": 0,
                "total_play_seconds": 0,
            }
            self.save_profile(profile)
            self.save_settings({"difficulty": diff_var.get(),
                                 "music_volume": self.sound.music_volume,
                                 "sfx_volume": self.sound.sfx_volume})
            self.show_id_card(profile)

        self.styled_button(form, "ISSUE BADGE \u25B6", do_continue,
                            bg="#173a1f", width=22).pack(pady=18)

    def show_id_card(self, profile):
        self.clear_screen()
        w, h = self.W(), self.H()
        self.set_background("title_bg.png")

        self.canvas.create_text(w / 2, 50, text="DETECTIVE ID CARD", fill=GOLD, font=self.f_title)

        card = tk.Frame(self.root, bg=PANEL, highlightbackground=GOLD, highlightthickness=2)
        self.add_widget(card)
        self.canvas.create_window(w / 2, h * 0.5, window=card, width=min(w - 120, 440), height=280)

        level, rank, _, _ = self.xp_progress(profile.get("xp", 0))

        tk.Label(card, text="\U0001F396", bg=PANEL, fg=GOLD, font=("Helvetica", 36)).pack(pady=(16, 4))
        tk.Label(card, text=profile["name"], bg=PANEL, fg=TEXT_LIGHT, font=self.f_h1).pack()
        tk.Label(card, text=profile["agency"], bg=PANEL, fg=TEXT_DIM, font=self.f_small).pack(pady=(0, 8))
        tk.Label(card, text=f"BADGE No. {profile['badge']}", bg=PANEL, fg=GOLD_BRIGHT,
                 font=self.f_body_b).pack()
        tk.Label(card, text=f"LEVEL {level}  \u2022  RANK: {rank}", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_small).pack(pady=(2, 0))
        tk.Label(card, text=f"Issued {profile['created']}", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_small).pack(pady=(6, 10))

        btn_frame = tk.Frame(self.root, bg=INK)
        self.add_widget(btn_frame)
        self.canvas.create_window(w / 2, h - 60, window=btn_frame)
        self.styled_button(btn_frame, "\U0001F6AA ENTER HEADQUARTERS \u25B6", self.show_title_screen,
                            bg="#173a1f", width=28).pack()

    def xp_progress(self, xp):
        """Returns (level, rank_name, xp_into_level, xp_needed_for_next_level)."""
        per_level = 100
        level = xp // per_level + 1
        into_level = xp % per_level
        rank_ladder = [
            "TRAINEE", "OFFICER", "JUNIOR DETECTIVE", "DETECTIVE",
            "SENIOR DETECTIVE", "INSPECTOR", "CHIEF INSPECTOR", "LEGEND DETECTIVE",
        ]
        idx = min(level - 1, len(rank_ladder) - 1)
        rank = rank_ladder[idx]
        return level, rank, into_level, per_level

    def award_xp(self, amount):
        profile = self.load_profile()
        if profile is None:
            return
        profile["xp"] = profile.get("xp", 0) + max(0, int(amount))
        self.save_profile(profile)

    # ==================================================================
    # POPUP (in-canvas styled dialog)
    # ==================================================================
    def show_popup(self, title, message, accent=GOLD):
        overlay = tk.Toplevel(self.root)
        overlay.title(title)
        overlay.configure(bg=PANEL)
        overlay.resizable(False, False)
        overlay.transient(self.root)
        overlay.grab_set()

        pw, ph = 400, 200
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - pw) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        overlay.geometry(f"{pw}x{ph}+{max(0, x)}+{max(0, y)}")

        tk.Frame(overlay, bg=accent, height=4).pack(fill="x")
        tk.Label(overlay, text=title, bg=PANEL, fg=accent, font=self.f_h2).pack(pady=(14, 6))
        tk.Label(overlay, text=message, bg=PANEL, fg=TEXT_LIGHT, font=self.f_body,
                 wraplength=350, justify="center").pack(padx=18, pady=5, expand=True)

        tk.Button(overlay, text="OK", command=overlay.destroy,
                  bg=PANEL_LIGHT, fg=GOLD, font=self.f_button, relief="flat",
                  width=11, cursor="hand2").pack(pady=12)

        overlay.bind("<Return>", lambda e: overlay.destroy())
        overlay.focus_set()

    def show_confirm_popup(self, title, message, on_confirm, accent=RED,
                            confirm_label="YES, CONTINUE", cancel_label="CANCEL"):
        """A Yes/No styled dialog, used before destructive actions."""
        overlay = tk.Toplevel(self.root)
        overlay.title(title)
        overlay.configure(bg=PANEL)
        overlay.resizable(False, False)
        overlay.transient(self.root)
        overlay.grab_set()

        pw, ph = 440, 230
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - pw) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        overlay.geometry(f"{pw}x{ph}+{max(0, x)}+{max(0, y)}")

        tk.Frame(overlay, bg=accent, height=4).pack(fill="x")
        tk.Label(overlay, text=title, bg=PANEL, fg=accent, font=self.f_h2).pack(pady=(14, 6))
        tk.Label(overlay, text=message, bg=PANEL, fg=TEXT_LIGHT, font=self.f_body,
                 wraplength=390, justify="center").pack(padx=18, pady=5, expand=True)

        btn_row = tk.Frame(overlay, bg=PANEL)
        btn_row.pack(pady=14)

        def do_confirm():
            overlay.destroy()
            on_confirm()

        tk.Button(btn_row, text=cancel_label, command=overlay.destroy,
                  bg=PANEL_LIGHT, fg=TEXT_LIGHT, font=self.f_button, relief="flat",
                  width=13, cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn_row, text=confirm_label, command=do_confirm,
                  bg=accent, fg="#ffffff",
                  font=self.f_button, relief="flat", width=17, cursor="hand2").pack(side="left", padx=8)

        overlay.bind("<Escape>", lambda e: overlay.destroy())
        overlay.focus_set()

    # ==================================================================
    # RESTART GAME (wipes ALL saved data: profile, records, achievements...)
    # ==================================================================
    def confirm_restart_game(self):
        self.show_confirm_popup(
            "\u26A0 RESTART GAME - ERASE ALL DATA",
            "This will permanently delete your detective profile, saved game, "
            "player records, case history, achievements, evidence locker, and "
            "settings, and start completely fresh.\n\nThis cannot be undone. Are you sure?",
            self.restart_all_data,
            accent=RED_BRIGHT,
            confirm_label="\U0001F5D1 ERASE EVERYTHING",
        )

    def restart_all_data(self):
        """Deletes every persistent data file and returns to a brand-new game."""
        self.sound.stop_ambient()
        data_files = [
            SAVE_FILE, RECORDS_FILE, CASE_RECORDS_FILE, PROFILE_FILE,
            ACHIEVEMENTS_FILE, EVIDENCE_LOG_FILE, SETTINGS_FILE,
        ]
        errors = []
        for f in data_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                errors.append(f"{os.path.basename(f)}: {e}")

        # reset all in-memory session state back to defaults
        self.case_index = 0
        self.score = 0
        self.solved_cases = []
        self.evidence = []
        self.selected_suspect = None
        self.interrogated = set()
        self.difficulty = "Medium"
        self.sound.set_music_volume(0.6)
        self.sound.set_sfx_volume(0.8)
        self._session_start = time.time()
        self._case_start_time = None

        if errors:
            self.show_popup("\u26A0 PARTIAL RESET", "Some files could not be deleted:\n" + "\n".join(errors),
                             accent=RED)
        # profile is gone, so send the player back through registration
        self.show_profile_creation()

    # ==================================================================
    # SAVE / LOAD
    # ==================================================================
    def save_game(self):
        data = {
            "case_index": self.case_index,
            "score": self.score,
            "solved_cases": self.solved_cases,
            "evidence": self.evidence,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.sound.play("notification.wav")
            self.show_popup("\U0001F4BE GAME SAVED", "Your progress has been saved successfully.",
                             accent=GREEN)
        except Exception as e:
            self.show_popup("\u26A0 SAVE FAILED", str(e), accent=RED)

    def auto_save(self):
        """Silent save (no popup) used after clue discovery, interrogation, and accusation."""
        data = {
            "case_index": self.case_index,
            "score": self.score,
            "solved_cases": self.solved_cases,
            "evidence": self.evidence,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
        try:
            self._accumulate_play_time()
        except Exception:
            pass

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            self.show_popup("\u26A0 NO SAVE FOUND",
                             "There is no saved game yet. Start a new investigation first.",
                             accent=RED)
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.case_index = data.get("case_index", 0)
            self.score = data.get("score", 0)
            self.solved_cases = data.get("solved_cases", [])
            self.evidence = data.get("evidence", [])
            self.max_clues = len(cases[self.case_index]["clues"])
            self.selected_suspect = None
            self.interrogated = set()
            self.show_investigation()
            self.show_popup("\U0001F4C2 GAME LOADED", "Your saved progress has been restored.",
                             accent=GREEN)
        except Exception as e:
            self.show_popup("\u26A0 LOAD FAILED", str(e), accent=RED)


# ==========================================================================
# ENTRY POINT
# ==========================================================================
def main():
    root = tk.Tk()
    try:
        icon = IMAGES.get("icon_badge.png")
        if icon:
            root.iconphoto(False, icon)
    except Exception:
        pass
    app = DetectiveApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
