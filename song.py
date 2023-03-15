import mido
from piano_display import PianoDisplay
from collections import defaultdict
import time
from scrolling_note import ScrollingNote


class Song:
    def __init__(self, file_name: str, display: PianoDisplay, audio_output: mido.ports.IOPort, show_scrolling_notes = True) -> None:
        # Tracks song time and progress
        self._message_index = 0
        self._scrolling_note_index = 0
        self._message_delta_time = 0
        self._scrolling_note_delta_time = 0
        self._last_frame = None

        self.midi_file = mido.MidiFile(file_name, clip=True)
        self.display = display
        self.audio_output = audio_output
        self.audio_output.reset()
        self.show_scrolling_notes = show_scrolling_notes
        
        self.messages = [msg for msg in self.midi_file if not msg.is_meta and (msg.is_cc() or msg.type.startswith("note") and 21 <= msg.note <= 108)]
        self.scrolling_notes = self.generate_scrolling_notes()     
        self.messages.insert(0, mido.Message('note_off', time=display.note_time))
        self.length = len(self.messages)
        self.scrolling_notes_amount = len(self.scrolling_notes)
        self.notes_pressed = defaultdict(lambda : False)
        self.active_scrolling_notes = []
        self.playing = False

    def __len__(self) -> int:
        return self.length
        
    def __getitem__(self, index: int) -> mido.Message:
        return self.messages[index]
    
    def __next__(self) -> mido.Message:
        return self.messages[self._message_index]
    
    def generate_scrolling_notes(self):
        scrolling_notes = []
        last_note = defaultdict(lambda : None)
        current_time = 0
        previous_time = 0
        for msg in self.messages:
            current_time += msg.time
            if msg.type.startswith("note"):
                if msg.type == "note_on" and msg.velocity > 0:
                    new_note = ScrollingNote(msg.note - 21, current_time - previous_time, self.display.note_time, current_time)
                    if last_note[msg.note] is not None:
                        last_note[msg.note][1].length = current_time - last_note[msg.note][1].start_time
                    last_note[msg.note] = (current_time, new_note)
                    scrolling_notes.append(new_note)
                    previous_time = current_time
                elif last_note[msg.note] is not None:
                    last_note[msg.note][1].length = current_time - last_note[msg.note][1].start_time
                    last_note[msg.note] = None         
        return scrolling_notes   
    
    def reset(self):
        self.stop()
        self.notes_pressed.clear()
        self.active_scrolling_notes.clear()  
        self._message_index = 0
        self._scrolling_note_index = 0
        self._message_delta_time = 0
        self._scrolling_note_delta_time = 0

    def start(self):
        self.playing = True

    def stop(self):
        self.playing = False
        self._last_frame= None
        self.audio_output.reset()

    def toggle_playing(self):
        (self.stop if self.playing else self.start)()

    def update(self):
        if not self.playing: 
            return

        if self._last_frame is None:
            self._last_frame = time.perf_counter()

        delta_time = time.perf_counter() - self._last_frame
        self._scrolling_note_delta_time += delta_time
        self._message_delta_time += delta_time
        self._last_frame = time.perf_counter()

        if self.show_scrolling_notes:
            for active_note in self.active_scrolling_notes:
                active_note.update_time(delta_time)

            while self._scrolling_note_index < self.scrolling_notes_amount and \
                    self.scrolling_notes[self._scrolling_note_index].time <= self._scrolling_note_delta_time:
                next_scrolling_note = self.scrolling_notes[self._scrolling_note_index]
                self._scrolling_note_delta_time -= next_scrolling_note.time
                self.active_scrolling_notes.append(next_scrolling_note)
                next_scrolling_note.activate()
                self._scrolling_note_index += 1

        while self._message_index < len(self) and next(self).time <= self._message_delta_time:
            self._message_delta_time -= next(self).time
            self.audio_output.send(next(self))
            if next(self).type.startswith('note'):
                self.notes_pressed[next(self).note] = next(self).type == 'note_on' and next(self).velocity > 0
            self._message_index += 1
            
        if self._message_index >= len(self):
            self.reset()


    def draw(self):
        self.display.draw(self.notes_pressed, self.active_scrolling_notes, self.playing)

    def play(self):
        self.update()
        self.draw()
