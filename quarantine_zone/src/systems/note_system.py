"""
note_system.py
Handles finding, showing and navigating story notes.
"""
import random

from settings import STATE_NOTE_VIEW, STATE_NOTES_LIST, STATE_EXPLORATION


class NoteSystem:
    def __init__(self, game):
        self.game = game

    # ── Public API ────────────────────────────────────────────

    def open_notes_list(self):
        g = self.game
        g.previous_state = g.state
        g._notes_origin = g.state
        g.notes_list_index = 0
        g.state = STATE_NOTES_LIST

    def show_note(self, note):
        g = self.game
        g.viewing_note = note
        if g.state != STATE_NOTES_LIST:
            g.previous_state = g.state
        g.state = STATE_NOTE_VIEW

    def try_find_note(self, location_id):
        """Try to find an undiscovered note in a location. 40% chance."""
        g = self.game
        available = [
            n for n in g.data.get("notes", [])
            if n.get("found_in") == location_id
            and n["id"] not in g.player.found_notes
        ]
        if not available:
            return None
        if random.randint(1, 100) > 40:
            return None
        note = random.choice(available)
        g.player.found_notes.append(note["id"])
        return note

    def show_notes_from_rewards(self, notes_ids):
        """Show notes granted by special actions."""
        g = self.game
        for note_id in notes_ids:
            if note_id not in g.player.found_notes:
                note = g.notes_by_id.get(note_id)
                if note:
                    g.player.found_notes.append(note_id)
                    self.show_note(note)
                    return  # show one at a time

    # ── Input handlers ────────────────────────────────────────

    def handle_note_view_input(self, key):
        import pygame # type: ignore
        g = self.game
        if key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
            g.viewing_note = None
            if g.previous_state == STATE_NOTES_LIST:
                g.state = STATE_NOTES_LIST
                g.previous_state = getattr(g, "_notes_origin", STATE_EXPLORATION)
            else:
                g.state = g.previous_state or STATE_EXPLORATION

    def handle_notes_list_input(self, key):
        import pygame # type: ignore
        g = self.game

        if key == pygame.K_ESCAPE:
            g.state = g.previous_state or STATE_EXPLORATION
            return

        found_notes = [
            g.notes_by_id[nid]
            for nid in g.player.found_notes
            if nid in g.notes_by_id
        ]
        if not found_notes:
            return

        if key == pygame.K_UP:
            g.notes_list_index = (g.notes_list_index - 1) % len(found_notes)
        elif key == pygame.K_DOWN:
            g.notes_list_index = (g.notes_list_index + 1) % len(found_notes)
        elif key == pygame.K_RETURN:
            prev = g.previous_state
            self.show_note(found_notes[g.notes_list_index])
            g.previous_state = STATE_NOTES_LIST
            g._notes_origin = prev