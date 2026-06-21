"""
Save and load game state with data validation.
"""
import json
import os

from settings import SAVES_DIR


class SaveManager:
    def __init__(self):
        if not SAVES_DIR.exists():
            SAVES_DIR.mkdir(parents=True)

    def get_save_path(self, file_reference):
        return file_reference

    def save_exists(self, file_reference):
        return os.path.exists(self.get_save_path(file_reference))

    def save_game(self, player, current_enemy, file_reference):
        save_data = {
            "player": {
                "name": player.name,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "infection": player.infection,
                "max_infection": player.max_infection,
                "current_location_id": player.current_location_id,
                "inventory": dict(player.inventory),
                "flags": dict(player.flags),
                "suppressant_battles_left": player.suppressant_battles_left,
                "used_one_time_actions": list(player.used_one_time_actions),
                "escape_attempts": player.escape_attempts,
                "found_notes": player.found_notes,
                "visited_locations": list(player.visited_locations),
            },
            "enemy": None,
        }

        if current_enemy is not None:
            save_data["enemy"] = {
                "id": current_enemy.id,
                "hp": current_enemy.hp,
                "max_hp": current_enemy.max_hp,
                "base_damage": current_enemy.base_damage,
                "infection_on_hit": current_enemy.infection_on_hit,
                "attack_pattern": current_enemy.attack_pattern,
                "escape_chance": current_enemy.escape_chance,
                "is_boss": current_enemy.is_boss,
            }

        path = self.get_save_path(file_reference)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Save error: {e}")
            return False
        return True

    def load_game(self, player_ref, enemies_by_id, file_reference,
                  valid_locations=None):
        """
        Load game state with validation.
        Args:
            player_ref: Player object to restore into
            enemies_by_id: dict of enemy templates
            file_reference: path to save file
            valid_locations: set of valid location IDs (optional)
        Returns:
            (Enemy or None, bool): restored enemy and success flag
        """
        path = self.get_save_path(file_reference)
        if not os.path.exists(path):
            print(f"Load failed: {path} not found.")
            return None, False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Load error: {e}")
            return None, False

        player_data = data.get("player")
        enemy_data = data.get("enemy")

        if not player_data:
            print("Load failed: no player data.")
            return None, False

        # ── Validate player data ──────────────────────────────
        errors = self._validate_player_data(player_data, valid_locations)
        if errors:
            for err in errors:
                print(f"Save validation error: {err}")
            return None, False

        # ── Restore player ────────────────────────────────────
        player_ref.name = player_data.get("name", "Survivor")
        player_ref.hp = player_data.get("hp", 100)
        player_ref.max_hp = player_data.get("max_hp", 100)
        player_ref.infection = player_data.get("infection", 0)
        player_ref.max_infection = player_data.get("max_infection", 100)
        player_ref.current_location_id = player_data.get(
            "current_location_id", "police_station"
        )

        player_ref.inventory = {}
        for k, v in player_data.get("inventory", {}).items():
            player_ref.inventory[k] = v

        player_ref.flags = player_data.get("flags", {})
        player_ref.suppressant_battles_left = player_data.get(
            "suppressant_battles_left", 0
        )
        player_ref.used_one_time_actions = set(
            tuple(x) for x in player_data.get("used_one_time_actions", [])
        )
        player_ref.escape_attempts = player_data.get("escape_attempts", 0)
        player_ref.found_notes = player_data.get("found_notes", [])
        player_ref.visited_locations = set(
            player_data.get("visited_locations",
                            [player_ref.current_location_id])
        )

        # ── Restore enemy ─────────────────────────────────────
        restored_enemy = None
        if enemy_data and isinstance(enemy_data, dict):
            enemy_id = enemy_data.get("id")
            template = enemies_by_id.get(enemy_id)
            if template is not None:
                from src.enemy import Enemy
                restored_enemy = Enemy(template)
                restored_enemy.hp = min(
                    max(0, enemy_data.get("hp", restored_enemy.max_hp)),
                    restored_enemy.max_hp
                )

        return restored_enemy, True

    def _validate_player_data(self, pd, valid_locations=None):
        """Validate player data from save file. Returns list of errors."""
        errors = []

        # HP validation
        hp = pd.get("hp", 100)
        max_hp = pd.get("max_hp", 100)

        if not isinstance(hp, (int, float)):
            errors.append(f"hp is not a number: {hp}")
        elif hp < 0:
            errors.append(f"hp is negative: {hp}")
        elif hp > max_hp:
            errors.append(f"hp ({hp}) exceeds max_hp ({max_hp})")

        if not isinstance(max_hp, (int, float)):
            errors.append(f"max_hp is not a number: {max_hp}")
        elif max_hp <= 0:
            errors.append(f"max_hp must be positive: {max_hp}")

        # Infection validation
        infection = pd.get("infection", 0)
        if not isinstance(infection, (int, float)):
            errors.append(f"infection is not a number: {infection}")
        elif infection < 0:
            errors.append(f"infection is negative: {infection}")
        elif infection > 100:
            errors.append(f"infection exceeds 100: {infection}")

        # Location validation
        loc_id = pd.get("current_location_id")
        if valid_locations and loc_id not in valid_locations:
            errors.append(f"unknown location: {loc_id}")

        # Inventory validation
        inventory = pd.get("inventory", {})
        if isinstance(inventory, dict):
            for item_id, qty in inventory.items():
                if not isinstance(qty, (int, float)):
                    errors.append(f"inventory[{item_id}] not a number: {qty}")
                elif qty < 0:
                    errors.append(f"inventory[{item_id}] is negative: {qty}")

        # Suppressant validation
        supp = pd.get("suppressant_battles_left", 0)
        if not isinstance(supp, (int, float)) or supp < 0:
            errors.append(f"suppressant invalid: {supp}")

        return errors