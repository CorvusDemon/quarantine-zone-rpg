"""
Tests for Enemy model.
Run: pytest tests/
"""
import pytest # type: ignore
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.enemy import Enemy

NORMAL_ZOMBIE_DATA = {
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

BOSS_DATA = {
    "id": "alpha_mutant",
    "name": "Alpha Mutant",
    "type": "boss",
    "is_boss": True,
    "max_hp": 200,
    "base_damage": 32,
    "infection_on_hit": 12,
    "attack_pattern": "mixed",
    "escape_chance": 0,
    "loot_table": [],
    "no_drop_chance": 100,
}


@pytest.fixture
def zombie():
    return Enemy(NORMAL_ZOMBIE_DATA)


@pytest.fixture
def boss():
    return Enemy(BOSS_DATA)


class TestEnemyInit:
    def test_name(self, zombie):
        assert zombie.name == "Normal Zombie"

    def test_hp_equals_max(self, zombie):
        assert zombie.hp == zombie.max_hp == 60

    def test_is_boss_false(self, zombie):
        assert zombie.is_boss is False

    def test_is_boss_true(self, boss):
        assert boss.is_boss is True

    def test_attack_pattern(self, zombie):
        assert zombie.attack_pattern == "heavy"


class TestEnemyCombat:
    def test_take_damage(self, zombie):
        zombie.take_damage(20)
        assert zombie.hp == 40

    def test_take_damage_not_below_zero(self, zombie):
        zombie.take_damage(999)
        assert zombie.hp == 0

    def test_is_alive_true(self, zombie):
        assert zombie.is_alive() is True

    def test_is_alive_false(self, zombie):
        zombie.take_damage(999)
        assert zombie.is_alive() is False

    def test_get_damage(self, zombie):
        assert zombie.get_damage() == 18

    def test_boss_escape_chance_zero(self, boss):
        assert boss.escape_chance == 0