import argparse
import pygame
import pygame.midi
import mido
from visualiser import Visualiser

def main():
    """Initializes Pygame and Mido, parses command line arguments, and runs the visualiser."""
    # Parses the command line argument for the file path
    parser = argparse.ArgumentParser(
        description="A real-time MIDI player and visualiser."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Optional path to a MIDI file or a directory of MIDI files."
    )
    args = parser.parse_args()

    try:
        # Sets up Pygame and Mido for audio playback
        pygame.init()
        pygame.midi.init()
        mido.set_backend('mido.backends.pygame')

        # Runs the visualiser
        app = Visualiser(args.path)
        app.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensures Pygame always quits successfully
        if pygame.get_init():
            pygame.quit()

if __name__ == "__main__":
    main()