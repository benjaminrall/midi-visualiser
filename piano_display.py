import pygame
import os
from collections import defaultdict
from scrolling_note import ScrollingNote

class PianoDisplay:
    def __init__(self, key_width = 20, key_ratio = 5, note_time = 2) -> None:
        # Calculates initial piano information
        self.key_width = key_width
        self.key_ratio = key_ratio
        self.note_time = note_time
        self.piano_width = key_width * 52
        self.key_height = key_width * self.key_ratio

        # Creates display window
        self.win_width = key_width * 52
        self.win_height = self.win_width // 2
        self.scrolling_height = self.win_height - self.key_height
        self.scrolling_unit = self.scrolling_height / self.note_time
        self.window = pygame.display.set_mode((self.win_width, self.win_height)) 
        self.piano_position = (0, self.scrolling_height)

        # Calculates white and black key sets and all key rects
        self.white_set = set()
        self.black_set = set()
        self.key_rects = {}
        left = 0
        self.octave_positions = []
        for i in range(88):
            black = i % 12 in (1, 4, 6, 9, 11)
            (self.black_set if black else self.white_set).add(i)
            if i % 12 == 3:
                self.octave_positions.append(left)
            if black:
                self.key_rects[i] = pygame.Rect(left - self.key_width / 4, 0, self.key_width / 2, self.key_height / 1.6)
            else:
                self.key_rects[i] = pygame.Rect(left, 0, self.key_width, self.key_height)
                left += self.key_width
        
        # Generates permanent surfaces
        self.white_fill_surface, self.white_outline_surface = self.generate_white_keys()
        self.black_fill_surface, self.black_outline_surface = self.generate_black_keys()
        self.octave_divider_surface, self.piano_divider_surface = self.generate_dividers()
        self.play_image = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "play.png")), (2 * self.key_width, 2 * self.key_width))
        self.pause_image = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "pause.png")), (2 * self.key_width, 2 * self.key_width))

    def draw(self, notes: defaultdict, scrolling_notes: list[ScrollingNote], playing: bool) -> None:
        """Draws the entire piano to a given surface."""
        self.window.blit(self.octave_divider_surface, (0, 0))

        for scrolling_note in scrolling_notes.copy():
            if not scrolling_note.check_active():
                scrolling_notes.remove(scrolling_note)
            if not scrolling_note.note in self.key_rects:
                continue
            rect = self.key_rects[scrolling_note.note]
            height = scrolling_note.length * self.scrolling_unit
            new_rect = pygame.Rect(rect.x, scrolling_note.get_percentage() * self.scrolling_height - height, rect.w, height)
            pygame.draw.rect(self.window, (255, 0, 0), new_rect, border_radius=self.key_ratio)
            pygame.draw.rect(self.window, (0, 0, 0), new_rect, border_radius=self.key_ratio, width=self.key_ratio // 5)

        # Draws piano surface
        for piano_surface in [
                self.white_fill_surface, self.generate_active_white_keys(notes), self.white_outline_surface, 
                self.black_fill_surface, self.generate_active_black_keys(notes), self.black_outline_surface, 
                self.piano_divider_surface
            ]:
            self.window.blit(piano_surface, self.piano_position)

        self.window.blit(self.play_image if playing else self.pause_image, (0, 0))
        pygame.display.update()

    def generate_dividers(self):
        """Generates surfaces for the piano's dividers."""
        # Creates piano divider surface
        piano_surface = pygame.Surface((self.piano_width, self.key_ratio))
        piano_surface.fill((255, 0, 0))
        pygame.draw.rect(piano_surface, (0, 0, 0), pygame.Rect(0, 0, self.piano_width, self.key_ratio), width=self.key_ratio // 5)

        # Creates octave dividers surface
        octave_surface = pygame.Surface((self.win_width, self.win_height))
        octave_surface.fill((60, 60, 60))
        for i in self.octave_positions:
            pygame.draw.line(octave_surface, (80, 80, 80), (i, 0), (i, self.win_height))
        return octave_surface, piano_surface

    def generate_white_keys(self):
        """Generates surfaces for the piano's white keys and their outlines."""
        # Creates the surfaces
        key_surface = pygame.Surface((self.piano_width, self.key_height))
        key_surface.fill((0, 0, 0))
        outline_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)

        for key in self.white_set:
            # Draws key body
            pygame.draw.rect(
                key_surface, (255, 255, 255), self.key_rects[key], 
                border_bottom_left_radius=self.key_ratio, border_bottom_right_radius=self.key_ratio
            )
            # Draws key outline
            pygame.draw.rect(
                outline_surface, (0, 0, 0), self.key_rects[key], 
                width=self.key_ratio // 5, border_bottom_left_radius=self.key_ratio, border_bottom_right_radius=self.key_ratio
            )

        return key_surface, outline_surface
    
    def generate_active_white_keys(self, active_notes):
        surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.white_set:
            if active_notes[key + 21]:
                pygame.draw.rect(
                    surface, (255, 0, 0), self.key_rects[key], 
                    border_bottom_left_radius=self.key_ratio, border_bottom_right_radius=self.key_ratio
                )
        return surface

    def generate_black_keys(self):
        """Generates the surface for the piano's black keys."""
        key_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        outline_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.black_set:
            pygame.draw.rect(
                key_surface, (0, 0, 0), self.key_rects[key], 
                border_bottom_left_radius=self.key_ratio // 2, border_bottom_right_radius=self.key_ratio // 2
            )
            pygame.draw.rect(
                outline_surface, (0, 0, 0), self.key_rects[key], 
                border_bottom_left_radius=self.key_ratio // 2, border_bottom_right_radius=self.key_ratio // 2, width=self.key_ratio//5
            )
        return key_surface, outline_surface
    
        
    def generate_active_black_keys(self, active_notes):
        """Generates the surface for the piano's active black keys."""
        surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.black_set:
            if active_notes[key + 21]:
                pygame.draw.rect(surface, (255, 0, 0), self.key_rects[key], border_bottom_left_radius=self.key_ratio // 2, border_bottom_right_radius=self.key_ratio // 2)
        return surface

