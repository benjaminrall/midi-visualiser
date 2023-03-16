class ScrollingNote:
    """A class to represent a scrolling note on the display."""

    def __init__(self, note: int, channel: int, time: float, note_time: float, start_time: float, length = 0) -> None:
        self.note = note                # The piano note value
        self.channel = channel          # The note's channel value
        self.length = length            # The length of the note in seconds
        self.time = time                # The time difference between this note and the previous note
        self.start_time = start_time    # The time that the note starts playing
        self.note_time = note_time      # The time taken for a note to scroll through the scroll display
        self.activate()

    def activate(self) -> None:
        """Activates a scrolling note by setting its current and end time."""
        self.current_time = 0
        self.end_time = self.note_time + self.length

    def get_percentage(self) -> float:
        """Calculates how far the note is through its scroll."""
        return self.current_time / self.note_time
    
    def update_time(self, delta_time: float) -> None:
        """Updates the note's current time."""
        self.current_time += delta_time
    
    def check_active(self) -> bool:
        """Returns if the note is still active and in view."""
        return self.current_time <= self.end_time
