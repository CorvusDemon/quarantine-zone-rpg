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
    YELLOW,
    PADDING,
)


GRAY_DISABLED = (110, 110, 120)


class InventoryScreen:
    def __init__(self, game):
        self.game = game

    def draw(self):
        self.game.screen.fill(BACKGROUND_COLOR)

        title = self.game.title_font.render("INVENTORY", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.game.screen.blit(title, title_rect)

        panel_rect = pygame.Rect(
            PADDING, 100,
            WINDOW_WIDTH - PADDING * 2,
            WINDOW_HEIGHT - 160,
        )
        self.game.draw_panel(panel_rect)

        self.draw_inventory_content(panel_rect)

        hint = self.game.small_font.render(
            "I or ESC - close inventory", True, TEXT_COLOR
        )
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.game.screen.blit(hint, hint_rect)

    def draw_inventory_content(self, rect):
        consumables = []
        materials = []
        key_items = []

        for item_id, quantity in self.game.player.inventory.items():
            if item_id.startswith("search_"):
                continue
            item_data = self.game.items_by_id.get(item_id)
            if item_data is None:
                continue
            category = item_data.get("category", "")
            entry = (item_id, item_data, quantity)
            if category == "consumable":
                consumables.append(entry)
            elif category == "material":
                materials.append(entry)
            elif category == "key_item":
                key_items.append(entry)

        col_width = (rect.width - 60) // 3
        col1_x = rect.x + 20
        col2_x = col1_x + col_width + 20
        col3_x = col2_x + col_width + 20
        start_y = rect.y + 20

        self.draw_category(col1_x, start_y, col_width, "Consumables", consumables)
        self.draw_category(col2_x, start_y, col_width, "Materials", materials)
        self.draw_category(col3_x, start_y, col_width, "Key Items", key_items)

    def draw_category(self, x, y, width, title, entries):
        title_surface = self.game.header_font.render(title, True, ACCENT_COLOR)
        self.game.screen.blit(title_surface, (x, y))
        y += 40

        if not entries:
            empty = self.game.small_font.render("(empty)", True, GRAY_DISABLED)
            self.game.screen.blit(empty, (x, y))
            return

        for item_id, item_data, quantity in entries:
            name = item_data.get("name", item_id)
            line = f"{name} x{quantity}"
            rendered = self.game.text_font.render(line, True, WHITE)
            self.game.screen.blit(rendered, (x, y))
            y += 28

            description = item_data.get("description", "")
            wrapped = self.game.wrap_text(description, self.game.small_font, width)
            for wline in wrapped:
                desc_rendered = self.game.small_font.render(wline, True, TEXT_COLOR)
                self.game.screen.blit(desc_rendered, (x + 10, y))
                y += 20
            y += 10