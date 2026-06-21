"""
battle_system.py
Handles all combat logic: QTE, reactions, skills, flee, loot.
"""
import random

from settings import (
    STATE_BATTLE, STATE_EXPLORATION, STATE_GAME_OVER, STATE_VICTORY,
    BATTLE_PLAYER_TURN, BATTLE_ENEMY_TURN, BATTLE_RESULT,
    BATTLE_QTE, BATTLE_REACTION,
    QTE_BAR_WIDTH, QTE_BAR_HEIGHT, QTE_MARKER_WIDTH, QTE_MARKER_SPEED,
    QTE_GREEN_ZONE_WIDTH, QTE_YELLOW_ZONE_WIDTH,
    INFECTED_STRIKE_THRESHOLD, INFECTED_STRIKE_MULTIPLIER, INFECTED_STRIKE_COST,
    MUTANT_BURST_THRESHOLD, MUTANT_BURST_MULTIPLIER, MUTANT_BURST_COST,
    MAX_ESCAPE_ATTEMPTS, ESCAPE_PENALTY_PER_ATTEMPT,
    LOW_HP_THRESHOLD_PERCENT, LOW_HP_ESCAPE_PENALTY,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)

# Battle log colors
LOG_COLOR_DEFAULT  = (220, 220, 225)
LOG_COLOR_DAMAGE   = (220, 80,  80)
LOG_COLOR_ATTACK   = (100, 200, 120)
LOG_COLOR_MISS     = (150, 150, 160)
LOG_COLOR_INFECTION= (180, 80,  220)
LOG_COLOR_HEAL     = (80,  200, 140)
LOG_COLOR_ENEMY    = (210, 120, 50)
LOG_COLOR_SYSTEM   = (130, 180, 255)
LOG_COLOR_FLEE     = (220, 200, 80)
LOG_COLOR_SKILL    = (220, 100, 60)
LOG_COLOR_WARN     = (220, 180, 50)

OPTIMAL_REACTION = {
    "heavy": "block",
    "fast":  "counter",
    "toxic": "dodge",
    "mixed": None,
}


