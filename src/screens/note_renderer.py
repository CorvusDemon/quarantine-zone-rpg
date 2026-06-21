"""
note_renderer.py
Renders note view and notes list screens.
"""
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR,
    WHITE, YELLOW, PADDING,
)

GRAY_DISABLED = (110, 110, 120)


class NoteRenderer:
    def __init__(self, game):
        self.game = game

    def draw_note_view(self):
        g = self.game
        s = g.screen
        s.fill(BACKGROUND_COLOR)

        if g.viewing_note is None:
            return

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 400, 80, 800, WINDOW_HEIGHT - 160)
        pygame.draw.rect(s, (45, 40, 30), panel, border_radius=12)
        pygame.draw.rect(s, (90, 80, 60), panel, width=3, border_radius=12)

        s.blit(
            g.header_font.render(
                g.viewing_note.get("title", "Unknown"), True, (220, 200, 140)
            ),
            (panel.x + 30, panel.y + 25)
        )

        pygame.draw.line(
            s, (120, 100, 70),
            (panel.x + 30, panel.y + 70),
            (panel.right - 30, panel.y + 70), 1
        )

        text = g.viewing_note.get("text", "")
        lines = g.ui_renderer.wrap_text(text, g.text_font, panel.width - 60)
        y = panel.y + 90
        for line in lines:
            s.blit(
                g.text_font.render(line, True, (230, 220, 190)),
                (panel.x + 30, y)
            )
            y += 34

        hint = g.small_font.render(
            "Press ENTER, SPACE or ESC to continue", True, (180, 160, 120)
        )
        s.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel.bottom - 25)))

    def draw_notes_list(self):
        g = self.game
        s = g.screen
        s.fill(BACKGROUND_COLOR)

        title = g.title_font.render("FOUND NOTES", True, ACCENT_COLOR)
        s.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 60)))

        panel = pygame.Rect(PADDING, 110, WINDOW_WIDTH - PADDING * 2, WINDOW_HEIGHT - 170)
        g.ui_renderer.draw_panel(panel)

        found = [
            g.notes_by_id[nid]
            for nid in g.player.found_notes
            if nid in g.notes_by_id
        ]

        if not found:
            empty = g.text_font.render("You haven't found any notes yet.", True, GRAY_DISABLED)
            s.blit(empty, empty.get_rect(center=(panel.centerx, panel.centery)))
        else:
            y = panel.y + 30
            for i, note in enumerate(found):
                selected = i == g.notes_list_index
                color = YELLOW if selected else WHITE
                prefix = "> " if selected else "  "
                s.blit(
                    g.text_font.render(
                        f"{prefix}{note.get('title', 'Unknown')}", True, color
                    ),
                    (panel.x + 30, y)
                )
                y += 36

        hint = g.small_font.render(
            "UP/DOWN - select   ENTER - read   ESC - close", True, TEXT_COLOR
        )
        s.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))