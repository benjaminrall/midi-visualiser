from collections import defaultdict
import random
import colorsys

# Default Display Settings
KEY_WIDTH = 25
NOTE_TIME = 2
SCROLL_HEIGHT_RATIO = 0.4
SCROLLING_NOTES = True
SHOW_PIANO_DIVIDER = True
SHOW_OCTAVE_DIVIDER = True
SHOW_PLAY_ICON = True
BACKGROUND_COLOUR = (60, 60, 60)
OCTAVE_DIVIDER_COLOUR = (80, 80, 80)
PIANO_DIVIDER_COLOUR = (200, 0, 0)
WHITE_KEY_PRESSED_COLOUR = (255, 0, 0)
BLACK_KEY_PRESSED_COLOUR= (127, 0, 0)
SCROLLING_NOTE_COLOUR = (200, 0, 0)

def generate_random_colour() -> tuple[int, int, int]:
    """Generates random colour using HLS and converts to RGB."""
    h,l,s = random.random(), .4 + random.random() / 5, .8 + random.random() / 5
    return tuple([int(256*i) for i in colorsys.hls_to_rgb(h,l,s)])

class ChannelColour:

    colour_parameters = 3

    """A class to represent key colours for a specific channel."""
    def __init__(self, 
        white_key_pressed_colour=WHITE_KEY_PRESSED_COLOUR,
        black_key_pressed_colour=BLACK_KEY_PRESSED_COLOUR,
        scrolling_note_colour=SCROLLING_NOTE_COLOUR
    ) -> None:
        self.white_key_pressed_colour = white_key_pressed_colour
        self.black_key_pressed_colour = black_key_pressed_colour
        self.scrolling_note_colour = scrolling_note_colour

    @staticmethod
    def random():
        """Returns a random single colour channel colour object."""
        return ChannelColour.single_colour(generate_random_colour())
    
    @staticmethod
    def single_colour(colour):
        """Returns a channel colour object with all options being one colour."""
        return ChannelColour(*[colour for _ in range(ChannelColour.colour_parameters)])

# Default channel colours
CHANNEL_COLOURS = [
    ChannelColour.single_colour((255, 128, 20)),
    ChannelColour.single_colour((0, 128, 255)),
    ChannelColour.single_colour((150, 50, 255)),
    ChannelColour.single_colour((0, 255, 0)),
    ChannelColour.single_colour((255, 0, 0)),
    ChannelColour.single_colour((150, 255, 255)),
    ChannelColour.single_colour((255, 100, 255)),
    ChannelColour.single_colour((0, 0, 255)),
]

class PianoDisplaySettings:
    """A class to store settings for a PianoDisplay object."""

    def __init__(self, 
        key_width=KEY_WIDTH, note_time=NOTE_TIME, scroll_height_ratio=SCROLL_HEIGHT_RATIO, scrolling_notes=SCROLLING_NOTES, 
        show_piano_divider=SHOW_PIANO_DIVIDER, show_octave_divider=SHOW_OCTAVE_DIVIDER, show_play_icon=SHOW_PLAY_ICON,
        background_colour=BACKGROUND_COLOUR, octave_divider_colour=OCTAVE_DIVIDER_COLOUR, piano_divider_colour=PIANO_DIVIDER_COLOUR,
        channel_colours=CHANNEL_COLOURS
    ) -> None:
        # General piano settings
        self.key_width = key_width
        self.note_time = note_time
        self.scroll_height_ratio = scroll_height_ratio
        self.scrolling_notes = scrolling_notes
        
        # Boolean display settings
        self.show_piano_divider = show_piano_divider
        self.show_octave_divider = show_octave_divider
        self.show_play_icon = show_play_icon

        # Colour settings
        self.background_colour = background_colour
        self.octave_divider_colour = octave_divider_colour
        self.piano_divider_colour = piano_divider_colour
        self.channel_colours = defaultdict(lambda : ChannelColour.random())
        for i in range(len(channel_colours)):
            self.channel_colours[i] = channel_colours[i]