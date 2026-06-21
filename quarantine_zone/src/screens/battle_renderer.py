"""
battle_renderer.py
Renders battle screen: enemy info, battle log, menus, QTE overlay.
"""
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PANEL_BORDER_COLOR, TEXT_COLOR, ACCENT_COLOR,
    WHITE, RED, GREEN, YELLOW,
    PADDING,
    BATTLE_ENEMY_AREA_HEIGHT, BATTLE_MENU_HEIGHT,
    BATTLE_REACTION, BATTLE_QTE, BATTLE_RESULT,
    QTE_BAR_WIDTH, QTE_BAR_HEIGHT, QTE_MARKER_WIDTH,
    INFECTED_STRIKE_THRESHOLD, INFECTED_STRIKE_MULTIPLIER,
    MUTANT_BURST_THRESHOLD, MUTANT_BURST_MULTIPLIER,
    MAX_ESCAPE_ATTEMPTS,
)
from src.systems.battle_system import LOG_COLOR_DEFAULT

GRAY_DISABLED = (110, 110, 120)


class BattleRenderer:
    def __init__(self, game):
        self.game = game

    def draw_battle(self):
        g = self.game
        enemy_rect = pygame.Rect(
            PADDING, PADDING,
            WINDOW_WIDTH - PADDING * 2, BATTLE_ENEMY_AREA_HEIGHT
        )
        menu_rect = pygame.Rect(
            PADDING, PADDING + BATTLE_ENEMY_AREA_HEIGHT + PADDING,
            WINDOW_WIDTH - PADDING * 2, BATTLE_MENU_HEIGHT
        )
        g.ui_renderer.draw_panel(enemy_rect)
        g.ui_renderer.draw_panel(menu_rect)
        self._draw_enemy_info(enemy_rect)
        self._draw_battle_menu(menu_rect)
        if g.battle_sub_state == BATTLE_QTE:
            self._draw_qte_overlay()
        g.ui_renderer.draw_message_bar()

    def _draw_enemy_info(self, rect):
        g = self.game
        enemy = g.current_enemy
        player = g.player

        g.screen.blit(
            g.header_font.render(enemy.name, True, RED),
            (rect.x + 15, rect.y + 15)
        )
        hints = {
            "heavy": "Moves slowly but strikes with full force...",
            "fast": "Twitches constantly, hard to read...",
            "toxic": "Dark fluid drips from its wounds...",
            "mixed": "Behaviour is completely erratic...",
        }
        g.screen.blit(
            g.small_font.render(hints.get(enemy.attack_pattern, "..."), True, YELLOW),
            (rect.x + 15, rect.y + 50)
        )

        rx = rect.x + rect.width // 2 + 20
        left = MAX_ESCAPE_ATTEMPTS - player.escape_attempts
        info = [
            (f"Enemy HP: {enemy.hp}/{enemy.max_hp}", RED),
            (f"Your HP:  {player.hp}/{player.max_hp}",
             GREEN if player.hp > 30 else RED),
            (f"Infection: {player.infection}% ({player.get_infection_state()})",
             g.ui_renderer.get_infection_color(player.infection)),
            (f"Suppressant: {player.suppressant_battles_left}", TEXT_COLOR),
            (f"Escape attempts left: {left}", YELLOW),
        ]
        y = rect.y + 20
        for text, color in info:
            g.screen.blit(g.small_font.render(text, True, color), (rx, y))
            y += 26

        bw, bh = 200, 14
        er = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        pygame.draw.rect(g.screen, GRAY_DISABLED, pygame.Rect(rx, y, bw, bh), border_radius=4)
        pygame.draw.rect(g.screen, RED, pygame.Rect(rx, y, int(bw * er), bh), border_radius=4)
        y += bh + 6
        pr = player.hp / player.max_hp if player.max_hp > 0 else 0
        pygame.draw.rect(g.screen, GRAY_DISABLED, pygame.Rect(rx, y, bw, bh), border_radius=4)
        pygame.draw.rect(g.screen, GREEN, pygame.Rect(rx, y, int(bw * pr), bh), border_radius=4)

    def _draw_battle_menu(self, rect):
        g = self.game
        lx = rect.x + 15
        ly = rect.y + 15
        lw = rect.width // 2 - 30

        g.screen.blit(g.small_font.render("Battle Log:", True, ACCENT_COLOR), (lx, ly))
        ly += 26
        pygame.draw.line(g.screen, PANEL_BORDER_COLOR, (lx, ly), (lx + lw, ly), 1)
        ly += 6

        for entry in g.battle_log[-10:]:
            if isinstance(entry, tuple):
                text, color = entry
            else:
                text, color = entry, LOG_COLOR_DEFAULT
            for line in g.ui_renderer.wrap_text(text, g.small_font, lw):
                g.screen.blit(g.small_font.render(line, True, color), (lx, ly))
                ly += 20

        ax = rect.x + rect.width // 2 + 20
        ay = rect.y + 15

        if g.battle_sub_state == BATTLE_RESULT:
            if g.battle_result == "victory":
                s, c = "VICTORY! Press ENTER.", GREEN
            elif g.battle_result == "defeat":
                s, c = "DEFEATED. Press ENTER.", RED
            else:
                s, c = "Escaped. Press ENTER.", YELLOW
            g.screen.blit(g.text_font.render(s, True, c), (ax, ay))
            return

        if g.battle_sub_state == BATTLE_QTE:
            g.screen.blit(
                g.small_font.render("Press SPACE in green zone!", True, ACCENT_COLOR),
                (ax, ay)
            )
            return

        if g.battle_sub_state == BATTLE_REACTION:
            g.screen.blit(g.small_font.render("Choose reaction:", True, ACCENT_COLOR), (ax, ay))
            ay += 28
            for label, hint in [
                ("1. Dodge", "(best vs toxic)"),
                ("2. Block", "(best vs heavy)"),
                ("3. Counter", "(best vs fast)"),
            ]:
                g.screen.blit(g.small_font.render(label, True, WHITE), (ax, ay))
                g.screen.blit(g.small_font.render(hint, True, GRAY_DISABLED), (ax + 120, ay))
                ay += 24
            return

        if g.battle_item_mode:
            g.screen.blit(
                g.small_font.render("Use item (ESC cancel):", True, ACCENT_COLOR),
                (ax, ay)
            )
            ay += 28
            for i, (_, data, qty) in enumerate(g.battle_consumables):
                g.screen.blit(
                    g.small_font.render(f"{i+1}. {data.get('name')} (x{qty})", True, WHITE),
                    (ax, ay)
                )
                ay += 24
            return

        if g.battle_skill_mode:
            g.screen.blit(
                g.small_font.render("Skills (ESC cancel):", True, ACCENT_COLOR),
                (ax, ay)
            )
            ay += 28
            a = g.player.infection >= INFECTED_STRIKE_THRESHOLD
            b = g.player.infection >= MUTANT_BURST_THRESHOLD
            g.screen.blit(
                g.small_font.render(
                    f"1. Infected Strike x{INFECTED_STRIKE_MULTIPLIER}"
                    f"  [{INFECTED_STRIKE_THRESHOLD}% inf]",
                    True, WHITE if a else GRAY_DISABLED
                ),
                (ax, ay)
            )
            ay += 24
            g.screen.blit(
                g.small_font.render(
                    f"2. Mutant Burst x{MUTANT_BURST_MULTIPLIER}"
                    f"  [{MUTANT_BURST_THRESHOLD}% inf]",
                    True, WHITE if b else GRAY_DISABLED
                ),
                (ax, ay)
            )
            return

        # Player turn
        g.screen.blit(g.small_font.render("Your turn:", True, ACCENT_COLOR), (ax, ay))
        ay += 28
        ca = MAX_ESCAPE_ATTEMPTS - g.player.escape_attempts
        cf = g.battle_system.get_escape_chance()
        can_flee = ca > 0 and not g.current_enemy.is_boss
        flee_text = (
            "4. Flee (impossible)" if g.current_enemy.is_boss
            else f"4. Flee ({cf}%, {ca} left)"
        )
        for text, color in [
            ("1. Attack", WHITE), ("2. Item", WHITE),
            ("3. Skill", WHITE),
            (flee_text, WHITE if can_flee else GRAY_DISABLED),
        ]:
            g.screen.blit(g.small_font.render(text, True, color), (ax, ay))
            ay += 28

        g.screen.blit(
            g.small_font.render(
                "1-Attack  2-Item  3-Skill  4-Flee  |  F5-Save  F9-Load  ESC-Pause",
                True, GRAY_DISABLED
            ),
            (rect.x + 15, rect.bottom - 30)
        )

    def _draw_qte_overlay(self):
        g = self.game
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        g.screen.blit(overlay, (0, 0))

        bar = pygame.Rect(g.qte_bar_x, g.qte_bar_y, QTE_BAR_WIDTH, QTE_BAR_HEIGHT)
        pygame.draw.rect(g.screen, GRAY_DISABLED, bar, border_radius=6)
        pygame.draw.rect(g.screen, YELLOW,
            pygame.Rect(g.qte_yellow_start, g.qte_bar_y,
                        g.qte_yellow_end - g.qte_yellow_start, QTE_BAR_HEIGHT),
            border_radius=6)
        pygame.draw.rect(g.screen, GREEN,
            pygame.Rect(g.qte_green_start, g.qte_bar_y,
                        g.qte_green_end - g.qte_green_start, QTE_BAR_HEIGHT),
            border_radius=6)
        pygame.draw.rect(g.screen, WHITE,
            pygame.Rect(int(g.qte_marker_x), g.qte_bar_y - 6,
                        QTE_MARKER_WIDTH, QTE_BAR_HEIGHT + 12),
            border_radius=2)

        h = g.text_font.render("Press SPACE in green zone!", True, WHITE)
        g.screen.blit(h, h.get_rect(center=(WINDOW_WIDTH // 2, g.qte_bar_y - 30)))

        skill_labels = {
            "infected_strike": ("Infected Strike", (220, 80, 80)),
            "mutant_burst": ("Mutant Burst", (180, 50, 200)),
        }
        if g.qte_skill in skill_labels:
            text, color = skill_labels[g.qte_skill]
            surface = g.text_font.render(text, True, color)
            g.screen.blit(surface, surface.get_rect(
                center=(WINDOW_WIDTH // 2, g.qte_bar_y + QTE_BAR_HEIGHT + 30)
            ))