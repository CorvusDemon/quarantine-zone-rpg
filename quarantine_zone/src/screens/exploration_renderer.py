"""
exploration_renderer.py
Renders exploration screen: location info, status, actions, search QTE.
"""
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PANEL_COLOR, PANEL_BORDER_COLOR,
    TEXT_COLOR, ACCENT_COLOR,
    WHITE, RED, GREEN, YELLOW,
    PADDING,
    LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH,
    TOP_PANEL_HEIGHT, BOTTOM_PANEL_HEIGHT,
    QTE_MARKER_WIDTH,
)

GRAY_DISABLED = (110, 110, 120)


class ExplorationRenderer:
    def __init__(self, game):
        self.game = game

    def draw_exploration(self):
        g = self.game
        location = g.get_current_location()

        if location is None:
            g.screen.blit(
                g.header_font.render("No location loaded.", True, RED),
                (PADDING, PADDING)
            )
            return

        left_top = pygame.Rect(PADDING, PADDING, LEFT_PANEL_WIDTH, TOP_PANEL_HEIGHT)
        left_bot = pygame.Rect(
            PADDING, PADDING + TOP_PANEL_HEIGHT + PADDING,
            LEFT_PANEL_WIDTH, BOTTOM_PANEL_HEIGHT
        )
        right = pygame.Rect(
            PADDING + LEFT_PANEL_WIDTH + PADDING, PADDING,
            RIGHT_PANEL_WIDTH,
            TOP_PANEL_HEIGHT + PADDING + BOTTOM_PANEL_HEIGHT
        )

        g.ui_renderer.draw_panel(left_top)
        g.ui_renderer.draw_panel(left_bot)
        g.ui_renderer.draw_panel(right)

        self._draw_location_info(left_top, location)
        self._draw_player_status(left_bot)
        self._draw_actions_panel(right, location)

        g.ui_renderer.draw_message_bar()

        if g.search_qte_active:
            self._draw_search_qte_overlay()

    def _draw_location_info(self, rect, location):
        g = self.game
        g.screen.blit(
            g.header_font.render(location.get("name", "Unknown"), True, ACCENT_COLOR),
            (rect.x + 15, rect.y + 15)
        )
        lines = g.ui_renderer.wrap_text(
            location.get("description", ""), g.text_font, rect.width - 30
        )
        y = rect.y + 70
        for line in lines:
            g.screen.blit(g.text_font.render(line, True, TEXT_COLOR), (rect.x + 15, y))
            y += 32

    def _draw_player_status(self, rect):
        g = self.game
        p = g.player
        g.screen.blit(
            g.header_font.render("Status", True, ACCENT_COLOR),
            (rect.x + 15, rect.y + 15)
        )
        inf_color = g.ui_renderer.get_infection_color(p.infection)
        key_items = [
            g.get_item_name(i)
            for i in ["crowbar", "flashlight", "gas_mask", "access_card"]
            if p.has_item(i)
        ]
        lines = [
            (f"HP: {p.hp} / {p.max_hp}", GREEN if p.hp > 30 else RED),
            (f"Infection: {p.infection}% ({p.get_infection_state()})", inf_color),
            (f"Suppressant: {p.suppressant_battles_left} battles", TEXT_COLOR),
            (f"Key items: {', '.join(key_items) if key_items else 'none'}", TEXT_COLOR),
        ]
        y = rect.y + 60
        for text, color in lines:
            g.screen.blit(g.small_font.render(text, True, color), (rect.x + 15, y))
            y += 30

    def _draw_actions_panel(self, rect, location):
        g = self.game
        g.screen.blit(
            g.header_font.render("Actions", True, ACCENT_COLOR),
            (rect.x + 15, rect.y + 15)
        )

        connections = location.get("connections", [])
        special = g.exploration_system.get_available_special_actions(location)

        CTRL_H = 130
        MSG_H = 55
        ctrl_y = rect.y + rect.height - CTRL_H - MSG_H
        max_y = ctrl_y - 10
        y = rect.y + 60

        # Move
        g.screen.blit(g.small_font.render("Move:", True, ACCENT_COLOR), (rect.x + 15, y))
        y += 22
        for i, conn in enumerate(connections):
            if y >= max_y:
                break
            reqs = conn.get("requirements", [])
            ok = g.exploration_system.check_requirements(reqs)
            color = WHITE if ok else GRAY_DISABLED
            g.screen.blit(
                g.small_font.render(f"{i+1}. {conn.get('label','?')}", True, color),
                (rect.x + 15, y)
            )
            y += 20
            if not ok and reqs and y < max_y:
                req_text = "   (" + ", ".join(f"needs {r.get('id')}" for r in reqs) + ")"
                g.screen.blit(g.small_font.render(req_text, True, RED), (rect.x + 25, y))
                y += 18

        # Special
        if y < max_y:
            y += 6
            g.screen.blit(
                g.small_font.render("Special:", True, ACCENT_COLOR),
                (rect.x + 15, y)
            )
            y += 22
            letters = ["Q", "W", "E", "R", "T", "Y", "U", "O"]
            if not special:
                g.screen.blit(
                    g.small_font.render("Nothing here.", True, GRAY_DISABLED),
                    (rect.x + 15, y)
                )
                y += 20
            else:
                for i, action in enumerate(special):
                    if y >= max_y:
                        break
                    g.screen.blit(
                        g.small_font.render(
                            f"{letters[i]}. {action.get('name','?')}", True, WHITE
                        ),
                        (rect.x + 15, y)
                    )
                    y += 20

        # Search
        if y < max_y and location.get("search_enabled"):
            y += 6
            loc_id = location.get("id")
            used = g.player.inventory.get(f"search_{loc_id}", 0)
            limit = location.get("search_attempts_limit", 0)
            remaining = max(0, limit - used)
            color = WHITE if remaining > 0 else GRAY_DISABLED
            g.screen.blit(
                g.small_font.render(f"S. Search ({remaining} left)", True, color),
                (rect.x + 15, y)
            )

        # Divider + controls
        pygame.draw.line(
            g.screen, PANEL_BORDER_COLOR,
            (rect.x + 10, ctrl_y - 6),
            (rect.x + rect.width - 10, ctrl_y - 6), 1
        )
        ctrl = pygame.Rect(rect.x + 10, ctrl_y, rect.width - 20, CTRL_H)
        pygame.draw.rect(g.screen, (20, 20, 26), ctrl, border_radius=6)
        pygame.draw.rect(g.screen, PANEL_BORDER_COLOR, ctrl, width=1, border_radius=6)
        g.screen.blit(
            g.small_font.render("Controls", True, ACCENT_COLOR),
            (ctrl.x + 10, ctrl.y + 7)
        )
        controls = [
            ("1-9", "Move"), ("Q-Y", "Special"), ("S", "Search"),
            ("I", "Inventory"), ("C", "Crafting"),
            ("N", "Notes"), ("M", "Map"),
            ("F5", "Quick Save"), ("F9", "Quick Load"), ("ESC", "Pause"),
        ]
        col1_x = ctrl.x + 10
        col2_x = ctrl.x + ctrl.width // 2
        row_y = ctrl.y + 28
        row_h = 18
        for i, (k, v) in enumerate(controls):
            x = col1_x if i < 5 else col2_x
            row = i if i < 5 else i - 5
            g.screen.blit(g.small_font.render(k, True, YELLOW), (x, row_y + row * row_h))
            g.screen.blit(g.small_font.render(v, True, TEXT_COLOR), (x + 40, row_y + row * row_h))

    def _draw_search_qte_overlay(self):
        from settings import SEARCH_QTE_BAR_WIDTH, SEARCH_QTE_BAR_HEIGHT
        g = self.game

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        g.screen.blit(overlay, (0, 0))

        pw = SEARCH_QTE_BAR_WIDTH + 80
        ph = 160
        px = WINDOW_WIDTH // 2 - pw // 2
        py = WINDOW_HEIGHT // 2 - ph // 2
        panel = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(g.screen, PANEL_COLOR, panel, border_radius=12)
        pygame.draw.rect(g.screen, PANEL_BORDER_COLOR, panel, width=2, border_radius=12)

        title = g.text_font.render("SEARCHING...", True, ACCENT_COLOR)
        g.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, py + 28)))

        bar_x = g.search_qte_bar_x
        bar_y = py + 60

        pygame.draw.rect(g.screen, GRAY_DISABLED,
            pygame.Rect(bar_x, bar_y, SEARCH_QTE_BAR_WIDTH, SEARCH_QTE_BAR_HEIGHT),
            border_radius=6)
        pygame.draw.rect(g.screen, YELLOW,
            pygame.Rect(g.search_qte_yellow_start, bar_y,
                        g.search_qte_yellow_end - g.search_qte_yellow_start,
                        SEARCH_QTE_BAR_HEIGHT),
            border_radius=6)
        pygame.draw.rect(g.screen, GREEN,
            pygame.Rect(g.search_qte_green_start, bar_y,
                        g.search_qte_green_end - g.search_qte_green_start,
                        SEARCH_QTE_BAR_HEIGHT),
            border_radius=6)
        pygame.draw.rect(g.screen, WHITE,
            pygame.Rect(int(g.search_qte_marker_x), bar_y - 6,
                        QTE_MARKER_WIDTH, SEARCH_QTE_BAR_HEIGHT + 12),
            border_radius=2)

        hint = g.small_font.render(
            "SPACE — stop the marker!   Green = bonus loot", True, WHITE
        )
        g.screen.blit(hint, hint.get_rect(
            center=(WINDOW_WIDTH // 2, bar_y + SEARCH_QTE_BAR_HEIGHT + 22)
        ))