"""
ui_renderer.py
Shared drawing utilities used across all screens.
"""
import pygame # type: ignore

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PANEL_COLOR, PANEL_BORDER_COLOR,
    WHITE, PADDING,
)

GRAY_DISABLED = (110, 110, 120)
MESSAGE_LIFETIME_MS = 9000


class UIRenderer:
    def __init__(self, game):
        self.game = game

    def draw_panel(self, rect):
        pygame.draw.rect(
            self.game.screen, PANEL_COLOR, rect, border_radius=10
        )
        pygame.draw.rect(
            self.game.screen, PANEL_BORDER_COLOR, rect,
            width=2, border_radius=10
        )

    def draw_message_bar(self):
        g = self.game
        if not g.message_text:
            return
        elapsed = pygame.time.get_ticks() - g.message_time
        if elapsed > MESSAGE_LIFETIME_MS:
            return

        bar_h = 40
        bar = pygame.Rect(
            PADDING,
            WINDOW_HEIGHT - bar_h - 5,
            WINDOW_WIDTH - PADDING * 2,
            bar_h
        )
        pygame.draw.rect(g.screen, PANEL_COLOR, bar, border_radius=8)
        pygame.draw.rect(g.screen, PANEL_BORDER_COLOR, bar, width=2, border_radius=8)

        rendered = g.small_font.render(g.message_text, True, WHITE)
        g.screen.blit(rendered, rendered.get_rect(
            midleft=(bar.x + 12, bar.centery)
        ))

    def wrap_text(self, text, font, max_w):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = w if not cur else f"{cur} {w}"
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def get_infection_color(self, infection):
        from settings import RED, YELLOW, GREEN
        if infection >= 75:
            return RED
        if infection >= 25:
            return YELLOW
        return GREEN

    def draw_mini_bar(self, x, y, width, height, value, max_value, color, bg):
        ratio = max(0.0, min(1.0, value / max_value)) if max_value > 0 else 0
        pygame.draw.rect(
            self.game.screen, bg,
            pygame.Rect(x, y, width, height), border_radius=4
        )
        fw = int(width * ratio)
        if fw > 0:
            pygame.draw.rect(
                self.game.screen, color,
                pygame.Rect(x, y, fw, height), border_radius=4
            )