import pygame  # type: ignore

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    ACCENT_COLOR,
    WHITE,
    RED,
    GREEN,
    YELLOW,
    PADDING,
)


GRAY_DISABLED = (110, 110, 120)


class CraftingScreen:
    def __init__(self, game):
        self.game = game
        self.selected_index = 0

    def reset(self):
        self.selected_index = 0

    def get_available_recipes(self):
        recipes = self.game.data.get("recipes", [])
        result = []
        for recipe in recipes:
            if self.is_recipe_unlocked(recipe):
                result.append(recipe)
        return result

    def is_recipe_unlocked(self, recipe):
        unlocked_by = recipe.get("unlocked_by", "default")
        if unlocked_by == "default":
            return True
        return self.game.player.flags.get(unlocked_by, False)

    def can_craft(self, recipe):
        for material in recipe.get("materials", []):
            item_id = material.get("item_id")
            quantity = material.get("quantity", 1)
            if not self.game.player.has_item(item_id, quantity):
                return False
        return True

    def craft(self, recipe):
        if not self.can_craft(recipe):
            self.game.set_message("Not enough materials.")
            return

        for material in recipe.get("materials", []):
            item_id = material.get("item_id")
            quantity = material.get("quantity", 1)
            self.game.player.remove_item(item_id, quantity)

        result = recipe.get("result", {})
        result_id = result.get("item_id")
        result_qty = result.get("quantity", 1)
        if result_id:
            self.game.player.add_item(result_id, result_qty)
            item_name = self.game.get_item_name(result_id)
            self.game.set_message(f"Crafted: {item_name} x{result_qty}.")

    def select_next(self):
        recipes = self.get_available_recipes()
        if not recipes:
            return
        self.selected_index = (self.selected_index + 1) % len(recipes)

    def select_prev(self):
        recipes = self.get_available_recipes()
        if not recipes:
            return
        self.selected_index = (self.selected_index - 1) % len(recipes)

    def craft_selected(self):
        recipes = self.get_available_recipes()
        if not recipes:
            return
        if 0 <= self.selected_index < len(recipes):
            self.craft(recipes[self.selected_index])

    def draw(self):
        self.game.screen.fill(BACKGROUND_COLOR)

        title = self.game.title_font.render("CRAFTING", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.game.screen.blit(title, title_rect)

        panel_rect = pygame.Rect(
            PADDING, 100,
            WINDOW_WIDTH - PADDING * 2,
            WINDOW_HEIGHT - 160,
        )
        self.game.draw_panel(panel_rect)

        self.draw_recipes(panel_rect)

        hint = self.game.small_font.render(
            "UP/DOWN - select   ENTER - craft   C or ESC - close",
            True, TEXT_COLOR,
        )
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.game.screen.blit(hint, hint_rect)

    def draw_recipes(self, rect):
        recipes = self.get_available_recipes()

        list_x = rect.x + 20
        list_y = rect.y + 20
        rect.width // 2 - 40

        list_title = self.game.header_font.render("Recipes:", True, ACCENT_COLOR)
        self.game.screen.blit(list_title, (list_x, list_y))
        list_y += 40

        if not recipes:
            empty = self.game.small_font.render(
                "No recipes available yet.", True, GRAY_DISABLED
            )
            self.game.screen.blit(empty, (list_x, list_y))
            return

        if self.selected_index >= len(recipes):
            self.selected_index = 0

        for index, recipe in enumerate(recipes):
            name = recipe.get("name", "Unknown")
            craftable = self.can_craft(recipe)
            is_selected = index == self.selected_index

            color = WHITE if craftable else GRAY_DISABLED
            if is_selected:
                color = YELLOW if craftable else RED

            prefix = "> " if is_selected else "  "
            line = f"{prefix}{name}"
            rendered = self.game.text_font.render(line, True, color)
            self.game.screen.blit(rendered, (list_x, list_y))
            list_y += 32

        detail_x = rect.x + rect.width // 2 + 20
        detail_y = rect.y + 20
        detail_width = rect.width // 2 - 40

        selected_recipe = recipes[self.selected_index]
        self.draw_recipe_details(detail_x, detail_y, detail_width, selected_recipe)

    def draw_recipe_details(self, x, y, width, recipe):
        title = recipe.get("name", "Unknown")
        result = recipe.get("result", {})
        result_id = result.get("item_id")
        result_qty = result.get("quantity", 1)

        title_surface = self.game.header_font.render(title, True, ACCENT_COLOR)
        self.game.screen.blit(title_surface, (x, y))
        y += 40

        description = recipe.get("description", "")
        wrapped = self.game.wrap_text(description, self.game.small_font, width)
        for line in wrapped:
            rendered = self.game.small_font.render(line, True, TEXT_COLOR)
            self.game.screen.blit(rendered, (x, y))
            y += 22

        y += 10
        produces = self.game.text_font.render(
            f"Produces: {self.game.get_item_name(result_id)} x{result_qty}",
            True, GREEN,
        )
        self.game.screen.blit(produces, (x, y))
        y += 34

        result_item = self.game.items_by_id.get(result_id, {})
        effects = result_item.get("effects", {})
        effect_parts = []
        if effects.get("heal_hp", 0) > 0:
            effect_parts.append(f"+{effects['heal_hp']} HP")
        if effects.get("reduce_infection", 0) > 0:
            effect_parts.append(f"-{effects['reduce_infection']} infection")
        if effects.get("apply_suppressant", 0) > 0:
            effect_parts.append(
                f"suppressant {effects['apply_suppressant']} battles"
            )
        if effect_parts:
            effect_line = "Effect: " + ", ".join(effect_parts)
            rendered = self.game.small_font.render(effect_line, True, TEXT_COLOR)
            self.game.screen.blit(rendered, (x, y))
            y += 28

        y += 10
        materials_title = self.game.text_font.render(
            "Required materials:", True, ACCENT_COLOR
        )
        self.game.screen.blit(materials_title, (x, y))
        y += 32

        for material in recipe.get("materials", []):
            item_id = material.get("item_id")
            needed = material.get("quantity", 1)
            have = self.game.player.inventory.get(item_id, 0)
            item_name = self.game.get_item_name(item_id)

            color = GREEN if have >= needed else RED
            line = f"- {item_name}: {have} / {needed}"
            rendered = self.game.small_font.render(line, True, color)
            self.game.screen.blit(rendered, (x, y))
            y += 24