import pygame
import os
import random

from settings import MUSIC_VOLUME, SOUND_VOLUME


class SoundManager:

    def __init__(self):

        try:
            pygame.mixer.init()

            self.sound_enabled = True
            self.muted = False

            self.base_volume = SOUND_VOLUME

            # ====== Sound Folder ======
            sound_path = os.path.join(os.path.dirname(__file__), "sound")

            # Background Music
            self.music = os.path.join(sound_path, "background.mp3")

            # Effects
            self.click_sound = self.load_sound(
                os.path.join(sound_path, "click.mp3")
            )

            self.pop_sound = self.load_sound(
                os.path.join(sound_path, "pop.mp3")
            )

            self.explosion_sound = self.load_sound(
                os.path.join(sound_path, "another.mp3")
            )

            self.bomb_sound = self.load_sound(
                os.path.join(sound_path, "another.mp3")
            )

            self.rainbow_sound = self.load_sound(
                os.path.join(sound_path, "another.mp3")
            )

            # Preloaded once instead of re-reading from disk every call
            self.win_sound = self.load_sound(
                os.path.join(sound_path, "win.mp3")
            )

            self.wand_sound = self.load_sound(
                os.path.join(sound_path, "another.mp3")
            )

            self.nice_sound = self.load_sound(
                os.path.join(sound_path, "win.mp3")
            )

            self.set_effect_volume(self.base_volume)

        except:

            self.sound_enabled = False

    # ====================================
    # Load Sound Safely
    # ====================================

    def load_sound(self, sound):

        try:

            if os.path.exists(sound):

                return pygame.mixer.Sound(sound)

        except:

            pass

        return None

    # ====================================
    # Play a sound with a bit of natural volume variance
    # so repeated effects feel less robotic / more alive
    # ====================================

    def _play_varied(self, sound, base=None, fade_ms=0, maxtime=0):

        if self.muted or not sound:
            return

        base = self.base_volume if base is None else base

        variance = random.uniform(0.82, 1.0)

        sound.set_volume(max(0.0, min(1.0, base * variance)))

        sound.play(fade_ms=fade_ms, maxtime=maxtime)

    # ====================================
    # Background Music
    # ====================================

    def play_background(self):

        if not self.sound_enabled:
            return

        try:

            if os.path.exists(self.music):

                pygame.mixer.music.load(self.music)

                pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)

                # Gentle fade-in feels nicer than an abrupt start
                pygame.mixer.music.play(-1, fade_ms=1200)

        except:

            pass

    def stop_background(self):

        if self.sound_enabled:

            pygame.mixer.music.stop()

    # ====================================
    # Effects
    # ====================================

    def play_click(self):

        self._play_varied(self.click_sound)

    def play_pop(self):

        self._play_varied(self.pop_sound)

    def play_explosion(self):

        self._play_varied(self.explosion_sound)

    def play_bomb(self):

        self._play_varied(self.bomb_sound)

    def play_rainbow(self):

        self._play_varied(self.rainbow_sound)

    def play_win(self):

        self._play_varied(self.win_sound, base=1.0, fade_ms=250)

    def play_shuffle(self):

        self._play_varied(self.click_sound)

    def play_wand(self):

        # A punchier, louder cue for the portal's appearance - capped with
        # maxtime so it only plays for that opening moment, not the whole
        # 3-second magic animation
        self._play_varied(self.wand_sound, base=1.0, fade_ms=120, maxtime=900)

    def play_nice(self):

        # Softer celebratory sting for a nice/awesome big pop
        self._play_varied(self.nice_sound, base=0.55, fade_ms=150)

    # ====================================
    # Volume
    # ====================================

    def set_music_volume(self, volume):

        pygame.mixer.music.set_volume(volume)

    def set_effect_volume(self, volume):

        self.base_volume = volume

        sounds = [

            self.click_sound,
            self.pop_sound,
            self.explosion_sound,
            self.bomb_sound,
            self.rainbow_sound,
            self.win_sound,
            self.wand_sound,
            self.nice_sound

        ]

        for sound in sounds:

            if sound:

                sound.set_volume(volume)

    def toggle_mute(self):
        if not self.sound_enabled:
            return False
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.pause()
            pygame.mixer.stop()
            self.set_effect_volume(0)
        else:
            pygame.mixer.music.unpause()
            self.set_effect_volume(SOUND_VOLUME)
        return self.muted
