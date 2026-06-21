"""
game.py
Main game controller — state machine, event loop, coordination.
"""
import json
import sys
import pygame # type: ignore

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, GAME_TITLE,
    STATE_MENU, STATE_EXPLORATION, STATE_BATTLE,
    STATE_GAME_OVER, STATE_VICTORY, STATE_INVENTORY,
    STATE_CRAFTING, STATE_PAUSE, STATE_MAP,
    STATE_NOTE_VIEW, STATE_NOTES_LIST,
    BATTLE_PLAYER_TURN, BATTLE_QTE, BATTLE_REACTION, BATTLE_RESULT,
    ITEMS_FILE, RECIPES_FILE, ENEMIES_FILE, LOCATIONS_FILE, NOTES_FILE,
    SAVE_FILE_1, SAVE_FILE_2, PAUSE_OPTIONS, QUICK_SAVE_KEY, QUICK_LOAD_KEY,
    BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR, WHITE, YELLOW, TITLE_FONT_SIZE, HEADER_FONT_SIZE, TEXT_FONT_SIZE, SMALL_FONT_SIZE,
    PADDING,
)

# ── Imports ─────────────────────
from src.screens.menu_renderer import MenuRenderer
from src.screens.pause_renderer import PauseRenderer
from src.screens.note_renderer import NoteRenderer
from src.screens.exploration_renderer import ExplorationRenderer
from src.screens.battle_renderer import BattleRenderer

from src.player import Player
from src.save_manager import SaveManager
from src.sound_manager import SoundManager

# Screens
from src.screens.map_screen import MapScreen
from src.screens.ui_renderer import UIRenderer
from src.inventory_screen import InventoryScreen  
from src.crafting_screen import CraftingScreen    

# Systems
from src.systems.battle_system import BattleSystem
from src.systems.exploration_system import ExplorationSystem
from src.systems.note_system import NoteSystem

