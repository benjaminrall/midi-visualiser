import os
import sys
import mido
import pygame
from piano_display import PianoDisplay
from song import Song

# Program Settings
KEY_WIDTH = 20      # The width of each white piano key in pixels (affects window size)
KEY_RATIO = 5       # The ratio of a key's width to its height
NOTE_TIME = 2       # The amount of time that a note is shown before being played

PRESET_SONGS = [
    "songs/pirates",
    "songs/mii_channel",
    "songs/tetris",
    "songs/moonlight_sonata",
    "songs/all_star",
]

def load_song(file_name, display, sound_output) -> Song:
    if not file_name.endswith(".mid"):
        file_name += ".mid"
    try:
        song = Song(file_name, display, sound_output)
        print(f"MIDI file '{file_name}' loaded successfully.")
        return song
    except FileNotFoundError:
        print(f"Failed to load MIDI file: '{file_name}'")
        return None

def main(argv: list[str]) -> None:
    # Display Setup
    display = PianoDisplay(KEY_WIDTH, KEY_RATIO, NOTE_TIME)
    pygame.display.set_caption("Piano MIDI Visualiser")
    icon_img = pygame.image.load(os.path.join("imgs", "icon.png"))
    pygame.display.set_icon(icon_img)

    # Opens sound output to default MIDI output
    sound_output = mido.open_output()

    # Loads MIDI song
    song_file = argv[0] if len(argv) > 0 else ""
    if song_file != "":
        song = load_song(song_file, display, sound_output)
    if song_file == "" or song is None:
        song = load_song(PRESET_SONGS[0], display, sound_output)

    # Main Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sound_output.close()
                exit(0)
            elif event.type == pygame.KEYDOWN:
                # Reset and play/pause song
                if event.key == pygame.K_r:
                    song.reset()
                elif event.key == pygame.K_SPACE:
                    song.toggle_playing()
                # Inputting new song name
                elif event.key == pygame.K_i:
                    song.stop()
                    song_file = input("Enter MIDI file name: ")
                    try:
                        song = Song(song_file, display, sound_output)
                        print(f"MIDI file '{song_file}' loaded successfully.")
                    except FileNotFoundError:
                        print(f"Failed to load MIDI file: '{song_file}'")
                # Preset song loading
                elif event.key == pygame.K_1:
                    song = load_song(PRESET_SONGS[0], display, sound_output)
                elif event.key == pygame.K_2:
                    song = load_song(PRESET_SONGS[1], display, sound_output)
                elif event.key == pygame.K_3:
                    song = load_song(PRESET_SONGS[2], display, sound_output)
                elif event.key == pygame.K_4:
                    song = load_song(PRESET_SONGS[3], display, sound_output)
                elif event.key == pygame.K_5:
                    song = load_song(PRESET_SONGS[4], display, sound_output)

        song.play()  
        

if __name__ == "__main__":
    main(sys.argv[1:])