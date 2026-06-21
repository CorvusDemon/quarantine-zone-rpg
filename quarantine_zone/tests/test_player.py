"""
Tests for Player model.
Run: pytest tests/
"""
import pytest # type: ignore
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.player import Player


@pytest.fixture
def player():
    return Player(name="Survivor", start_location_id="police_station")


class TestPlayerInit:
    def test_initial_hp(self, player):
        assert player.hp == 100
        assert player.max_hp == 100

    def test_initial_infection(self, player):
        assert player.infection == 0

    def test_initial_location(self, player):
        assert player.current_location_id == "police_station"

    def test_initial_inventory_empty(self, player):
        assert player.inventory == {}

    def test_initial_visited_locations(self, player):
        assert "police_station" in player.visited_locations

    def test_initial_found_notes_empty(self, player):
        assert player.found_notes == []


class TestPlayerHealth:
    def test_take_damage(self, player):
        player.take_damage(30)
        assert player.hp == 70

    def test_take_damage_not_below_zero(self, player):
        player.take_damage(999)
        assert player.hp == 0

    def test_heal(self, player):
        player.take_damage(50)
        player.heal(20)
        assert player.hp == 70

    def test_heal_not_above_max(self, player):
        player.heal(999)
        assert player.hp == player.max_hp

    def test_heal_reduced_at_high_infection(self, player):
        player.take_damage(50)
        player.infection = 50
        player.heal(20)
        # 20 * 0.8 = 16
        assert player.hp == 66

    def test_is_alive_true(self, player):
        assert player.is_alive() is True

    def test_is_alive_false_no_hp(self, player):
        player.take_damage(100)
        assert player.is_alive() is False

    def test_is_alive_false_full_infection(self, player):
        player.infection = 100
        assert player.is_alive() is False


class TestPlayerInfection:
    def test_add_infection(self, player):
        player.add_infection(20)
        assert player.infection == 20

    def test_add_infection_not_above_max(self, player):
        player.add_infection(999)
        assert player.infection == 100

    def test_reduce_infection(self, player):
        player.infection = 50
        player.reduce_infection(20)
        assert player.infection == 30

    def test_reduce_infection_not_below_zero(self, player):
        player.infection = 10
        player.reduce_infection(999)
        assert player.infection == 0

    def test_suppressant_reduces_infection_gain(self, player):
        player.suppressant_battles_left = 1
        player.add_infection(20)
        assert player.infection == 10  # 20 * 0.5

    def test_infection_state_stable(self, player):
        player.infection = 0
        assert player.get_infection_state() == "Stable"

    def test_infection_state_fever(self, player):
        player.infection = 25
        assert player.get_infection_state() == "Fever"

    def test_infection_state_instability(self, player):
        player.infection = 50
        assert player.get_infection_state() == "Instability"

    def test_infection_state_critical(self, player):
        player.infection = 75
        assert player.get_infection_state() == "Critical"

    def test_infection_state_transformation(self, player):
        player.infection = 100
        assert player.get_infection_state() == "Transformation"


class TestPlayerInventory:
    def test_add_item(self, player):
        player.add_item("bandage", 2)
        assert player.inventory["bandage"] == 2

    def test_add_item_stacks(self, player):
        player.add_item("bandage", 2)
        player.add_item("bandage", 3)
        assert player.inventory["bandage"] == 5

    def test_has_item_true(self, player):
        player.add_item("bandage", 2)
        assert player.has_item("bandage") is True

    def test_has_item_false(self, player):
        assert player.has_item("bandage") is False

    def test_has_item_quantity(self, player):
        player.add_item("bandage", 1)
        assert player.has_item("bandage", 2) is False

    def test_remove_item(self, player):
        player.add_item("bandage", 3)
        result = player.remove_item("bandage", 2)
        assert result is True
        assert player.inventory["bandage"] == 1

    def test_remove_item_deletes_when_zero(self, player):
        player.add_item("bandage", 1)
        player.remove_item("bandage", 1)
        assert "bandage" not in player.inventory

    def test_remove_item_not_enough(self, player):
        player.add_item("bandage", 1)
        result = player.remove_item("bandage", 5)
        assert result is False

    def test_remove_item_missing(self, player):
        result = player.remove_item("bandage")
        assert result is False