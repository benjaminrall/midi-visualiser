class ScrollingNote:
    def __init__(self, note, time, note_time, start_time, length = 0) -> None:
        self.note = note
        self.length = length
        self.time = time
        self.start_time = start_time
        self.note_time = note_time

        self.activate()

    def activate(self):
        self.current_time = 0
        self.end_time = self.note_time + self.length

    def get_percentage(self):
        return self.current_time / self.note_time
    
    def update_time(self, delta_time):
        self.current_time += delta_time
    
    def check_active(self):
        return self.current_time <= self.end_time
