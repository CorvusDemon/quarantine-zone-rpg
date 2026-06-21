"""
menu_renderer.py
Renders main menu, game over and victory screens.
"""
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PANEL_BORDER_COLOR,
    TEXT_COLOR, ACCENT_COLOR,
    WHITE, RED, GREEN,
    SAVE_FILE_1, SAVE_FILE_2,
)

GRAY_DISABLED = (110, 110, 120)


class MenuRenderer:
    def __init__(self, game):
        self.game = game

    def draw_menu(self):
        g = self.game
        s = g.screen

        title = g.title_font.render("QUARANTINE ZONE", True, ACCENT_COLOR)
        s.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 110)))

        subtitle = g.text_font.render(
            "Survive the outbreak. Reach the rooftop.", True, TEXT_COLOR
        )
        s.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 165)))

        pygame.draw.line(
            s, PANEL_BORDER_COLOR,
            (WINDOW_WIDTH // 2 - 200, 195),
            (WINDOW_WIDTH // 2 + 200, 195), 1
        )

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 240, 210, 480, 280)
        g.ui_renderer.draw_panel(panel)

        y = panel.y + 25
        s.blit(g.text_font.render("1.  New Game", True, WHITE), (panel.x + 30, y))

        y += 60
        slot1 = g.save_manager.save_exists(SAVE_FILE_1)
        s.blit(
            g.text_font.render("2.  Load Slot 1", True, WHITE if slot1 else GRAY_DISABLED),
            (panel.x + 30, y)
        )
        if slot1:
            s.blit(g.small_font.render("(save exists)", True, GREEN), (panel.x + 30, y + 28))

        y += 70
        slot2 = g.save_manager.save_exists(SAVE_FILE_2)
        s.blit(
            g.text_font.render("3.  Load Slot 2", True, WHITE if slot2 else GRAY_DISABLED),
            (panel.x + 30, y)
        )
        if slot2:
            s.blit(g.small_font.render("(save exists)", True, GREEN), (panel.x + 30, y + 28))

        y += 70
        s.blit(g.text_font.render("ESC  Quit", True, GRAY_DISABLED), (panel.x + 30, y))

        hint = g.small_font.render(
            "In-game: F5 Quick Save   F9 Quick Load   ESC Pause", True, TEXT_COLOR
        )
        s.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel.bottom + 30)))

        g.ui_renderer.draw_message_bar()

    def draw_game_over(self):
        g = self.game
        t = g.title_font.render("GAME OVER", True, RED)
        g.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)))
        t = g.text_font.render("Press ENTER.", True, TEXT_COLOR)
        g.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)))

    def draw_victory(self):
        g = self.game
        t = g.title_font.render("YOU ESCAPED!", True, GREEN)
        g.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)))
        t = g.text_font.render("You reached the rooftop and survived.", True, TEXT_COLOR)
        g.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)))
        t = g.text_font.render("Press ENTER.", True, TEXT_COLOR)
        g.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)))