GRAY_DISABLED = (110, 110, 120)
MESSAGE_LIFETIME_MS = 9000


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Renderers
        self.menu_renderer = MenuRenderer(self)
        self.pause_renderer = PauseRenderer(self)
        self.note_renderer = NoteRenderer(self)
        self.exploration_renderer = ExplorationRenderer(self)
        self.battle_renderer = BattleRenderer(self)

        self.running = True
        self.state = STATE_MENU
        self.previous_state = None
        self._notes_origin = STATE_EXPLORATION
        self._transitioning_state = False

        # Fonts
        self.title_font  = pygame.font.SysFont("arial", TITLE_FONT_SIZE,  bold=True)
        self.header_font = pygame.font.SysFont("arial", HEADER_FONT_SIZE, bold=True)
        self.text_font   = pygame.font.SysFont("arial", TEXT_FONT_SIZE)
        self.small_font  = pygame.font.SysFont("arial", SMALL_FONT_SIZE)

        # Data
        self.data = self._load_all_data()
        self.locations_by_id = {l["id"]: l for l in self.data["locations"]}  # noqa: E741
        self.items_by_id     = {i["id"]: i for i in self.data["items"]}
        self.enemies_by_id   = {e["id"]: e for e in self.data["enemies"]}
        self.notes_by_id     = {n["id"]: n for n in self.data["notes"]}

        # Player & enemy
        self.player = None
        self.current_enemy = None
        self.is_story_battle = False

        # Battle state
        self.battle_sub_state  = None
        self.battle_log        = []
        self.battle_result     = None
        self.battle_item_mode  = False
        self.battle_skill_mode = False
        self.battle_consumables = []

        # QTE state
        self.qte_marker_x    = 0
        self.qte_direction   = 1
        self.qte_green_start = 0
        self.qte_green_end   = 0
        self.qte_yellow_start = 0
        self.qte_yellow_end  = 0
        self.qte_bar_x       = 0
        self.qte_bar_y       = 0
        self.qte_skill       = "normal"

        # Search QTE state
        self.search_qte_active    = False
        self.search_qte_marker_x  = 0
        self.search_qte_direction = 1
        self.search_qte_bar_x     = 0
        self.search_qte_bar_y     = 0
        self.search_qte_green_start  = 0
        self.search_qte_green_end    = 0
        self.search_qte_yellow_start = 0
        self.search_qte_yellow_end   = 0
        self.search_qte_location  = None

        # Notes state
        self.viewing_note     = None
        self.notes_list_index = 0

        # Message bar
        self.message_text = ""
        self.message_time = 0

        # Pause
        self.pause_selected_index = 0

        # Systems
        self.battle_system      = BattleSystem(self)
        self.exploration_system = ExplorationSystem(self)
        self.note_system        = NoteSystem(self)
        self.ui_renderer        = UIRenderer(self)

        # Screens
        self.inventory_screen = InventoryScreen(self)
        self.crafting_screen  = CraftingScreen(self)
        self.map_screen       = MapScreen(self)

        # Services
        self.save_manager  = SaveManager()
        self.sound_manager = SoundManager()

        self.sound_manager.play_music("menu")

    # ── Data ──────────────────────────────────────────────────

    def _load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[DATA] Error loading {path}: {e}")
            return {}

    def _load_all_data(self):
        return {
            "items":     self._load_json(ITEMS_FILE).get("items", []),
            "recipes":   self._load_json(RECIPES_FILE).get("recipes", []),
            "enemies":   self._load_json(ENEMIES_FILE).get("enemies", []),
            "locations": self._load_json(LOCATIONS_FILE).get("locations", []),
            "notes":     self._load_json(NOTES_FILE).get("notes", []),
        }

    # ── Helpers ───────────────────────────────────────────────

    def get_current_location(self):
        if self.player is None:
            return None
        return self.locations_by_id.get(self.player.current_location_id)

    def get_item_name(self, item_id):
        item = self.items_by_id.get(item_id)
        return item.get("name", item_id) if item else item_id

    def set_message(self, text):
        self.message_text = text
        self.message_time = pygame.time.get_ticks()

    def roll_loot(self, loot_table):
        if not loot_table:
            return None
        total = sum(e.get("chance", 0) for e in loot_table)
        if total <= 0:
            return None
        import random
        roll = random.randint(1, total)
        cumulative = 0
        for entry in loot_table:
            cumulative += entry.get("chance", 0)
            if roll <= cumulative:
                return entry
        return None


    # ── Notes (delegated) ─────────────────────────────────────

    def show_note(self, note):
        self.note_system.show_note(note)

    def open_notes_list(self):
        self.note_system.open_notes_list()

    def try_find_note(self, location_id):
        return self.note_system.try_find_note(location_id)

    # ── Exploration (delegated) ───────────────────────────────

    def check_requirements(self, requirements):
        return self.exploration_system.check_requirements(requirements)

    def get_available_special_actions(self, location):
        return self.exploration_system.get_available_special_actions(location)

    def try_move_to(self, connection):
        self.exploration_system.try_move_to(connection)

    def try_perform_action(self, action):
        self.exploration_system.try_perform_action(action)

    def try_search_location(self, location):
        self.exploration_system.try_search_location(location)

    def start_random_encounter(self, encounter_table):
        self.exploration_system.start_random_encounter(encounter_table)

    # ── Battle (delegated) ────────────────────────────────────

    def start_battle(self, enemy_data, is_story_battle=False):
        self.battle_system.start_battle(enemy_data, is_story_battle)

    def get_current_escape_chance(self):
        return self.battle_system.get_escape_chance()

    # ── Game flow ─────────────────────────────────────────────

    def start_new_game(self):
        self.player = Player(name="Survivor", start_location_id="police_station")
        self.player.add_item("bandage", 2)
        self.player.add_item("cloth", 2)
        self.current_enemy = None
        self.state = STATE_EXPLORATION
        self.sound_manager.play_music("exploration")
        self.set_message("You wake up in the police station. Find a way out.")

    # ── Main loop ─────────────────────────────────────────────

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key):
        if key == QUICK_SAVE_KEY:
            if self.state not in (STATE_MENU, STATE_GAME_OVER, STATE_VICTORY):
                if self.player:
                    ok = self.save_manager.save_game(
                        self.player, self.current_enemy, SAVE_FILE_1
                    )
                    self.set_message(
                        "Quick Saved to Slot 1." if ok else "Save failed!"
                    )
            return

        if key == QUICK_LOAD_KEY:
            if self.state not in (STATE_GAME_OVER, STATE_VICTORY):
                self._do_load(SAVE_FILE_1, 1, from_menu=(self.state == STATE_MENU))
            return

        dispatch = {
            STATE_MENU:        self.handle_menu_input,
            STATE_EXPLORATION: self.handle_exploration_input,
            STATE_BATTLE:      self.handle_battle_input,
            STATE_INVENTORY:   self.handle_inventory_input,
            STATE_CRAFTING:    self.handle_crafting_input,
            STATE_PAUSE:       self.handle_pause_input,
            STATE_MAP:         self.handle_map_input,
            STATE_NOTE_VIEW:   self.note_system.handle_note_view_input,
            STATE_NOTES_LIST:  self.note_system.handle_notes_list_input,
        }

        handler = dispatch.get(self.state)
        if handler:
            handler(key)
        elif self.state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.state = STATE_MENU
        elif self.state == STATE_VICTORY:
            if key == pygame.K_RETURN:
                self.state = STATE_MENU

    def update(self):
        if self.state == STATE_BATTLE and self.battle_sub_state == BATTLE_QTE:
            self.battle_system.update_qte()
        if self.state == STATE_EXPLORATION and self.search_qte_active:
            self.exploration_system.update_search_qte()

    # ── Input handlers ────────────────────────────────────────

    def handle_menu_input(self, key):
        if key == pygame.K_RETURN or key == pygame.K_1:
            self.start_new_game()
        elif key == pygame.K_2:
            self._do_load(SAVE_FILE_1, 1, from_menu=True)
        elif key == pygame.K_3:
            self._do_load(SAVE_FILE_2, 2, from_menu=True)
        elif key == pygame.K_ESCAPE:
            self.running = False

    def handle_exploration_input(self, key):
        if self._transitioning_state:
            self._transitioning_state = False
            return

        if self.search_qte_active:
            if key == pygame.K_SPACE:
                self.exploration_system.resolve_search_qte()
            return

        if key == pygame.K_ESCAPE:
            self.open_pause()
            return
        if key == pygame.K_i:
            self.open_inventory()
            return
        if key == pygame.K_c:
            self.open_crafting()
            return
        if key == pygame.K_n:
            self.note_system.open_notes_list()
            return
        if key == pygame.K_m:
            self.open_map()
            return

        location = self.get_current_location()
        if location is None:
            return

        connections = location.get("connections", [])
        special = self.exploration_system.get_available_special_actions(location)

        number_keys = [
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
            pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
        ]
        letter_keys = [
            pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
            pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_o,
        ]

        if key == pygame.K_s:
            self.exploration_system.try_search_location(location)
            return

        for i, k in enumerate(number_keys):
            if key == k and i < len(connections):
                self.exploration_system.try_move_to(connections[i])
                return

        for i, k in enumerate(letter_keys):
            if key == k and i < len(special):
                self.exploration_system.try_perform_action(special[i])
                return

    def handle_battle_input(self, key):
        if key == pygame.K_ESCAPE:
            if self.battle_item_mode:
                self.battle_item_mode = False; return  # noqa: E702
            if self.battle_skill_mode:
                self.battle_skill_mode = False; return  # noqa: E702
            if self.battle_sub_state not in (BATTLE_QTE, BATTLE_REACTION, BATTLE_RESULT):
                self.open_pause()
            return

        if self.battle_sub_state == BATTLE_RESULT:
            if key == pygame.K_RETURN:
                self.battle_system.end_battle()
            return

        if self.battle_sub_state == BATTLE_QTE:
            if key == pygame.K_SPACE:
                self.battle_system.resolve_qte()
            return

        if self.battle_sub_state == BATTLE_REACTION:
            if key == pygame.K_1:
                self.battle_system.resolve_reaction("dodge")
            elif key == pygame.K_2:
                self.battle_system.resolve_reaction("block")
            elif key == pygame.K_3:
                self.battle_system.resolve_reaction("counter")
            return

        if self.battle_item_mode:
            number_keys = [
                pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
            ]
            for i, k in enumerate(number_keys):
                if key == k and i < len(self.battle_consumables):
                    self.battle_system.use_battle_item(i)
                    return
            return

        if self.battle_skill_mode:
            self.battle_system.handle_battle_skill_input(key)
            return

        if self.battle_sub_state == BATTLE_PLAYER_TURN:
            if key == pygame.K_1:
                self.battle_system.start_qte("normal")
            elif key == pygame.K_2:
                self.battle_system.open_battle_items()
            elif key == pygame.K_3:
                self.battle_system.open_battle_skills()
            elif key == pygame.K_4:
                self.battle_system.player_flee()

    def handle_inventory_input(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_i):
            self._transitioning_state = True
            self.state = self.previous_state or STATE_EXPLORATION

    def handle_crafting_input(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_c):
            self._transitioning_state = True
            self.state = self.previous_state or STATE_EXPLORATION
            return
        if key == pygame.K_UP:
            self.crafting_screen.select_prev()
        elif key == pygame.K_DOWN:
            self.crafting_screen.select_next()
        elif key == pygame.K_RETURN:
            self.crafting_screen.craft_selected()

    def handle_map_input(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_m):
            self._transitioning_state = True
            self.state = self.previous_state or STATE_EXPLORATION

    def handle_pause_input(self, key):
        n = len(PAUSE_OPTIONS)
        if key in (pygame.K_ESCAPE, pygame.K_i, pygame.K_c):
            self.state = self.previous_state or STATE_EXPLORATION
            return
        if key == pygame.K_UP:
            self.pause_selected_index = (self.pause_selected_index - 1) % n
        elif key == pygame.K_DOWN:
            self.pause_selected_index = (self.pause_selected_index + 1) % n
        elif key == pygame.K_RETURN:
            self._execute_pause_option(PAUSE_OPTIONS[self.pause_selected_index][0])

    # ── Pause logic ───────────────────────────────────────────

    def open_pause(self):
        self.previous_state = self.state
        self.pause_selected_index = 0
        self.state = STATE_PAUSE

    def open_inventory(self):
        self.previous_state = self.state
        self.state = STATE_INVENTORY

    def open_crafting(self):
        self.previous_state = self.state
        self.crafting_screen.reset()
        self.state = STATE_CRAFTING

    def open_map(self):
        self.previous_state = self.state
        self.state = STATE_MAP

    def _execute_pause_option(self, key):
        if key == "continue":
            self.state = self.previous_state or STATE_EXPLORATION
        elif key == "save1":
            self._do_save(SAVE_FILE_1, 1)
        elif key == "load1":
            self._do_load(SAVE_FILE_1, 1)
        elif key == "save2":
            self._do_save(SAVE_FILE_2, 2)
        elif key == "load2":
            self._do_load(SAVE_FILE_2, 2)
        elif key == "main_menu":
            self.state = STATE_MENU
            self.sound_manager.play_music("menu")
        elif key == "quit_game":
            self.running = False

    def _do_save(self, save_file, slot):
        if self.player:
            ok = self.save_manager.save_game(
                self.player, self.current_enemy, save_file
            )
            self.set_message(f"Saved to Slot {slot}." if ok else "Save failed!")
            if ok:
                self.sound_manager.play_sfx("save")
        self.state = self.previous_state or STATE_EXPLORATION

    def _do_load(self, save_file, slot, from_menu=False):
        if not self.save_manager.save_exists(save_file):
            self.set_message(f"No save found in Slot {slot}!")
            if from_menu:
                self.state = STATE_MENU
            return

        if self.player is None:
            self.player = Player("Survivor", "police_station")

        valid_locs = set(self.locations_by_id.keys())
        loaded_enemy, ok = self.save_manager.load_game(
            self.player, self.enemies_by_id, save_file, valid_locs
        )

        if not ok:
            self.set_message(f"Save file in Slot {slot} is corrupted!")
            return

        self.battle_item_mode = False
        self.battle_skill_mode = False
        self.battle_log = []
        self.battle_result = None

        if loaded_enemy is not None:
            self.current_enemy = loaded_enemy
            self.battle_sub_state = BATTLE_PLAYER_TURN
            self.battle_log = [
                (f"Restored battle with {loaded_enemy.name}.", (130, 180, 255)),
                ("Your turn.", (220, 220, 225)),
            ]
            self.state = STATE_BATTLE
            self.sound_manager.play_music("battle")
        else:
            self.current_enemy = None
            self.state = STATE_EXPLORATION
            self.sound_manager.play_music("exploration")

        self.set_message(f"Loaded Slot {slot}.")
        self.sound_manager.play_sfx("load")

    # ─── Drawing ──────────────────────────────────────────────

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.state == STATE_MENU:
            self.menu_renderer.draw_menu()
        elif self.state == STATE_EXPLORATION:
            self.exploration_renderer.draw_exploration()
        elif self.state == STATE_BATTLE:
            self.battle_renderer.draw_battle()
        elif self.state == STATE_INVENTORY:
            self.inventory_screen.draw()
        elif self.state == STATE_CRAFTING:
            self.crafting_screen.draw()
        elif self.state == STATE_PAUSE:
            self.pause_renderer.draw_pause()
        elif self.state == STATE_GAME_OVER:
            self.menu_renderer.draw_game_over()
        elif self.state == STATE_VICTORY:
            self.menu_renderer.draw_victory()
        elif self.state == STATE_NOTE_VIEW:
            self.note_renderer.draw_note_view()
        elif self.state == STATE_NOTES_LIST:
            self.note_renderer.draw_notes_list()
        elif self.state == STATE_MAP:
            self.map_screen.draw()
            
    def draw_panel(self, rect):
        self.ui_renderer.draw_panel(rect)

    def wrap_text(self, text, font, max_w):
        return self.ui_renderer.wrap_text(text, font, max_w)

    def get_infection_color(self, inf):
        return self.ui_renderer.get_infection_color(inf)

    # ─── Notes ───────────────────────────────────────────────