class BattleSystem:
    def __init__(self, game):
        self.game = game

    # ── Helpers ───────────────────────────────────────────────

    def blog(self, text, color=None):
        if color is None:
            color = LOG_COLOR_DEFAULT
        self.game.battle_log.append((text, color))

    # ── Start / End ───────────────────────────────────────────

    def start_battle(self, enemy_data, is_story_battle=False):
        from src.enemy import Enemy
        g = self.game
        g.current_enemy = Enemy(enemy_data)
        g.battle_sub_state = BATTLE_PLAYER_TURN
        g.battle_log = []
        g.battle_result = None
        g.battle_item_mode = False
        g.battle_skill_mode = False
        g.battle_consumables = []
        g.is_story_battle = is_story_battle
        g.player.escape_attempts = 0
        g.state = STATE_BATTLE
        g.sound_manager.play_music("battle")
        self.blog(f"━━━ {g.current_enemy.name} appears! ━━━", LOG_COLOR_ENEMY)

    def end_battle(self):
        g = self.game
        if g.battle_result == "victory":
            g.sound_manager.play_sfx("victory")
            loot = self._generate_loot()
            if loot:
                item_id = loot["item_id"]
                qty = loot.get("quantity", 1)
                g.player.add_item(item_id, qty)
                g.set_message(
                    f"Victory! Loot: {g.get_item_name(item_id)} x{qty}."
                )
            else:
                g.set_message("Victory! No loot.")

            if g.current_enemy.is_boss:
                g.state = STATE_VICTORY
                return

            if g.player.suppressant_battles_left > 0:
                g.player.suppressant_battles_left -= 1

        elif g.battle_result == "defeat":
            g.sound_manager.play_sfx("defeat")
            g.state = STATE_GAME_OVER
            return
        else:
            g.sound_manager.play_sfx("flee")
            g.set_message("Escaped the fight.")

        g.current_enemy = None
        g.state = STATE_EXPLORATION
        g.sound_manager.play_music("exploration")

    def _generate_loot(self):
        g = self.game
        if g.current_enemy is None:
            return None
        if random.randint(1, 100) <= g.current_enemy.no_drop_chance:
            return None
        return g.roll_loot(g.current_enemy.loot_table)

    # ── QTE ───────────────────────────────────────────────────

    def start_qte(self, skill_type):
        g = self.game
        g.qte_skill = skill_type
        g.qte_bar_x = WINDOW_WIDTH  // 2 - QTE_BAR_WIDTH  // 2
        g.qte_bar_y = WINDOW_HEIGHT // 2 - QTE_BAR_HEIGHT // 2

        green_w = QTE_GREEN_ZONE_WIDTH
        yellow_w = QTE_YELLOW_ZONE_WIDTH

        if g.player.infection >= 25:
            green_w = int(green_w * 0.8)

        min_x = g.qte_bar_x + yellow_w + 20
        max_x = g.qte_bar_x + QTE_BAR_WIDTH - yellow_w - green_w - 20
        if max_x <= min_x:
            max_x = min_x + 1

        g.qte_green_start  = random.randint(min_x, max_x)
        g.qte_green_end    = g.qte_green_start + green_w
        g.qte_yellow_start = g.qte_green_start - yellow_w
        g.qte_yellow_end   = g.qte_green_end   + yellow_w
        g.qte_marker_x     = g.qte_bar_x
        g.qte_direction    = 1
        g.battle_sub_state = BATTLE_QTE

    def update_qte(self):
        g = self.game
        g.qte_marker_x += QTE_MARKER_SPEED * g.qte_direction
        right = g.qte_bar_x + QTE_BAR_WIDTH - QTE_MARKER_WIDTH
        if g.qte_marker_x >= right:
            g.qte_marker_x = right
            g.qte_direction = -1
        elif g.qte_marker_x <= g.qte_bar_x:
            g.qte_marker_x = g.qte_bar_x
            g.qte_direction = 1

    def resolve_qte(self):
        g = self.game
        center = g.qte_marker_x + QTE_MARKER_WIDTH // 2

        if g.qte_green_start <= center <= g.qte_green_end:
            multiplier, result = 1.0, "GREEN"
        elif g.qte_yellow_start <= center <= g.qte_yellow_end:
            multiplier, result = 0.6, "YELLOW"
        else:
            multiplier, result = 0.0, "MISS"

        skill_mult = 1.0
        if g.qte_skill == "infected_strike":
            skill_mult = INFECTED_STRIKE_MULTIPLIER
            g.player.add_infection(INFECTED_STRIKE_COST)
            self.blog(random.choice([
                f"Infected Strike! Your veins burn. +{INFECTED_STRIKE_COST}% inf.",
                f"Mutation surges through you! +{INFECTED_STRIKE_COST}% inf.",
                f"You channel the infection! +{INFECTED_STRIKE_COST}% inf.",
            ]), LOG_COLOR_SKILL)
        elif g.qte_skill == "mutant_burst":
            skill_mult = MUTANT_BURST_MULTIPLIER
            g.player.add_infection(MUTANT_BURST_COST)
            self.blog(random.choice([
                f"Mutant Burst! You lose control. +{MUTANT_BURST_COST}% inf.",
                f"The virus explodes outward! +{MUTANT_BURST_COST}% inf.",
            ]), LOG_COLOR_SKILL)

        damage = int(random.randint(15, 25) * multiplier * skill_mult)
        enemy = g.current_enemy

        if result == "MISS":
            self.blog(random.choice([
                f"Missed! {enemy.name} sidesteps.",
                "Your attack hits nothing but air.",
                f"Too slow! {enemy.name} avoids the hit.",
            ]), LOG_COLOR_MISS)
        else:
            enemy.take_damage(damage)
            g.sound_manager.play_sfx("attack")
            if result == "GREEN":
                self.blog(random.choice([
                    f"★ Clean hit! {damage} damage.",
                    f"★ Perfect timing! {damage} damage.",
                ]), LOG_COLOR_ATTACK)
            else:
                self.blog(random.choice([
                    f"Glancing blow! {damage} damage.",
                    f"Weak hit for {damage} damage.",
                ]), LOG_COLOR_ATTACK)

        if not enemy.is_alive():
            self.blog(random.choice([
                f"{enemy.name} collapses.",
                f"{enemy.name} is defeated!",
            ]), LOG_COLOR_ENEMY)
            g.battle_result = "victory"
            g.battle_sub_state = BATTLE_RESULT
            return

        if g.player.infection >= 100:
            self.blog("The infection takes over completely...", LOG_COLOR_DAMAGE)
            g.battle_result = "defeat"
            g.battle_sub_state = BATTLE_RESULT
            return

        self.start_reaction_phase()

    # ── Reaction ──────────────────────────────────────────────

    def start_reaction_phase(self):
        g = self.game
        g.battle_sub_state = BATTLE_REACTION
        enemy = g.current_enemy

        messages = {
            "heavy": [
                f"{enemy.name} winds up a heavy strike!",
                f"{enemy.name} swings with terrifying strength!",
            ],
            "fast": [
                f"{enemy.name} darts forward in a flash!",
                f"{enemy.name} strikes rapidly without warning!",
            ],
            "toxic": [
                f"{enemy.name} spews infected fluids at you!",
                f"A wave of infection erupts from {enemy.name}!",
            ],
            "mixed": [
                f"{enemy.name} attacks unpredictably!",
                f"You can't read {enemy.name}'s next move!",
            ],
        }
        pattern = enemy.attack_pattern
        self.blog(
            random.choice(messages.get(pattern, [f"{enemy.name} attacks!"])),
            LOG_COLOR_WARN
        )

    def resolve_reaction(self, reaction):
        g = self.game
        enemy = g.current_enemy
        player = g.player
        pattern = enemy.attack_pattern
        optimal = OPTIMAL_REACTION.get(pattern)

        dmg = enemy.get_damage()
        inf = enemy.infection_on_hit
        counter = 0
        parts = []

        if reaction == "dodge":
            if pattern == "mixed":
                if random.randint(1, 100) <= 50:
                    dmg = inf = 0
                    parts.append("You barely dodge the attack!")
                else:
                    parts.append("Dodge failed!")
            elif optimal == "dodge":
                dmg = inf = 0
                parts.append("✦ Perfect dodge!")
            else:
                if random.randint(1, 100) <= 30:
                    dmg = inf = 0
                    parts.append("Lucky dodge!")
                else:
                    parts.append("Too slow to dodge.")

        elif reaction == "block":
            if pattern == "mixed":
                dmg //= 2
                parts.append("Partial block.")
            elif optimal == "block":
                dmg //= 2
                inf //= 2
                parts.append("✦ Solid block! Damage and infection reduced.")
            else:
                dmg = int(dmg * 0.75)
                parts.append("Weak block.")

        elif reaction == "counter":
            if pattern == "mixed":
                if random.randint(1, 100) <= 50:
                    counter = random.randint(8, 14)
                    dmg //= 2
                    parts.append(f"Counter connects! {counter} retaliation.")
                else:
                    parts.append("Counter missed! Full damage.")
            elif optimal == "counter":
                counter = random.randint(13, 18)
                dmg = inf = 0
                parts.append(f"✦ Perfect counter! {counter} damage, no harm taken.")
            else:
                parts.append("Counter mistimed. Full damage.")

        # Determine color
        if dmg == 0 and inf == 0:
            color = LOG_COLOR_ATTACK
        elif dmg > 0:
            color = LOG_COLOR_DAMAGE
        else:
            color = LOG_COLOR_DEFAULT

        if dmg > 0:
            player.take_damage(dmg)
            parts.append(f"-{dmg} HP.")
            g.sound_manager.play_sfx("hit")
        if inf > 0:
            player.add_infection(inf)
            parts.append(f"+{inf}% inf.")
            g.sound_manager.play_sfx("infection")
        if counter > 0:
            enemy.take_damage(counter)

        self.blog(" ".join(parts), color)

        # Check outcomes
        if not enemy.is_alive():
            self.blog(f"{enemy.name} is defeated!", LOG_COLOR_ENEMY)
            g.battle_result = "victory"
            g.battle_sub_state = BATTLE_RESULT
            return

        if player.infection >= 100:
            self.blog("The infection takes over.", LOG_COLOR_DAMAGE)
            g.battle_result = "defeat"
            g.battle_sub_state = BATTLE_RESULT
            return

        if not player.is_alive():
            self.blog("You fall.", LOG_COLOR_DAMAGE)
            g.battle_result = "defeat"
            g.battle_sub_state = BATTLE_RESULT
            return

        if player.infection >= 75:
            hp_loss = 5
            player.take_damage(hp_loss)
            self.blog(
                f"Critical infection burns through you. -{hp_loss} HP.",
                LOG_COLOR_INFECTION
            )
            if not player.is_alive():
                self.blog("You succumb to the infection.", LOG_COLOR_DAMAGE)
                g.battle_result = "defeat"
                g.battle_sub_state = BATTLE_RESULT
                return

        g.battle_sub_state = BATTLE_PLAYER_TURN

    # ── Items in battle ───────────────────────────────────────

    def open_battle_items(self):
        g = self.game
        g.battle_consumables = []
        for item_id, qty in g.player.inventory.items():
            if item_id.startswith("search_"):
                continue
            data = g.items_by_id.get(item_id)
            if data is None:
                continue
            if data.get("category") != "consumable":
                continue
            if not data.get("usable_in_battle", False):
                continue
            g.battle_consumables.append((item_id, data, qty))

        if not g.battle_consumables:
            self.blog("No usable items.", LOG_COLOR_WARN)
            return
        g.battle_item_mode = True

    def use_battle_item(self, index):
        g = self.game
        item_id, item_data, _ = g.battle_consumables[index]
        if not g.player.remove_item(item_id):
            self.blog("Cannot use item.", LOG_COLOR_WARN)
            return

        effects = item_data.get("effects", {})
        heal = effects.get("heal_hp", 0)
        red_inf = effects.get("reduce_infection", 0)
        supp = effects.get("apply_suppressant", 0)

        parts = [f"Used {item_data.get('name', item_id)}."]
        if heal > 0:
            g.player.heal(heal)
            parts.append(f"+{heal} HP.")
            g.sound_manager.play_sfx("heal")
        if red_inf > 0:
            g.player.reduce_infection(red_inf)
            parts.append(f"-{red_inf}% inf.")
        if supp > 0:
            g.player.suppressant_battles_left = supp
            parts.append(f"Suppressant: {supp} battles.")

        self.blog(" ".join(parts), LOG_COLOR_HEAL)
        g.battle_item_mode = False
        self.start_reaction_phase()

    # ── Skills ────────────────────────────────────────────────

    def open_battle_skills(self):
        self.game.battle_skill_mode = True

    def handle_battle_skill_input(self, key):
        import pygame # type: ignore
        g = self.game
        if key == pygame.K_1:
            if g.player.infection >= INFECTED_STRIKE_THRESHOLD:
                g.battle_skill_mode = False
                self.start_qte("infected_strike")
            else:
                self.blog(
                    f"Need {INFECTED_STRIKE_THRESHOLD}% infection.",
                    LOG_COLOR_WARN
                )
        elif key == pygame.K_2:
            if g.player.infection >= MUTANT_BURST_THRESHOLD:
                g.battle_skill_mode = False
                self.start_qte("mutant_burst")
            else:
                self.blog(
                    f"Need {MUTANT_BURST_THRESHOLD}% infection.",
                    LOG_COLOR_WARN
                )

    # ── Flee ──────────────────────────────────────────────────

    def get_escape_chance(self):
        g = self.game
        if g.current_enemy is None or g.current_enemy.is_boss:
            return 0
        chance = g.current_enemy.escape_chance
        chance -= g.player.escape_attempts * ESCAPE_PENALTY_PER_ATTEMPT
        hp_pct = (g.player.hp / g.player.max_hp) * 100
        if hp_pct < LOW_HP_THRESHOLD_PERCENT:
            chance -= LOW_HP_ESCAPE_PENALTY
        return max(0, chance)

    def player_flee(self):
        g = self.game
        if g.current_enemy.is_boss:
            self.blog(
                random.choice([
                    "There's nowhere to run from this.",
                    "Fleeing is not an option here.",
                ]),
                LOG_COLOR_WARN
            )
            return

        if g.player.escape_attempts >= MAX_ESCAPE_ATTEMPTS:
            self.blog("No more chances to run.", LOG_COLOR_WARN)
            return

        g.player.escape_attempts += 1
        chance = self.get_escape_chance()

        if random.randint(1, 100) <= chance:
            self.blog(
                random.choice([
                    "You find an opening and run!",
                    "You break away and escape!",
                ]),
                LOG_COLOR_FLEE
            )
            g.battle_result = "escaped"
            g.battle_sub_state = BATTLE_RESULT
            g.sound_manager.play_sfx("flee")
        else:
            left = MAX_ESCAPE_ATTEMPTS - g.player.escape_attempts
            self.blog(
                f"No opening! ({chance}% chance, {left} attempts left)",
                LOG_COLOR_FLEE
            )
            self.start_reaction_phase()