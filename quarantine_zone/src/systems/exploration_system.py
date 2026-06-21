"""
exploration_system.py
Handles movement, searching, special actions and encounters.
"""
import random

from settings import STATE_EXPLORATION


class ExplorationSystem:
    def __init__(self, game):
        self.game = game

    # ── Movement ──────────────────────────────────────────────

    def try_move_to(self, connection):
        g = self.game
        target_id = connection.get("target_id")
        if target_id is None:
            return
        if not self.check_requirements(connection.get("requirements", [])):
            g.set_message("You cannot go there yet.")
            return
        if target_id not in g.locations_by_id:
            return

        g.player.current_location_id = target_id
        g.player.visited_locations.add(target_id)

        target = g.locations_by_id[target_id]
        name = target.get("name", target_id)

        # Infection on travel
        inf_gain = target.get("action_infection_gain", 0)
        prot = target.get("protection_item_id", "")
        if prot and g.player.has_item(prot):
            inf_gain = target.get("protected_action_infection_gain", 0)

        if inf_gain > 0:
            g.player.add_infection(inf_gain)
            g.set_message(
                f"You enter {name}. The air feels wrong. +{inf_gain}% infection."
            )
        else:
            g.set_message(f"You move to {name}.")

        # Travel encounter
        chance = target.get("travel_encounter_chance", 0)
        if chance > 0 and random.randint(1, 100) <= chance:
            table = target.get("encounter_table", [])
            if table:
                g.set_message(f"You enter {name} — something moves in the shadows!")
                self.start_random_encounter(table)

    # ── Requirements ──────────────────────────────────────────

    def check_requirements(self, requirements):
        g = self.game
        for req in requirements:
            rtype = req.get("type")
            rid = req.get("id")
            if rtype == "item" and not g.player.has_item(rid):
                return False
            if rtype == "flag" and not g.player.flags.get(rid, False):
                return False
        return True

    # ── Special actions ───────────────────────────────────────

    def get_available_special_actions(self, location):
        result = []
        for action in location.get("special_actions", []):
            if not action.get("repeatable", False):
                if self._is_action_used(location, action):
                    continue
            result.append(action)
        return result

    def _is_action_used(self, location, action):
        key = (location.get("id"), action.get("id"))
        return key in self.game.player.used_one_time_actions

    def mark_action_used(self, location, action):
        key = (location.get("id"), action.get("id"))
        self.game.player.used_one_time_actions.add(key)

    def try_perform_action(self, action):
        g = self.game
        location = g.get_current_location()
        if location is None:
            return
        if not self.check_requirements(action.get("requirements", [])):
            g.set_message("You cannot perform this action yet.")
            return

        atype = action.get("type", "")
        if atype == "one_time_reward":
            self._perform_reward_action(location, action)
        elif atype == "treatment":
            self._perform_treatment_action(location, action)
        elif atype == "boss_battle":
            self._start_boss_battle(action)
        else:
            g.set_message(f"Unknown action type: {atype}")

    def _perform_reward_action(self, location, action):
        g = self.game
        rewards = action.get("rewards", {})
        effects = action.get("effects", {})

        gained_parts = []

        for entry in rewards.get("items", []):
            item_id = entry.get("item_id")
            qty = entry.get("quantity", 1)
            g.player.add_item(item_id, qty)
            gained_parts.append(f"{g.get_item_name(item_id)} x{qty}")

        for flag in rewards.get("flags", []):
            g.player.flags[flag] = True

        # Notes via rewards
        g.note_system.show_notes_from_rewards(rewards.get("notes", []))

        heal_hp = effects.get("heal_hp", 0)
        reduce_inf = effects.get("reduce_infection", 0)
        if heal_hp > 0:
            g.player.heal(heal_hp)
        if reduce_inf > 0:
            g.player.reduce_infection(reduce_inf)

        self.mark_action_used(location, action)
        g.sound_manager.play_sfx("item_pickup")

        desc = action.get("description", "")
        if gained_parts:
            g.set_message(f"{desc}  Gained: {', '.join(gained_parts)}.")
        else:
            g.set_message(desc)

    def _perform_treatment_action(self, location, action):
        g = self.game
        effects = action.get("effects", {})
        heal_hp = effects.get("heal_hp", 0)
        reduce_inf = effects.get("reduce_infection", 0)
        if heal_hp > 0:
            g.player.heal(heal_hp)
        if reduce_inf > 0:
            g.player.reduce_infection(reduce_inf)
        self.mark_action_used(location, action)
        g.set_message(f"Treatment used. +{heal_hp} HP, -{reduce_inf} infection.")

    def _start_boss_battle(self, action):
        g = self.game
        location = g.get_current_location()
        enemy_id = action.get("enemy_id")
        if enemy_id and enemy_id in g.enemies_by_id:
            self.mark_action_used(location, action)
            g.battle_system.start_battle(
                g.enemies_by_id[enemy_id],
                is_story_battle=True
            )

    # ── Search ────────────────────────────────────────────────

    def try_search_location(self, location):
        g = self.game
        if not location.get("search_enabled", False):
            g.set_message("Nothing to search here.")
            return

        loc_id = location.get("id")
        search_key = f"search_{loc_id}"
        limit = location.get("search_attempts_limit", 0)
        used = g.player.inventory.get(search_key, 0)

        if used >= limit:
            g.set_message("You have already searched this area thoroughly.")
            return

        self._start_search_qte(location)

    def _start_search_qte(self, location):
        g = self.game
        from settings import (
            SEARCH_QTE_BAR_WIDTH,
            SEARCH_QTE_GREEN_WIDTH,
            SEARCH_QTE_YELLOW_WIDTH,
        )
        g.search_qte_location = location
        g.search_qte_active = True

        g.search_qte_bar_x = 640 - SEARCH_QTE_BAR_WIDTH // 2
        g.search_qte_bar_y = 360

        min_x = g.search_qte_bar_x + SEARCH_QTE_YELLOW_WIDTH + 10
        max_x = (
            g.search_qte_bar_x
            + SEARCH_QTE_BAR_WIDTH
            - SEARCH_QTE_YELLOW_WIDTH
            - SEARCH_QTE_GREEN_WIDTH
            - 10
        )
        if max_x <= min_x:
            max_x = min_x + 1

        g.search_qte_green_start = random.randint(min_x, max_x)
        g.search_qte_green_end = g.search_qte_green_start + SEARCH_QTE_GREEN_WIDTH
        g.search_qte_yellow_start = g.search_qte_green_start - SEARCH_QTE_YELLOW_WIDTH
        g.search_qte_yellow_end = g.search_qte_green_end + SEARCH_QTE_YELLOW_WIDTH
        g.search_qte_marker_x = g.search_qte_bar_x
        g.search_qte_direction = 1

    def update_search_qte(self):
        g = self.game
        from settings import SEARCH_QTE_BAR_WIDTH, SEARCH_QTE_MARKER_SPEED, QTE_MARKER_WIDTH
        if not g.search_qte_active:
            return
        g.search_qte_marker_x += SEARCH_QTE_MARKER_SPEED * g.search_qte_direction
        right = g.search_qte_bar_x + SEARCH_QTE_BAR_WIDTH - QTE_MARKER_WIDTH
        if g.search_qte_marker_x >= right:
            g.search_qte_marker_x = right
            g.search_qte_direction = -1
        elif g.search_qte_marker_x <= g.search_qte_bar_x:
            g.search_qte_marker_x = g.search_qte_bar_x
            g.search_qte_direction = 1

    def resolve_search_qte(self):
        g = self.game
        from settings import SEARCH_QTE_BAR_WIDTH, QTE_MARKER_WIDTH
        g.search_qte_active = False
        location = g.search_qte_location
        g.search_qte_location = None

        marker_center = g.search_qte_marker_x + QTE_MARKER_WIDTH // 2

        if g.search_qte_green_start <= marker_center <= g.search_qte_green_end:
            quality = "green"
        elif g.search_qte_yellow_start <= marker_center <= g.search_qte_yellow_end:
            quality = "yellow"
        else:
            quality = "miss"

        loc_id = location.get("id")
        search_key = f"search_{loc_id}"
        g.player.add_item(search_key, 1)

        # Infection
        inf_gain = location.get("action_infection_gain", 0)
        prot = location.get("protection_item_id", "")
        if prot and g.player.has_item(prot):
            inf_gain = location.get("protected_action_infection_gain", 0)
        if inf_gain > 0:
            g.player.add_infection(inf_gain)

        # Encounter
        enc_chance = location.get("search_encounter_chance", 0)
        if random.randint(1, 100) <= enc_chance:
            table = location.get("encounter_table", [])
            if table:
                self.start_random_encounter(table)
                return

        if quality == "miss":
            g.set_message(random.choice([
                "You search hastily but find nothing.",
                "Nothing useful here. You wasted time.",
                "Searched poorly — found nothing.",
            ]))
            return

        # Try note
        note = g.note_system.try_find_note(loc_id)
        if note:
            g.note_system.show_note(note)
            g.sound_manager.play_sfx("item_pickup")
            return

        loot_table = location.get("search_loot_table", [])
        no_find = location.get("no_find_chance", 50)
        if quality == "green":
            no_find = max(0, no_find - 30)

        if random.randint(1, 100) <= no_find:
            g.set_message("You search the area but find nothing useful.")
            return

        found = g.roll_loot(loot_table)
        if found:
            item_id = found["item_id"]
            qty = found.get("quantity", 1)
            if quality == "green" and random.randint(1, 100) <= 40:
                qty += 1
            g.player.add_item(item_id, qty)
            g.sound_manager.play_sfx("item_pickup")
            prefix = "★ Excellent search! Found:" if quality == "green" else "Found:"
            g.set_message(f"{prefix} {g.get_item_name(item_id)} x{qty}.")
        else:
            g.set_message("You search the area but find nothing useful.")

    def start_random_encounter(self, encounter_table):
        g = self.game
        total = sum(e.get("weight", 0) for e in encounter_table)
        if total <= 0:
            return
        roll = random.randint(1, total)
        cumulative = 0
        for entry in encounter_table:
            cumulative += entry.get("weight", 0)
            if roll <= cumulative:
                eid = entry.get("enemy_id")
                if eid in g.enemies_by_id:
                    g.battle_system.start_battle(g.enemies_by_id[eid])
                return