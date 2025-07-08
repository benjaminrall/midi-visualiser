import os
import pygame
from .song import Song
from .piano_display_settings import PianoDisplaySettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PianoDisplay:
    """Class to manage rendering of the piano and scrolling notes using Pygame."""

    def __init__(self, settings: PianoDisplaySettings) -> None:
        """Initialises the display, calculates dimensions, and pre-renders static surfaces."""
        self.settings = settings
        
        self._calculate_dimensions()
        self.surface = pygame.Surface((self.width, self.height))

        self.key_rects: dict[int, pygame.Rect] = {}
        self.white_key_indices: set[int] = set()
        self.black_key_indices: set[int] = set()
        self.octave_positions: list[int] = []
        self._generate_key_layout()

        self._pre_render_surfaces()

    def _calculate_dimensions(self):
        """Calculates the dimensions of the piano and scrolling note area."""
        self.piano_width = self.settings.key_width * 52
        self.key_height = self.settings.key_width * 5
        self.scrolling_height = self.piano_width * self.settings.scroll_height_ratio
        
        self.width = self.piano_width
        self.height = self.scrolling_height + self.key_height
        self.piano_position = (0, self.scrolling_height)
        
        if self.settings.scrolling_notes:
            self.scrolling_unit = self.scrolling_height / self.settings.note_time

    def _generate_key_layout(self):
        """Calculates the positions and rectangles for all 88 piano keys."""
        left = 0
        for i in range(88):
            black = i % 12 in (1, 4, 6, 9, 11)
            (self.black_key_indices if black else self.white_key_indices).add(i)
            if i % 12 == 3:
                self.octave_positions.append(left)
            if black:
                self.key_rects[i] = pygame.Rect(
                    left - self.settings.key_width / 4, 0, 
                    self.settings.key_width / 2, self.key_height / 1.6
                )
            else:
                self.key_rects[i] = pygame.Rect(left, 0, self.settings.key_width, self.key_height)
                left += self.settings.key_width

    def _pre_render_surfaces(self):
        """Pre-renders all static surfaces that do not change frame-to-frame."""
        self.white_fill_surface, self.white_outline_surface = self._generate_key_surfaces(self.white_key_indices, (255, 255, 255), 5)
        self.black_fill_surface, self.black_outline_surface = self._generate_key_surfaces(self.black_key_indices, (0, 0, 0), 2)

        self.octave_divider_surface = self._generate_octave_dividers()
        self.piano_divider_surface = self._generate_piano_divider()
        
        if self.settings.show_play_icon:
            icon_size = (self.settings.key_width * 2, self.settings.key_width * 2)
            self.play_icon = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "imgs", "play.png")), icon_size)
            self.pause_icon = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "imgs", "pause.png")), icon_size)

    def _generate_key_surfaces(self, key_indices: set[int], color: tuple[int, int, int], border: int) -> tuple[pygame.Surface, pygame.Surface]:
        """Generates the fill and outline surfaces for the given set of keys."""
        fill_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        outline_surface = pygame.Surface((self.piano_width, self.key_height), pygame.SRCALPHA)
        
        for key_index in key_indices:
            rect = self.key_rects[key_index]
            pygame.draw.rect(
                fill_surface, color, rect, 
                border_bottom_left_radius=border, 
                border_bottom_right_radius=border
            )
            pygame.draw.rect(
                outline_surface, (0, 0, 0), rect, 
                border_bottom_left_radius=border, 
                border_bottom_right_radius=border, 
                width=1
            )
            
        return fill_surface, outline_surface

    def _generate_octave_dividers(self) -> pygame.Surface:
        """Generates a surface containing vertical lines for each octave."""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for x_pos in self.octave_positions:
            pygame.draw.line(surface, self.settings.octave_divider_colour, (x_pos, 0), (x_pos, self.height))
        return surface

    def _generate_piano_divider(self) -> pygame.Surface:
        """Generates the surface for the horizontal divider above the piano."""
        surface = pygame.Surface((self.piano_width, 5), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.settings.piano_divider_colour, surface.get_rect())
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), width=1)
        return surface
    
    def _draw_background(self):
        """Draws the static background and dividers."""
        self.surface.fill(self.settings.background_colour)
        if self.settings.show_octave_divider:
            self.surface.blit(self.octave_divider_surface, (0, 0))

    def _draw_scrolling_notes(self, song: Song):
        """Draws all active scrolling notes."""
        # Iterate backwards to safely remove items while looping
        for note in song.active_scrolling_notes:
            if note.note not in self.key_rects:
                continue

            base_rect = self.key_rects[note.note]
            height = note.length * self.scrolling_unit
            y_pos = note.scroll_percentage * self.scrolling_height - height
            
            note_rect = pygame.Rect(base_rect.x, y_pos, base_rect.w, height)
            
            colour = self.settings.channel_colours[note.channel].scrolling_note_colour
            pygame.draw.rect(self.surface, colour, note_rect, border_radius=5)
            pygame.draw.rect(self.surface, (0, 0, 0), note_rect, border_radius=5, width=1)

    def _draw_piano(self, song: Song | None):
        """Draws the piano itself, including all actively coloured keys."""
        # Draws white key backgrounds
        self.surface.blit(self.white_fill_surface, self.piano_position)

        # Draws active white keys
        if song:
            for key in self.white_key_indices:
                note = key + 21
                channel, pressed = song.notes_pressed[note]
                if not pressed:
                    continue
                rect = self.key_rects[key]
                colour = self.settings.channel_colours[channel].white_key_pressed_colour
                pygame.draw.rect(
                    self.surface, colour, rect.move(self.piano_position), 
                    border_bottom_left_radius=5, border_bottom_right_radius=5
                )

        # Draws white key outlines
        self.surface.blit(self.white_outline_surface, self.piano_position)

        # Draws black key background
        self.surface.blit(self.black_fill_surface, self.piano_position)

        # Draws active black keys
        if song:
            for key in self.black_key_indices:
                note = key + 21
                channel, pressed = song.notes_pressed[note]
                if not pressed:
                    continue
                rect = self.key_rects[key]
                colour = self.settings.channel_colours[channel].black_key_pressed_colour
                pygame.draw.rect(
                    self.surface, colour, rect.move(self.piano_position), 
                    border_bottom_left_radius=2, border_bottom_right_radius=2
                )
                
        # Draws black key outlines
        self.surface.blit(self.black_outline_surface, self.piano_position)

        # Draws piano divider
        if self.settings.show_piano_divider:
            self.surface.blit(self.piano_divider_surface, self.piano_position)

    def _draw_ui(self, song: Song):
        """Draws UI elements like the play/pause icon."""
        icon = self.play_icon if song.playing else self.pause_icon
        pos = (self.settings.key_width // 8, self.settings.key_width // 8)
        self.surface.blit(icon, pos)

    def draw(self, target: pygame.Surface, song: Song | None, pos: tuple[int, int] = (0, 0)):
        """
        Draws the entire piano display for a given song to a target surface.
        This is the main rendering method called every frame.
        """
        self._draw_background()
        
        if song:
            if self.settings.scrolling_notes:
                self._draw_scrolling_notes(song)
            self._draw_piano(song)
            if self.settings.show_play_icon:
                self._draw_ui(song)
        else:
            # If no song, draws a static, empty piano
            self._draw_piano(None)

        target.blit(self.surface, pos)
