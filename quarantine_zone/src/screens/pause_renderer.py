"""
pause_renderer.py
Renders pause menu overlay.
"""
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TEXT_COLOR, ACCENT_COLOR,
    WHITE, GREEN, YELLOW,
    PAUSE_OPTIONS,
    SAVE_FILE_1, SAVE_FILE_2,
)

GRAY_DISABLED = (110, 110, 120)


class PauseRenderer:
    def __init__(self, game):
        self.game = game

    def draw_pause(self):
        g = self.game
        s = g.screen

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        s.blit(overlay, (0, 0))

        title = g.title_font.render("PAUSE MENU", True, ACCENT_COLOR)
        s.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        start_y = 200
        line_h = 50
        cx = WINDOW_WIDTH // 2

        for i, (key, label) in enumerate(PAUSE_OPTIONS):
            selected = i == g.pause_selected_index
            color = YELLOW if selected else WHITE
            prefix = "> " if selected else "  "
            suffix = " <" if selected else "  "

            slot_exists = False
            if key in ("save1", "load1"):
                slot_exists = g.save_manager.save_exists(SAVE_FILE_1)
            elif key in ("save2", "load2"):
                slot_exists = g.save_manager.save_exists(SAVE_FILE_2)

            if key.startswith("load") and not slot_exists:
                color = GRAY_DISABLED

            rendered = g.text_font.render(f"{prefix}{label}{suffix}", True, color)
            rect = rendered.get_rect(center=(cx, start_y + i * line_h))
            s.blit(rendered, rect)

            if slot_exists and (key.startswith("save") or key.startswith("load")):
                s.blit(
                    g.small_font.render("[saved]", True, GREEN),
                    (rect.right + 20, rect.centery - 10)
                )

        hint = g.small_font.render(
            "UP/DOWN - select   ENTER - confirm   ESC - close", True, TEXT_COLOR
        )
        s.blit(hint, hint.get_rect(
            center=(cx, start_y + len(PAUSE_OPTIONS) * line_h + 30)
        ))