import pygame # type: ignore

from settings import (
    MUSIC_MENU,
    MUSIC_BATTLE,
    MUSIC_EXPLORATION,
    SFX_ATTACK,
    SFX_HIT,
    SFX_HEAL,
    SFX_INFECTION,
    SFX_ITEM_PICKUP,
    SFX_VICTORY,
    SFX_DEFEAT,
    SFX_FLEE,
    SFX_SAVE,
    SFX_LOAD,
    MUSIC_VOLUME,
    SFX_VOLUME,
)


class SoundManager:
    def __init__(self):
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error as e:
                print(f"Sound system init failed: {e}")
                self._enabled = False
                return

        self._enabled = True
        self._current_music = None
        self._music_volume = MUSIC_VOLUME
        self._sfx_volume = SFX_VOLUME

        # Load all SFX
        self._sfx = {}
        sfx_files = {
            "attack": SFX_ATTACK,
            "hit": SFX_HIT,
            "heal": SFX_HEAL,
            "infection": SFX_INFECTION,
            "item_pickup": SFX_ITEM_PICKUP,
            "victory": SFX_VICTORY,
            "defeat": SFX_DEFEAT,
            "flee": SFX_FLEE,
            "save": SFX_SAVE,
            "load": SFX_LOAD,
        }

        for name, path in sfx_files.items():
            self._sfx[name] = self._load_sfx(path)

    def _load_sfx(self, path):
        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(self._sfx_volume)
            return sound
        except (pygame.error, FileNotFoundError):
            return None

    def _load_music(self, path):
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(loops=-1, fade_ms=1500)
            return True
        except (pygame.error, FileNotFoundError):
            return False

    def play_music(self, music_key):
        if not self._enabled:
            return

        music_map = {
            "menu": MUSIC_MENU,
            "battle": MUSIC_BATTLE,
            "exploration": MUSIC_EXPLORATION,
        }

        if music_key == self._current_music:
            return

        path = music_map.get(music_key)
        if path is None:
            return

        pygame.mixer.music.fadeout(800)
        success = self._load_music(path)
        if success:
            self._current_music = music_key

    def stop_music(self):
        if not self._enabled:
            return
        pygame.mixer.music.fadeout(800)
        self._current_music = None

    def play_sfx(self, name):
        if not self._enabled:
            return
        sound = self._sfx.get(name)
        if sound is not None:
            sound.play()

    def set_music_volume(self, volume):
        self._music_volume = max(0.0, min(1.0, volume))
        if self._enabled:
            pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)."""
        self._sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sfx.values():
            if sound is not None:
                sound.set_volume(self._sfx_volume)

    def is_enabled(self):
        return self._enabled