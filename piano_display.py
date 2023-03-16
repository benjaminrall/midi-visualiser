import os
import pygame
from song import Song
from piano_display_settings import PianoDisplaySettings

class PianoDisplay:
    def __init__(self, settings: PianoDisplaySettings) -> None:
        self.settings = settings
        
        # Calculates initial piano information
        self.key_height = settings.key_width * 5
        self.piano_width = settings.key_width * 52
        self.scrolling_height = self.piano_width * settings.scroll_height_ratio        

        # Creates display surface
        self.width = self.piano_width
        self.height = self.scrolling_height + self.key_height
        self.surface = pygame.Surface((self.width, self.height))
        if settings.scrolling_notes:
            self.scrolling_unit = self.scrolling_height / settings.note_time
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
                self.key_rects[i] = pygame.Rect(left - settings.key_width / 4, 0, settings.key_width / 2, self.key_height / 1.6)
            else:
                self.key_rects[i] = pygame.Rect(left, 0, settings.key_width, self.key_height)
                left += settings.key_width
        
        # Generates permanent surfaces
        self.white_fill_surface, self.white_outline_surface = self.generate_white_keys()
        self.black_fill_surface, self.black_outline_surface = self.generate_black_keys()
        self.octave_divider_surface, self.piano_divider_surface = self.generate_dividers()
        self.play_image = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "play.png")), (2 * settings.key_width, 2 * settings.key_width))
        self.pause_image = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "pause.png")), (2 * settings.key_width, 2 * settings.key_width))

    def draw(self, target: pygame.Surface, song: Song = None, pos: tuple[int, int] = (0, 0)) -> None:
        """Draws the piano display for a given song to a given surface."""
        # Resets current surface
        self.surface.fill(self.settings.background_colour)
        
        # Draws octave dividers
        if self.settings.show_octave_divider:
            self.surface.blit(self.octave_divider_surface, (0, 0))

        # Draw blank piano with no song information if there is no song
        if song is None:
            for piano_surface in [
                    self.white_fill_surface, self.white_outline_surface, 
                    self.black_fill_surface, self.black_outline_surface, 
                ]:
                self.surface.blit(piano_surface, self.piano_position)
            if self.settings.show_piano_divider:
                self.surface.blit(self.piano_divider_surface, self.piano_position)
            target.blit(self.surface, pos)
            return

        # Draws scrolling notes
        if self.settings.scrolling_notes:
            for scrolling_note in song.active_scrolling_notes.copy():
                if not scrolling_note.check_active():
                    song.active_scrolling_notes.remove(scrolling_note)
                if not scrolling_note.note in self.key_rects:
                    continue
                rect = self.key_rects[scrolling_note.note]
                height = scrolling_note.length * self.scrolling_unit
                new_rect = pygame.Rect(rect.x, scrolling_note.get_percentage() * self.scrolling_height - height, rect.w, height)
                pygame.draw.rect(self.surface, 
                    self.settings.channel_colours[scrolling_note.channel].white_key_pressed_colour, new_rect, border_radius=5
                )
                pygame.draw.rect(self.surface, (0, 0, 0), new_rect, border_radius=5, width=1)

        # Draws piano surface
        for piano_surface in [
                self.white_fill_surface, self.generate_active_white_keys(song.notes_pressed), self.white_outline_surface, 
                self.black_fill_surface, self.generate_active_black_keys(song.notes_pressed), self.black_outline_surface, 
            ]:
            self.surface.blit(piano_surface, self.piano_position)
        if self.settings.show_piano_divider:
            self.surface.blit(self.piano_divider_surface, self.piano_position)

        # Draws play/pause icon
        if self.settings.show_play_icon:
            self.surface.blit(self.play_image if song.playing else self.pause_image, (0, 0))
        
        # Draws surface to
        target.blit(self.surface, pos)

    def generate_dividers(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Generates surfaces for the piano's dividers."""
        # Creates piano divider surface
        piano_surface = pygame.Surface((self.piano_width, 5))
        piano_surface.fill(self.settings.piano_divider_colour)
        pygame.draw.rect(piano_surface, (0, 0, 0), pygame.Rect(0, 0, self.piano_width, 5), width=1)

        # Creates octave dividers surface
        octave_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in self.octave_positions:
            pygame.draw.line(octave_surface, self.settings.octave_divider_colour, (i, 0), (i, self.height))
        return octave_surface, piano_surface

    def generate_white_keys(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Generates surfaces for the piano's white keys and their outlines."""
        # Creates the surfaces
        key_surface = pygame.Surface((self.piano_width, self.key_height))
        key_surface.fill((0, 0, 0))
        outline_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)

        for key in self.white_set:
            # Draws key body
            pygame.draw.rect(
                key_surface, (255, 255, 255), self.key_rects[key], 
                border_bottom_left_radius=5, border_bottom_right_radius=5
            )
            # Draws key outline
            pygame.draw.rect(
                outline_surface, (0, 0, 0), self.key_rects[key], 
                border_bottom_left_radius=5, border_bottom_right_radius=5, width=1
            )

        return key_surface, outline_surface
    
    def generate_active_white_keys(self, active_notes) -> pygame.Surface:
        """Generates the surface for the piano's active white keys."""
        surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.white_set:
            if active_notes[key + 21][1]:
                pygame.draw.rect(
                    surface, self.settings.channel_colours[active_notes[key + 21][0]].white_key_pressed_colour, 
                    self.key_rects[key], border_bottom_left_radius=5, border_bottom_right_radius=5
                )
        return surface

    def generate_black_keys(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Generates the surface for the piano's black keys."""
        key_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        outline_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.black_set:
            pygame.draw.rect(
                key_surface, (0, 0, 0), self.key_rects[key], 
                border_bottom_left_radius=2, border_bottom_right_radius=2
            )
            pygame.draw.rect(
                outline_surface, (0, 0, 0), self.key_rects[key], 
                border_bottom_left_radius=2, border_bottom_right_radius=2, width=1
            )
        return key_surface, outline_surface
    
        
    def generate_active_black_keys(self, active_notes) -> pygame.Surface:
        """Generates the surface for the piano's active black keys."""
        surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        for key in self.black_set:
            if active_notes[key + 21][1]:
                pygame.draw.rect(
                    surface, self.settings.channel_colours[active_notes[key + 21][0]].black_key_pressed_colour, 
                    self.key_rects[key], border_bottom_left_radius=2, border_bottom_right_radius=2
                )
        return surface
