from dataclasses import dataclass, field

@dataclass
class ScrollingNote:
    """Data class representing a single scrolling note on the display."""

    note: int
    """The MIDI note value."""

    channel: int
    """The MIDI channel this note belongs to."""

    delta_time: float
    """The time in seconds between the start of the previous note and this one."""

    start_time: float
    """The time in seconds from the start of the song to when this note should be played."""

    note_time: float
    """The total time it should take for the note to travel through the scrolling area."""

    length: float = 0.0
    """The duration in seconds that this note is held down."""

    current_time: float = field(init=False, default=0.0)
    """The time elapsed in seconds since this note became active on screen."""

    end_time: float = field(init=False, default=0.0)
    """The time at which the note should disappear from the screen."""

    def activate(self, current_time: float = 0) -> None:
        """Activates the note by setting its current and end time."""
        self.current_time = current_time
        self.end_time = self.note_time + self.length

    def update(self, delta_time: float) -> None:
        """Updates the note's current time by the given delta from the last update."""
        self.current_time += delta_time

    @property
    def scroll_percentage(self) -> float:
        """How far the note has scrolled down the screen as a percentage."""
        return self.current_time / self.note_time
    
    @property
    def active(self) -> bool:
        """Whether the note is still active and in view."""
        return self.current_time <= self.end_time