def draw_note_view(self):
    """Render single note reading screen."""
    if not self.viewing_note or not isinstance(self.viewing_note, dict):
        return

    self.screen.fill(BACKGROUND_COLOR)

    panel = pygame.Rect(
        WINDOW_WIDTH // 2 - 400, 80,
        800, WINDOW_HEIGHT - 160
    )
    pygame.draw.rect(self.screen, (45, 40, 30), panel, border_radius=12)
    pygame.draw.rect(self.screen, (90, 80, 60), panel, width=3, border_radius=12)

    # Title
    title = self.header_font.render(
        self.viewing_note.get("title", "Unknown Note"),
        True, (220, 200, 140)
    )
    self.screen.blit(title, (panel.x + 30, panel.y + 25))

    # Divider
    pygame.draw.line(
        self.screen, (120, 100, 70),
        (panel.x + 30,   panel.y + 70),
        (panel.right - 30, panel.y + 70), 1
    )

    # Body text
    text = self.viewing_note.get("text", "")
    lines = self.ui_renderer.wrap_text(text, self.text_font, panel.width - 60)
    y = panel.y + 90
    for line in lines:
        self.screen.blit(
            self.text_font.render(line, True, (230, 220, 190)),
            (panel.x + 30, y)
        )
        y += 34

    # Hint
    hint = self.small_font.render(
        "Press ENTER, SPACE or ESC to continue",
        True, (180, 160, 120)
    )
    self.screen.blit(
        hint,
        hint.get_rect(center=(WINDOW_WIDTH // 2, panel.bottom - 25))
    )


def draw_notes_list(self):
    """Render the list of found notes."""
    self.screen.fill(BACKGROUND_COLOR)

    title = self.title_font.render("FOUND NOTES", True, ACCENT_COLOR)
    self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 60)))

    panel = pygame.Rect(
        PADDING, 110,
        WINDOW_WIDTH - PADDING * 2,
        WINDOW_HEIGHT - 170
    )
    self.draw_panel(panel)

    found_notes = [
        self.notes_by_id[nid]
        for nid in self.player.found_notes
        if nid in self.notes_by_id
    ]

    if not found_notes:
        empty = self.text_font.render(
            "You haven't found any notes yet.", True, GRAY_DISABLED
        )
        self.screen.blit(empty, empty.get_rect(center=(panel.centerx, panel.centery)))
    else:
        y = panel.y + 30
        for index, note in enumerate(found_notes):
            is_selected = index == self.notes_list_index
            color  = YELLOW if is_selected else WHITE
            prefix = "> " if is_selected else "  "
            rendered = self.text_font.render(
                f"{prefix}{note.get('title', 'Unknown')}",
                True, color
            )
            self.screen.blit(rendered, (panel.x + 30, y))
            y += 36

    hint = self.small_font.render(
        "UP/DOWN — select   ENTER — read   ESC — close",
        True, TEXT_COLOR
    )
    self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))