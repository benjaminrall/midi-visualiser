import os
import mido
import pygame
from .song import Song
from .piano_display import PianoDisplay
from .piano_display_settings import PianoDisplaySettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Visualiser:
    """Manages the Pygame visualiser window and main application loop."""

    DEFAULT_SONGS_FOLDER = os.path.join(BASE_DIR, "songs")

    def __init__(self, path: str | None):
        """Initialises the visualiser and loads the initial song(s)."""
        # Creates Piano Display
        self.settings = PianoDisplaySettings()
        self.display = PianoDisplay(self.settings)
        
        # Mido sound output setup
        self.sound_output = mido.open_output()

        # Attempts to find and store all song filenames found at the given path
        self.current_song_index = 0
        self.song_files = self._get_song_files(path or Visualiser.DEFAULT_SONGS_FOLDER)
        if len(self.song_files) == 0:
            raise RuntimeError(f"No MIDI files found at the path: {path}")
        self.song: Song | None = self._load_song(self.song_files[self.current_song_index]) 

        # Pygame initialisation and setup
        if not pygame.get_init():
            pygame.init()
        self.win = pygame.display.set_mode((self.display.width, self.display.height))
        pygame.display.set_caption("Piano MIDI Visualiser")
        try:
            icon_img = pygame.image.load(os.path.join(BASE_DIR, "imgs", "icon.png"))
            pygame.display.set_icon(icon_img)
        except pygame.error as e:
            print(f"Could not load window icon: {e}")
        self.clock = pygame.time.Clock()
        
        # Application state
        self.running = False

    def _get_song_files(self, path: str) -> list[str]:
        """Gets a list of MIDI song files from the given path."""
        # Handles erroneous paths
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"Could not find MIDI song files at the path: {path}")

        if os.path.isdir(path):
            song_files = []
            for file in sorted(os.listdir(path)):
                if file.lower().endswith(".mid"):
                    song_files.append(os.path.join(path, file))
            return song_files
        elif os.path.isfile(path) and path.lower().endswith(".mid"):
            return [path]
        
        return []

    def _load_song(self, file_path: str, verbose: bool = True) -> Song | None:
        """Attempts to load a Song object from a given file path."""
        try:
            song = Song(file_path, self.sound_output, self.settings)
            if verbose:
                print(f"MIDI file '{file_path}' loaded successfully.")
            return song
        except Exception as e:
            if verbose:
                print(f"Failed to load MIDI file '{file_path}': {e}.")
            return None

    def run(self):
        """Contains the main loop for the application."""
        self.running = True
        while self.running:
            # Handles Pygame events
            self._handle_events()

            # Updates the current song, if one exists
            if self.song:
                self.song.update()

            # Draws the current state to the Pygame window
            self.display.draw(self.win, self.song)
            pygame.display.update()

            self.clock.tick(60)

        # Cleans up necessary resources
        self._cleanup()

    def _handle_events(self):
        """Processes all Pygame events for the application."""
        for event in pygame.event.get():
            # Handles quitting the Pygame window
            if event.type == pygame.QUIT:
                self.running = False
            # Stops song if the window is moved to prevent audio misalignment
            elif event.type == pygame.WINDOWMOVED and self.song:
                self.song.stop()
            # Handles any key presses
            elif event.type == pygame.KEYDOWN:
                self._handle_keypress(event.key)
    
    def _handle_keypress(self, key: int):
        """Handles all Pygame key press events."""
        # Quitting the game with 'Q'
        if key == pygame.K_q:
            self.running = False
        # Resetting the current song with 'R'
        elif key == pygame.K_r and self.song:
            self.song.reset()
        # Playing/pausing the current song with space
        elif key == pygame.K_SPACE and self.song:
            self.song.toggle_playing()
        # Cycling through loaded songs with the arrow keys
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            # Stops the current song
            if self.song:
                self.song.stop()

            # Loads the next song
            delta = 1 if key == pygame.K_RIGHT else -1
            self.current_song_index = (self.current_song_index + delta) % len(self.song_files)
            self.song = self._load_song(self.song_files[self.current_song_index]) 

    def _cleanup(self):
        """Ensures all resources are closed properly."""
        if self.sound_output:
            self.sound_output.close()
        if pygame.get_init():
            pygame.quit()