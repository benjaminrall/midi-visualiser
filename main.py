import os
import sys
import mido
import pygame
from song import Song
from piano_display import PianoDisplay
from piano_display_settings import PianoDisplaySettings

# Adjustable Display Settings
DISPLAY_SETTINGS = PianoDisplaySettings()

# Path to a folder containing MIDI files to be used as preset songs
PRESET_SONGS_FOLDER = "songs"   

def load_song(file_name: str, sound_output: mido.ports.IOPort, display_settings: PianoDisplaySettings, verbose: bool = True) -> Song | None:
    """Attempts to load a song from a given filename. Returns None if the song couldn't be loaded."""
    # Adds MIDI file extension if it wasn't specified
    if not file_name.endswith(".mid"):
        file_name += ".mid"

    # Attempts to load song
    try:
        song = Song(file_name, sound_output, display_settings)
        if verbose: 
            print(f"MIDI file '{file_name}' loaded successfully.")
        return song
    except Exception as e:
        if verbose: 
            print(f"Failed to load MIDI file '{file_name}': {e}.")
        return None
    
def load_preset(index: int, presets: list[str], sound_output: mido.ports.IOPort, display_settings: PianoDisplaySettings, verbose: bool = True) -> Song | None:
    """Attempts to load a preset with a given index from the preset songs folder. Returns None if the song couldn't be loaded."""
    # Checks that there are preset songs
    if len(presets) == 0:
        if verbose:
            print("No preset songs were loaded.")
        return None
    
    # Adjusts index to stay in range of presets list
    if index < 0 or index >= len(presets):
        index = index % len(presets)

    # Loads and returns the preset song
    return load_song(presets[index], sound_output, display_settings, verbose)

def main(argv: list[str]) -> None:
    """Main program entry point."""
    # Sets up pygame window and piano display
    display = PianoDisplay(DISPLAY_SETTINGS)
    win = pygame.display.set_mode((display.width, display.height))
    pygame.display.set_caption("Piano MIDI Visualiser")
    icon_img = pygame.image.load(os.path.join("imgs", "icon.png"))
    pygame.display.set_icon(icon_img)
    
    # Initial empty draw to the window
    display.draw(win)
    pygame.display.update()

    # Opens sound output to default MIDI output
    sound_output = mido.open_output()

    # Attempts to load preset songs
    current_preset_index = 0
    preset_songs = []
    try:
        for file in os.listdir(PRESET_SONGS_FOLDER):
            if file.endswith(".mid"):
                preset_songs.append(os.path.join(PRESET_SONGS_FOLDER, file))
    except FileNotFoundError:
        print(f"Failed to load preset songs from the folder '{PRESET_SONGS_FOLDER}'")

    # Attempts to load song from command line argument
    song_file = argv[0] if len(argv) > 0 else ""
    song = None
    if song_file != "":
        song = load_song(song_file, sound_output, DISPLAY_SETTINGS)
    if len(preset_songs) > 0 and song is None:
        song = load_preset(0, preset_songs, sound_output, DISPLAY_SETTINGS)

    # Main Loop
    running = True
    while running:
        for event in pygame.event.get():
            # Checks for quitting the game
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sound_output.close()
                exit()
            # Stops song if the window is moved to prevent bugs
            elif event.type == pygame.WINDOWMOVED and song is not None:
                song.stop()
            # Checks for key presses
            elif event.type == pygame.KEYDOWN:
                # Reset and play/pause song
                if event.key == pygame.K_r and song is not None:
                    song.reset()
                elif event.key == pygame.K_SPACE and song is not None:
                    song.toggle_playing()
                # Inputting new song name
                elif event.key == pygame.K_i:
                    if song is not None:
                        song.stop()
                    if (new_song := load_song(input("Enter MIDI file name: "), sound_output, DISPLAY_SETTINGS)) is not None:
                        song = new_song
                # Preset song loading
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    current_preset_index += 1 if event.key == pygame.K_RIGHT else -1
                    song = song if (s := load_preset(current_preset_index, preset_songs, sound_output, DISPLAY_SETTINGS)) is None else s

        # Updates and draws song
        if song is not None:
            song.update()  
        display.draw(win, song)
        pygame.display.update()

if __name__ == "__main__":
    main(sys.argv[1:])