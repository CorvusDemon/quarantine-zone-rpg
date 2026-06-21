"""
Tests for SaveManager.
Run: pytest tests/
"""
import pytest # type: ignore
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.player import Player
from src.enemy import Enemy
from src.save_manager import SaveManager

ENEMY_DATA = {
    "id": "normal_zombie",
    "name": "Normal Zombie",
    "type": "standard",
    "is_boss": False,
    "max_hp": 60,
    "base_damage": 18,
    "infection_on_hit": 3,
    "attack_pattern": "heavy",
    "escape_chance": 70,
    "loot_table": [],
    "no_drop_chance": 35,
}

ENEMIES_BY_ID = {"normal_zombie": ENEMY_DATA}


@pytest.fixture
def save_file(tmp_path):
    return tmp_path / "test_save.json"


@pytest.fixture
def manager(tmp_path):
    # Override SAVES_DIR to temp
    sm = SaveManager.__new__(SaveManager)
    tmp_path.mkdir(parents=True, exist_ok=True)
    return sm


@pytest.fixture
def player():
    p = Player("Survivor", "police_station")
    p.add_item("bandage", 2)
    p.add_item("cloth", 1)
    p.infection = 25
    p.hp = 80
    p.flags["first_aid_notes"] = True
    p.found_notes = ["note_1"]
    p.visited_locations = {"police_station", "street"}
    return p


class TestSaveManager:
    def test_save_creates_file(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        result = sm.save_game(player, None, save_path)
        assert result is True
        assert save_path.exists()

    def test_save_file_is_valid_json(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        with open(save_path) as f:
            data = json.load(f)
        assert "player" in data
        assert "enemy" in data

    def test_save_preserves_player_data(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        with open(save_path) as f:
            data = json.load(f)
        pd = data["player"]
        assert pd["hp"] == 80
        assert pd["infection"] == 25
        assert pd["flags"]["first_aid_notes"] is True

    def test_load_restores_player(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)

        new_player = Player("Empty", "police_station")
        _, ok = sm.load_game(new_player, ENEMIES_BY_ID, save_path)

        assert ok is True
        assert new_player.hp == 80
        assert new_player.infection == 25
        assert new_player.flags["first_aid_notes"] is True

    def test_save_exists_true(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        assert sm.save_exists(save_path) is True

    def test_save_exists_false(self, tmp_path):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "nonexistent.json"
        assert sm.save_exists(save_path) is False

    def test_load_missing_file(self, tmp_path):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "missing.json"
        player = Player("Test", "police_station")
        _, ok = sm.load_game(player, {}, save_path)
        assert ok is False

    def test_save_and_load_enemy(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        enemy = Enemy(ENEMY_DATA)
        enemy.hp = 30
        sm.save_game(player, enemy, save_path)

        new_player = Player("Empty", "police_station")
        loaded_enemy, ok = sm.load_game(new_player, ENEMIES_BY_ID, save_path)

        assert ok is True
        assert loaded_enemy is not None
        assert loaded_enemy.hp == 30
        assert loaded_enemy.name == "Normal Zombie"

    def test_save_no_enemy(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        with open(save_path) as f:
            data = json.load(f)
        assert data["enemy"] is None

    def test_load_found_notes(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        new_player = Player("Empty", "police_station")
        sm.load_game(new_player, {}, save_path)
        assert "note_1" in new_player.found_notes

    def test_load_visited_locations(self, tmp_path, player):
        sm = SaveManager.__new__(SaveManager)
        save_path = tmp_path / "save.json"
        sm.save_game(player, None, save_path)
        new_player = Player("Empty", "police_station")
        sm.load_game(new_player, {}, save_path)
        assert "street" in new_player.visited_locations