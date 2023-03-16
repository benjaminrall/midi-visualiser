import mido
import time
from collections import defaultdict
from scrolling_note import ScrollingNote
from piano_display_settings import PianoDisplaySettings

class Song:
    """A class to represent a song loaded from a MIDI file."""

    def __init__(self, file_name: str, audio_output: mido.ports.IOPort, display_settings: PianoDisplaySettings) -> None:
        self.display_settings = display_settings

        # Trackers for song time and progress
        self._message_index = 0
        self._scrolling_note_index = 0
        self._message_delta_time = 0
        self._scrolling_note_delta_time = 0
        self._last_frame = None

        # Loads midi file and stores parameters
        self.midi_file = mido.MidiFile(file_name, clip=True)
        self.audio_output = audio_output
        self.audio_output.reset()

        # Adds delay message to song and generates scrolling notes
        self.messages = [mido.Message('note_off', time=display_settings.note_time)] + list(self.midi_file)
        self.length = len(self.messages)
        if display_settings.scrolling_notes:
            self.scrolling_notes = self.generate_scrolling_notes()
            self.scrolling_notes_length = len(self.scrolling_notes)
        
        # Sets initial song display information
        self.notes_pressed = defaultdict(lambda : (0, False))
        self.active_scrolling_notes = []
        self.playing = False

    def __len__(self) -> int:
        """Returns the amount of messages that the song has."""
        return self.length
        
    def __getitem__(self, index: int) -> mido.Message:
        """Returns the message at a given index."""
        return self.messages[index]
    
    def __next__(self) -> mido.Message:
        """Returns the next message to execute based on the current message index."""
        return self[self._message_index]
    
    def generate_scrolling_notes(self) -> list[ScrollingNote]:
        """Generates a list of the song's scrolling notes."""
        last_note = defaultdict(lambda : None)
        scrolling_notes = []
        current_time = 0
        delta_time = 0

        # Loops through all messages (ignoring the buffer message) and creates scrolling notes
        for msg in self.messages[1:]:
            # Add to current and delta time
            current_time += msg.time
            delta_time += msg.time

            # Check for notes being played/released
            if msg.type.startswith("note"):
                if msg.type == "note_on" and msg.velocity > 0:
                    # Create a new note if a note is being played
                    new_note = ScrollingNote(msg.note - 21, msg.channel, delta_time, self.display_settings.note_time, current_time)

                    # If the previous press of the same note never ended, calculate its length here
                    if last_note[msg.note] is not None:
                        last_note[msg.note].length = current_time - last_note[msg.note].start_time

                    # Store reference to the new note so its length can be calculated later 
                    last_note[msg.note] = new_note

                    # Add new note to list and reset delta time
                    scrolling_notes.append(new_note)
                    delta_time = 0
                elif last_note[msg.note] is not None:
                    # If a note ended, calculate its length and reset the last note
                    last_note[msg.note].length = current_time - last_note[msg.note].start_time
                    last_note[msg.note] = None

        # Calculate lengths for all remaining unended notes
        for note in last_note:
            if last_note[note] is not None:
                last_note[note].length = current_time - last_note[note].start_time

        # Return full scrolling notes list
        return scrolling_notes   
    
    def reset(self):
        """Stops and resets the song."""
        # Stops song and clears display information
        self.stop()
        self.notes_pressed.clear()
        self.active_scrolling_notes.clear()  

        # Resets timing and progress indicators
        self._message_index = 0
        self._scrolling_note_index = 0
        self._message_delta_time = 0
        self._scrolling_note_delta_time = 0

    def start(self):
        """Starts playing the song."""
        self.playing = True

    def stop(self):
        """Stops playing the song."""
        self.playing = False
        self._last_frame= None
        self.audio_output.reset()

    def toggle_playing(self):
        """Toggles if the song is playing or not."""
        (self.stop if self.playing else self.start)()

    def update(self):
        """ Updates the song and advances time. 
            Should be called every frame for accurate song playback.
        """

        # Doesn't update song if it isn't currently playing
        if not self.playing: 
            return

        # Sets initial last frame value to the current frame
        if self._last_frame is None:
            self._last_frame = time.perf_counter()

        # Calculates time difference since the last frame and updates tracker values
        delta_time = time.perf_counter() - self._last_frame
        self._scrolling_note_delta_time += delta_time
        self._message_delta_time += delta_time
        self._last_frame = time.perf_counter()

        # Updates all currently active scrolling notes with the time difference 
        for active_note in self.active_scrolling_notes:
            active_note.update_time(delta_time)

        # Activates the next scrolling notes that have had their time exceeded
        while self.display_settings.scrolling_notes and self._scrolling_note_index < self.scrolling_notes_length \
                and self.scrolling_notes[self._scrolling_note_index].time <= self._scrolling_note_delta_time:
            next_scrolling_note = self.scrolling_notes[self._scrolling_note_index]
            self._scrolling_note_delta_time -= next_scrolling_note.time
            self.active_scrolling_notes.append(next_scrolling_note)
            next_scrolling_note.activate()
            self._scrolling_note_index += 1

        # Sends messages that have had their time exceeded to the audio output
        while self._message_index < len(self) and next(self).time <= self._message_delta_time:
            self._message_delta_time -= next(self).time
            if not next(self).is_meta:
                self.audio_output.send(next(self))
                if next(self).type.startswith('note'):
                    self.notes_pressed[next(self).note] = (next(self).channel, next(self).type == 'note_on' and next(self).velocity > 0)
            self._message_index += 1
            
        # Resets the song if the end has been reached
        if self._message_index >= len(self):
            self.reset()
