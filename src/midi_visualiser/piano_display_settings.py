from dataclasses import dataclass, field
from collections import defaultdict
import random
import colorsys

def generate_random_colour() -> tuple[int, int, int]:
    """Generates a random colour by using HLS and then converting to RGB."""
    H, L, S = random.random(), .4 + random.random() / 5, .8 + random.random() / 5
    return tuple([int(256 * i) for i in colorsys.hls_to_rgb(H, L, S)])

@dataclass
class ChannelColour:
    """
    Data class representing the colour scheme for a single MIDI channel.
    Allows different colours to be specified for white/black keys and scrolling notes.
    """
    white_key_pressed_colour: tuple[int, int, int]
    black_key_pressed_colour: tuple[int, int, int]
    scrolling_note_colour: tuple[int, int, int]

    @staticmethod
    def random() -> 'ChannelColour':
        """Constructs a ChannelColour instance with a random monochromatic scheme.

        Returns
        -------
        ChannelColour
            An instance of ChannelColour where all colours are the same, random colour.
        """
        return ChannelColour.monochromatic(generate_random_colour())
    
    @staticmethod
    def monochromatic(colour: tuple[int, int, int]) -> 'ChannelColour':
        """Creates a ChannelColour instance with all colours set to the provided colour.

        Parameters
        ----------
        colour : tuple[int, int, int]
            The RGB tuple to use for all colour properties.

        Returns
        -------
        ChannelColour
            An instance of ChannelColour where all colours are the same.
        """
        return ChannelColour(
            white_key_pressed_colour=colour,
            black_key_pressed_colour=colour,
            scrolling_note_colour=colour,
        )

@dataclass
class PianoDisplaySettings:
    """Data class storing all configurable settings for a PianoDisplay object."""
    
    key_width: int = 25
    """Width in pixels of a single white key on the virtual piano."""
    
    note_time: float = 2.0
    """The duration in seconds for a scrolling note to travel from the top of 
    the screen to the piano."""

    scroll_height_ratio: float = 0.4
    """The ratio between the piano's width and the height of the scrolling 
    note area. A larger value makes the scrolling area taller."""

    scrolling_notes: bool = True
    """If True, scrolling notes will be displayed."""

    show_piano_divider: bool = True
    """If True, a horizontal line is drawn separating the piano from the 
    scrolling note area."""

    show_octave_divider: bool = True
    """If True, vertical lines are drawn to separate octaves in the scrolling 
    note area."""

    show_play_icon: bool = True
    """If True, a play/pause icon is shown in the top-left corner of the 
    window to indicate the current playback state."""

    background_colour: tuple[int, int, int] = (60, 60, 60)
    """The background colour of the scrolling note area."""

    piano_divider_colour: tuple[int, int, int] = (200, 0, 0)
    """The colour of the horizontal line separating the piano and note area."""

    octave_divider_colour: tuple[int, int, int] = (80, 80, 80)
    """The colour of the vertical octave divider lines."""

    channel_colours: defaultdict[int, ChannelColour] = field(
        default_factory=lambda: defaultdict(ChannelColour.random)
    )
    """A dictionary mapping a MIDI channel number to a ChannelColour object.
    Each time a new channel is encountered, a random colour is generated."""

    def __post_init__(self):
        """Populates the default channel colours after initialisation."""
        default_colours = [
            ChannelColour.monochromatic((255, 128, 20)),
            ChannelColour.monochromatic((0, 128, 255)),
            ChannelColour.monochromatic((150, 50, 255)),
            ChannelColour.monochromatic((0, 255, 0)),
            ChannelColour.monochromatic((255, 0, 0)),
            ChannelColour.monochromatic((150, 255, 255)),
            ChannelColour.monochromatic((255, 100, 255)),
            ChannelColour.monochromatic((0, 0, 255)),
        ]

        for i, colour in enumerate(default_colours):
            self.channel_colours[i] = colour