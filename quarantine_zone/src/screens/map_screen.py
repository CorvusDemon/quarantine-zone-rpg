import pygame # type: ignore
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    PANEL_COLOR,
    PANEL_BORDER_COLOR,
    TEXT_COLOR,
    ACCENT_COLOR,
    WHITE,
    RED,
    GREEN,
    PADDING,
    MAP_NODE_RADIUS,
    MAP_NODE_RADIUS_CURRENT,
    MAP_CONNECTION_WIDTH,
)

GRAY_DISABLED = (110, 110, 120)
NODE_VISITED_COLOR    = (60, 160, 90)   
NODE_CURRENT_COLOR    = (130, 180, 255) 
NODE_UNKNOWN_COLOR    = (80, 80, 95) 
NODE_BORDER_COLOR     = (200, 200, 210)
CONNECTION_COLOR      = (100, 100, 115)
CONNECTION_OPEN_COLOR = (80, 140, 80)
DANGER_COLOR          = (200, 70, 70)
SAFE_COLOR            = (60, 160, 90)


class MapScreen:
    def __init__(self, game):
        self.game = game

    def draw(self):
        g = self.game
        screen = g.screen

        screen.fill(BACKGROUND_COLOR)

        title = g.title_font.render("MAP", True, ACCENT_COLOR)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 45)))

        panel = pygame.Rect(
            PADDING, 80,
            WINDOW_WIDTH - PADDING * 2,
            WINDOW_HEIGHT - 170
        )
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=10)
        pygame.draw.rect(screen, PANEL_BORDER_COLOR, panel, width=2, border_radius=10)

        self._draw_connections(panel)

        self._draw_nodes(panel)

        self._draw_info_sidebar(panel)

        self._draw_legend()

        hint = g.small_font.render(
            "M or ESC — close map", True, TEXT_COLOR
        )
        screen.blit(hint, hint.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)
        ))

    def _get_node_screen_pos(self, location, panel):
        map_area_w = int(panel.width * 0.68)
        map_area_h = panel.height - 40

        raw_x = location.get("map_x", 500)
        raw_y = location.get("map_y", 300)

        norm_x = (raw_x - 150) / (1150 - 150)
        norm_y = (raw_y - 100) / (420 - 100)

        screen_x = panel.x + 20 + int(norm_x * (map_area_w - 40))
        screen_y = panel.y + 20 + int(norm_y * (map_area_h - 40))

        return screen_x, screen_y

    def _draw_connections(self, panel):
        g = self.game
        locations = g.data.get("locations", [])
        loc_by_id = g.locations_by_id
        drawn = set()

        for loc in locations:
            loc_id = loc.get("id")
            x1, y1 = self._get_node_screen_pos(loc, panel)

            for conn in loc.get("connections", []):
                target_id = conn.get("target_id")
                if target_id not in loc_by_id:
                    continue

                pair = tuple(sorted([loc_id, target_id]))
                if pair in drawn:
                    continue
                drawn.add(pair)

                target = loc_by_id[target_id]
                x2, y2 = self._get_node_screen_pos(target, panel)

                # Connection color
                reqs = conn.get("requirements", [])
                is_open = g.check_requirements(reqs)

                if is_open:
                    color = CONNECTION_OPEN_COLOR
                else:
                    color = CONNECTION_COLOR

                pygame.draw.line(g.screen, color, (x1, y1), (x2, y2),
                                 MAP_CONNECTION_WIDTH)

                # Lock on a closed path
                if not is_open:
                    mid_x = (x1 + x2) // 2
                    mid_y = (y1 + y2) // 2
                    lock = g.small_font.render("🔒", True, GRAY_DISABLED)
                    g.screen.blit(lock, (mid_x - 8, mid_y - 8))

    def _draw_nodes(self, panel):
        g = self.game
        player = g.player
        locations = g.data.get("locations", [])

        visited = getattr(player, "visited_locations", set())

        for loc in locations:
            loc_id = loc.get("id")
            x, y = self._get_node_screen_pos(loc, panel)

            is_current = loc_id == player.current_location_id
            is_visited = loc_id in visited
            is_safe = loc.get("safe_zone", False)

            # Radius
            radius = MAP_NODE_RADIUS_CURRENT if is_current else MAP_NODE_RADIUS

            if is_current:
                fill_color = NODE_CURRENT_COLOR
            elif is_visited:
                fill_color = NODE_VISITED_COLOR
            else:
                fill_color = NODE_UNKNOWN_COLOR

            # Shadow
            pygame.draw.circle(g.screen, (0, 0, 0), (x + 3, y + 3), radius)

            # Main circle
            pygame.draw.circle(g.screen, fill_color, (x, y), radius)

            # Border -pulsating for the current location
            border_color = ACCENT_COLOR if is_current else NODE_BORDER_COLOR
            border_w = 3 if is_current else 1
            pygame.draw.circle(g.screen, border_color, (x, y), radius, border_w)

            # Security icon
            if is_safe and is_visited:
                safe_dot = pygame.Rect(x + radius - 6, y - radius - 2, 8, 8)
                pygame.draw.rect(g.screen, SAFE_COLOR, safe_dot, border_radius=4)
            elif not is_safe and is_visited:
                danger_dot = pygame.Rect(x + radius - 6, y - radius - 2, 8, 8)
                pygame.draw.rect(g.screen, DANGER_COLOR, danger_dot, border_radius=4)

            # Node name
            name = loc.get("name", loc_id)
            short_names = {
                "Police Station": "Police\nStation",
                "Ruined Street": "Street",
                "Metro": "Metro",
                "City Hospital": "Hospital",
                "Underground Laboratory": "Lab",
                "Rooftop": "Rooftop",
            }
            display_name = short_names.get(name, name)

            text_color = WHITE if is_visited or is_current else GRAY_DISABLED
            name_surf = g.small_font.render(display_name, True, text_color)
            g.screen.blit(name_surf, name_surf.get_rect(
                center=(x, y + radius + 14)
            ))

            # Marker for current position
            if is_current:
                marker = g.small_font.render("▼", True, ACCENT_COLOR)
                g.screen.blit(marker, marker.get_rect(
                    center=(x, y - radius - 12)
                ))

    def _draw_info_sidebar(self, panel):
        g = self.game
        player = g.player

        sidebar_x = panel.x + int(panel.width * 0.70)
        sidebar_y = panel.y + 15
        sidebar_w = panel.width - int(panel.width * 0.70) - 15

        # Separator
        pygame.draw.line(
            g.screen, PANEL_BORDER_COLOR,
            (sidebar_x - 5, panel.y + 10),
            (sidebar_x - 5, panel.bottom - 10),
            1
        )

        # Sidebar header
        g.screen.blit(
            g.header_font.render("Status", True, ACCENT_COLOR),
            (sidebar_x, sidebar_y)
        )
        sidebar_y += 38

        # Current Location
        current_loc = g.get_current_location()
        if current_loc:
            loc_name = current_loc.get("name", "Unknown")
            g.screen.blit(
                g.small_font.render("Location:", True, GRAY_DISABLED),
                (sidebar_x, sidebar_y)
            )
            sidebar_y += 20
            g.screen.blit(
                g.small_font.render(loc_name, True, WHITE),
                (sidebar_x, sidebar_y)
            )
            sidebar_y += 24

            safe = current_loc.get("safe_zone", False)
            safe_text = "✓ Safe Zone" if safe else "✗ Danger Zone"
            safe_color = SAFE_COLOR if safe else DANGER_COLOR
            g.screen.blit(
                g.small_font.render(safe_text, True, safe_color),
                (sidebar_x, sidebar_y)
            )
            sidebar_y += 28

        # Separator
        pygame.draw.line(
            g.screen, PANEL_BORDER_COLOR,
            (sidebar_x, sidebar_y),
            (sidebar_x + sidebar_w, sidebar_y), 1
        )
        sidebar_y += 10

        # HP
        hp_color = GREEN if player.hp > 30 else RED
        g.screen.blit(
            g.small_font.render(
                f"HP: {player.hp}/{player.max_hp}", True, hp_color
            ),
            (sidebar_x, sidebar_y)
        )
        sidebar_y += 4
        self._draw_mini_bar(
            sidebar_x, sidebar_y + 18,
            sidebar_w, 10,
            player.hp, player.max_hp,
            GREEN, RED
        )
        sidebar_y += 36

        # Infection
        inf_color = g.get_infection_color(player.infection)
        g.screen.blit(
            g.small_font.render(
                f"Infection: {player.infection}%", True, inf_color
            ),
            (sidebar_x, sidebar_y)
        )
        sidebar_y += 4
        self._draw_mini_bar(
            sidebar_x, sidebar_y + 18,
            sidebar_w, 10,
            player.infection, 100,
            RED, GRAY_DISABLED
        )
        sidebar_y += 36

        # Infection Stage
        state = player.get_infection_state()
        g.screen.blit(
            g.small_font.render(f"Stage: {state}", True, inf_color),
            (sidebar_x, sidebar_y)
        )
        sidebar_y += 28

        # Separator
        pygame.draw.line(
            g.screen, PANEL_BORDER_COLOR,
            (sidebar_x, sidebar_y),
            (sidebar_x + sidebar_w, sidebar_y), 1
        )
        sidebar_y += 10

        # Goals
        g.screen.blit(
            g.small_font.render("Objectives:", True, ACCENT_COLOR),
            (sidebar_x, sidebar_y)
        )
        sidebar_y += 22

        for text, done in self._get_objectives():
            color = GRAY_DISABLED if done else WHITE
            prefix = "✓ " if done else "• "
            # Перенос текста
            wrapped = g.wrap_text(prefix + text, g.small_font, sidebar_w)
            for line in wrapped:
                g.screen.blit(
                    g.small_font.render(line, True, color),
                    (sidebar_x, sidebar_y)
                )
                sidebar_y += 18
            sidebar_y += 2

    def _draw_mini_bar(self, x, y, width, height, value, max_value, color, bg_color):
        ratio = max(0.0, min(1.0, value / max_value)) if max_value > 0 else 0
        bg = pygame.Rect(x, y, width, height)
        fg = pygame.Rect(x, y, int(width * ratio), height)
        pygame.draw.rect(self.game.screen, bg_color, bg, border_radius=4)
        if fg.width > 0:
            pygame.draw.rect(self.game.screen, color, fg, border_radius=4)

    def _get_objectives(self):
        g = self.game
        p = g.player
        visited = getattr(p, "visited_locations", set())

        objectives = [
            (
                "Find a crowbar",
                p.has_item("crowbar")
            ),
            (
                "Find a flashlight",
                p.has_item("flashlight")
            ),
            (
                "Reach the Metro",
                "metro" in visited
            ),
            (
                "Find a Gas Mask",
                p.has_item("gas_mask")
            ),
            (
                "Reach the Hospital",
                "hospital" in visited
            ),
            (
                "Get the Access Card",
                p.has_item("access_card")
            ),
            (
                "Reach the Laboratory",
                "laboratory" in visited
            ),
            (
                "Reach the Rooftop",
                "rooftop" in visited
            ),
        ]

       # Show only the current + next 3 goals
        first_incomplete = next(
            (i for i, (_, done) in enumerate(objectives) if not done),
            len(objectives)
        )

        start = max(0, first_incomplete - 1)
        end = min(len(objectives), start + 5)
        return objectives[start:end]

    def _draw_legend(self):
        g = self.game
        items = [
            (NODE_CURRENT_COLOR,  "You are here"),
            (NODE_VISITED_COLOR,  "Visited"),
            (NODE_UNKNOWN_COLOR,  "Unknown"),
            (CONNECTION_OPEN_COLOR, "Path open"),
            (CONNECTION_COLOR,    "Path locked"),
        ]

        x = PADDING + 10
        y = WINDOW_HEIGHT - 55

        for color, label in items:
            pygame.draw.circle(g.screen, color, (x + 6, y + 7), 6)
            pygame.draw.circle(g.screen, NODE_BORDER_COLOR, (x + 6, y + 7), 6, 1)
            g.screen.blit(
                g.small_font.render(label, True, TEXT_COLOR),
                (x + 16, y)
            )
            x += 160