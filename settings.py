from pathlib import Path
import pygame # type: ignore

# Window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
GAME_TITLE = "Quarantine Zone"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (40, 40, 40)

RED = (180, 50, 50)
GREEN = (60, 180, 90)
BLUE = (70, 120, 200)
YELLOW = (220, 200, 80)

BACKGROUND_COLOR = (18, 18, 22)
PANEL_COLOR = (28, 28, 34)
PANEL_BORDER_COLOR = (80, 80, 95)
TEXT_COLOR = (230, 230, 235)
ACCENT_COLOR = (130, 180, 255)

# States
STATE_MENU = "menu"
STATE_EXPLORATION = "exploration"

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

ITEMS_FILE = DATA_DIR / "items.json"
RECIPES_FILE = DATA_DIR / "recipes.json"
ENEMIES_FILE = DATA_DIR / "enemies.json"
LOCATIONS_FILE = DATA_DIR / "locations.json"

# Fonts
TITLE_FONT_SIZE = 48
HEADER_FONT_SIZE = 30
TEXT_FONT_SIZE = 24
SMALL_FONT_SIZE = 20

# Layout
PADDING = 20
LEFT_PANEL_WIDTH = 760
RIGHT_PANEL_WIDTH = 460
TOP_PANEL_HEIGHT = 380
BOTTOM_PANEL_HEIGHT = 280

# Battle states
STATE_BATTLE = "battle"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

# Battle sub-states
BATTLE_PLAYER_TURN = "player_turn"
BATTLE_ENEMY_TURN = "enemy_turn"
BATTLE_RESULT = "result"

# Battle layout
BATTLE_ENEMY_AREA_HEIGHT = 280
BATTLE_MENU_HEIGHT = 380

# Battle sub-states (extended)
BATTLE_QTE = "qte"
BATTLE_REACTION = "reaction"

# QTE settings
QTE_BAR_WIDTH = 600
QTE_BAR_HEIGHT = 40
QTE_MARKER_WIDTH = 6
QTE_MARKER_SPEED = 10  # pixels per frame
QTE_GREEN_ZONE_WIDTH = 55
QTE_YELLOW_ZONE_WIDTH = 60

# Mutation skill thresholds and multipliers
INFECTED_STRIKE_THRESHOLD = 35
INFECTED_STRIKE_MULTIPLIER = 1.4
INFECTED_STRIKE_COST = 5

MUTANT_BURST_THRESHOLD = 60
MUTANT_BURST_MULTIPLIER = 1.8
MUTANT_BURST_COST = 10

# Inventory & Crafting states
STATE_INVENTORY = "inventory"
STATE_CRAFTING = "crafting"

# Escape rules
MAX_ESCAPE_ATTEMPTS = 3
ESCAPE_PENALTY_PER_ATTEMPT = 20
LOW_HP_THRESHOLD_PERCENT = 30
LOW_HP_ESCAPE_PENALTY = 15


# Save & Load
STATE_PAUSE = "pause"
SAVES_DIR = DATA_DIR / "saves"
SAVE_FILE_1 = SAVES_DIR / "save1.json"
SAVE_FILE_2 = SAVES_DIR / "save2.json"

PAUSE_OPTIONS = [
    ("continue", "Continue"),
    ("save1", "Save to Slot 1"),
    ("load1", "Load Slot 1"),
    ("save2", "Save to Slot 2"),
    ("load2", "Load Slot 2"),
    ("main_menu", "Main Menu"),
    ("quit_game", "Quit Game"),
]

# Quick Save/Load Keys
QUICK_SAVE_KEY = pygame.K_F5
QUICK_LOAD_KEY = pygame.K_F9

# Sound settings
SOUNDS_DIR = ASSETS_DIR / "sounds"

MUSIC_MENU = SOUNDS_DIR / "music_menu.ogg"
MUSIC_BATTLE = SOUNDS_DIR / "music_battle.ogg"
MUSIC_EXPLORATION = SOUNDS_DIR / "music_exploration.ogg"

SFX_ATTACK = SOUNDS_DIR / "sfx_attack.ogg"
SFX_HIT = SOUNDS_DIR / "sfx_hit.ogg"
SFX_HEAL = SOUNDS_DIR / "sfx_heal.ogg"
SFX_INFECTION = SOUNDS_DIR / "sfx_infection.ogg"
SFX_ITEM_PICKUP = SOUNDS_DIR / "sfx_item_pickup.ogg"
SFX_VICTORY = SOUNDS_DIR / "sfx_victory.ogg"
SFX_DEFEAT = SOUNDS_DIR / "sfx_defeat.ogg"
SFX_FLEE = SOUNDS_DIR / "sfx_flee.ogg"
SFX_SAVE = SOUNDS_DIR / "sfx_save.ogg"
SFX_LOAD = SOUNDS_DIR / "sfx_load.ogg"

MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Notes (story fragments)
NOTES_FILE = DATA_DIR / "notes.json"
STATE_NOTES = "notes"

# Note viewing states
STATE_NOTE_VIEW = "note_view"
STATE_NOTES_LIST = "notes_list"

# Search QTE
SEARCH_QTE_BAR_WIDTH = 500
SEARCH_QTE_BAR_HEIGHT = 35
SEARCH_QTE_MARKER_SPEED = 12
SEARCH_QTE_GREEN_WIDTH = 80
SEARCH_QTE_YELLOW_WIDTH = 70

# Search QTE states
STATE_SEARCH_QTE = "search_qte"

# Map settings
STATE_MAP = "map"
MAP_NODE_RADIUS = 18
MAP_NODE_RADIUS_CURRENT = 22
MAP_CONNECTION_WIDTH = 2

STATE_MAP = "map"

# .exe build
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

if getattr(sys, "frozen", False):
    # Run from .exe
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Normal launch
    BASE_DIR = Path(__file__).resolve().parent

DATA_DIR   = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
SAVES_DIR  = DATA_DIR / "saves"

STATE_NOTE_VIEW = "note_view"
STATE_NOTES_LIST = "notes_list"
NOTE_VIEW_STATE = "note_view"
NOTES_LIST_STATE = "notes_list"