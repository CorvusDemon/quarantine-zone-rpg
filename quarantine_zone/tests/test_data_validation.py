"""
Tests for JSON data integrity.
Run: pytest tests/
"""
import json
import pytest # type: ignore
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def items():
    return {i["id"]: i for i in load("items.json").get("items", [])}


@pytest.fixture(scope="module")
def enemies():
    return {e["id"]: e for e in load("enemies.json").get("enemies", [])}


@pytest.fixture(scope="module")
def locations():
    return {loc["id"]: loc for loc in load("locations.json").get("locations", [])}


@pytest.fixture(scope="module")
def recipes():
    return load("recipes.json").get("recipes", [])


@pytest.fixture(scope="module")
def notes():
    return load("notes.json").get("notes", [])


class TestItemsData:
    def test_items_not_empty(self, items):
        assert len(items) > 0

    def test_items_have_required_fields(self, items):
        for item_id, item in items.items():
            assert "name" in item, f"{item_id} missing name"
            assert "category" in item, f"{item_id} missing category"
            assert "effects" in item, f"{item_id} missing effects"

    def test_item_categories_valid(self, items):
        valid = {"consumable", "material", "key_item"}
        for item_id, item in items.items():
            assert item["category"] in valid, \
                f"{item_id} has invalid category: {item['category']}"


class TestEnemiesData:
    def test_enemies_not_empty(self, enemies):
        assert len(enemies) > 0

    def test_enemies_have_required_fields(self, enemies):
        for eid, enemy in enemies.items():
            for field in ("name", "max_hp", "base_damage",
                          "attack_pattern", "is_boss"):
                assert field in enemy, f"{eid} missing {field}"

    def test_attack_patterns_valid(self, enemies):
        valid = {"heavy", "fast", "toxic", "mixed"}
        for eid, enemy in enemies.items():
            assert enemy["attack_pattern"] in valid, \
                f"{eid} invalid pattern: {enemy['attack_pattern']}"

    def test_boss_escape_chance_zero(self, enemies):
        for eid, enemy in enemies.items():
            if enemy.get("is_boss"):
                assert enemy["escape_chance"] == 0, \
                    f"Boss {eid} should have escape_chance=0"


class TestLocationsData:
    def test_locations_not_empty(self, locations):
        assert len(locations) > 0

    def test_locations_have_required_fields(self, locations):
        for lid, loc in locations.items():
            for field in ("name", "description", "connections"):
                assert field in loc, f"{lid} missing {field}"

    def test_connections_point_to_existing_locations(self, locations):
        for lid, loc in locations.items():
            for conn in loc.get("connections", []):
                tid = conn.get("target_id")
                assert tid in locations, \
                    f"{lid} → unknown location '{tid}'"

    def test_loot_table_items_exist(self, locations, items):
        for lid, loc in locations.items():
            for entry in loc.get("search_loot_table", []):
                iid = entry.get("item_id")
                assert iid in items, \
                    f"{lid} loot table: unknown item '{iid}'"

    def test_encounter_table_enemies_exist(self, locations, enemies):
        for lid, loc in locations.items():
            for entry in loc.get("encounter_table", []):
                eid = entry.get("enemy_id")
                assert eid in enemies, \
                    f"{lid} encounter table: unknown enemy '{eid}'"


class TestRecipesData:
    def test_recipes_not_empty(self, recipes):
        assert len(recipes) > 0

    def test_recipe_materials_exist(self, recipes, items):
        for recipe in recipes:
            for mat in recipe.get("materials", []):
                iid = mat.get("item_id")
                assert iid in items, \
                    f"Recipe '{recipe['id']}': unknown material '{iid}'"

    def test_recipe_result_exists(self, recipes, items):
        for recipe in recipes:
            rid = recipe.get("result", {}).get("item_id")
            assert rid in items, \
                f"Recipe '{recipe['id']}': unknown result '{rid}'"


class TestNotesData:
    def test_notes_not_empty(self, notes):
        assert len(notes) > 0

    def test_notes_have_required_fields(self, notes):
        for note in notes:
            nid = note.get("id", "?")
            for field in ("title", "text", "found_in"):
                assert field in note, f"Note '{nid}' missing {field}"
                assert note[field], f"Note '{nid}' empty {field}"

    def test_note_ids_unique(self, notes):
        ids = [n["id"] for n in notes]
        assert len(ids) == len(set(ids)), "Duplicate note IDs found"

    def test_notes_found_in_valid_location(self, notes, locations):
        for note in notes:
            found_in = note.get("found_in")
            if found_in:
                assert found_in in locations, \
                    f"Note '{note['id']}' found_in unknown location '{found_in}'"