import mido
import time
from collections import defaultdict
from .piano_display_settings import PianoDisplaySettings
from .scrolling_note import ScrollingNote

class Song:
    """Class representing a song loaded from a MIDI file."""

    def __init__(self, file_name: str, audio_output: mido.ports.IOPort, display_settings: PianoDisplaySettings) -> None:
        """Initialises the Song object by loading and processing the given MIDI file."""
        self.audio_output = audio_output
        self.display_settings = display_settings
        self.midi_file = mido.MidiFile(file_name, clip=True)

        self.messages: list[mido.Message] = []
        
        self.scrolling_notes: list[ScrollingNote] = []
        self.active_scrolling_notes: list[ScrollingNote] = []
        self.notes_pressed = defaultdict(lambda : (0, False))

        self.playing = False
        self._initialise_song_data()
        self.reset()

    def __len__(self) -> int:
        """Returns the number of MIDI messages in the song."""
        return len(self.messages)
    
    def __getitem__(self, index: int) -> mido.Message:
        """Returns the message at a given index."""
        return self.messages[index]
    
    def __next__(self) -> mido.Message:
        """Returns the next message to execute based on the current message index."""
        return self[self._message_index]

    def _initialise_song_data(self) -> None:
        """Generates messages and scrolling notes lists to represent the song data."""
        # Prepends a buffer message to delay the song start so notes can scroll to the piano
        buffer_time = self.display_settings.note_time
        self.messages = [mido.Message('note_off', time=buffer_time)] + list(self.midi_file)

        # Generates scrolling note data
        if self.display_settings.scrolling_notes:
            self.scrolling_notes = self._generate_scrolling_notes()

    def _generate_scrolling_notes(self) -> list[ScrollingNote]:
        """
        Pre-processes MIDI messages to gnereate a list of all notes with
        their start times and calculated durations.
        """
        open_notes: dict[int, ScrollingNote] = defaultdict(lambda : None)
        notes = []
        current_time = 0
        delta_time = 0

        # Loops through all messages except the buffer message to create scrolling notes
        for msg in self.messages[1:]:
            # Add to current and delta time
            current_time += msg.time 
            delta_time += msg.time

            # Ignores non-note entries
            if not msg.type.startswith("note"):
                continue

            # Checks if the note is starting or ending
            if msg.type == "note_on" and msg.velocity > 0:
                # If the same note was already playing, ends the previous one before starting the new one
                if existing_note := open_notes[msg.note]:
                    existing_note.length = current_time - existing_note.start_time

                # Creates the new scrolling note object
                new_note = ScrollingNote(
                    note=msg.note - 21,
                    channel=msg.channel,
                    delta_time=delta_time,
                    start_time=current_time,
                    note_time=self.display_settings.note_time
                )

                # Stores new note and resets delta time
                open_notes[msg.note] = new_note
                notes.append(new_note)
                delta_time = 0
            elif note_to_end := open_notes[msg.note]:
                # If a note has ended, calculates its length and closes it
                note_to_end.length = current_time - note_to_end.start_time
                open_notes[msg.note] = None

        # Calculates lengths for all remaining open notes
        for note in open_notes.values():
            if note:
                note.length = current_time - note.start_time

        return notes
    
    def reset(self) -> None:
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

    def start(self) -> None:
        """Starts playing the song."""
        self.playing = True
        self._last_frame_time = None

    def stop(self) -> None:
        """Stops playing the song."""
        self.playing = False
        self.audio_output.reset()

    def toggle_playing(self) -> None:
        """Toggles if the song is playing or not."""
        (self.stop if self.playing else self.start)()

    def update(self) -> None:
        """
        Updates the song's state by processing events based on elapsed time.
        This method should be called once per frame for accurate playback.
        """

        # Doesn't update the song if it isn't currently playing
        if not self.playing:
            return
        
        # Initialises or calculates delta time
        now = time.perf_counter()
        if self._last_frame_time is None:
            delta_time = 0
        else:
            delta_time = now - self._last_frame_time
        self._last_frame_time = now

        self._message_delta_time += delta_time
        self._scrolling_note_delta_time += delta_time

        # Updates all currently visible scrolling notes and removes inactive ones
        active_notes = []
        for note in self.active_scrolling_notes:
            note.update(delta_time)
            if note.active:
                active_notes.append(note)
        self.active_scrolling_notes = active_notes

        # Activates new scrolling notes as their time arrives
        while self.display_settings.scrolling_notes and self._scrolling_note_index < len(self.scrolling_notes) \
                and self.scrolling_notes[self._scrolling_note_index].delta_time <= self._scrolling_note_delta_time:
            next_scrolling_note = self.scrolling_notes[self._scrolling_note_index]
            self._scrolling_note_delta_time -= next_scrolling_note.delta_time
            self.active_scrolling_notes.append(next_scrolling_note)
            next_scrolling_note.activate(self._scrolling_note_delta_time)
            self._scrolling_note_index += 1
        
        # Processes and sends MIDI messages as their time arrives
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
