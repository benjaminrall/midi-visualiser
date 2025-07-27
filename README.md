# Python MIDI Visualiser 🎹

A real-time MIDI player and visualiser built with Python and Pygame.

This tool can be run from the command line to open any `.mid` file as a dynamic, scrolling piano roll, synchronising the on-screen notes with the audio output.

![MIDI Visualiser Demonstration GIF](https://github.com/user-attachments/assets/6bbbe8f7-e93b-4289-8eb1-d0823b3c3bfe)

## Key Features

- 🎵 **MIDI File Parsing**: Uses the Mido library to load and interpret note events and channels from MIDI files
- 🎹 **Real-time Piano Roll**: Dynamically renders scrolling notes as the music plays
- 🔊 **Synchronised Audio**: Plays the MIDI data through Pygame's audio mixer, synchronised with the visuals
- ⏯️ **Playback Control**: Includes standard playback features like play, pause, and restart, controlled via keyboard shortcuts
- 🎨 **Multi-channel Colouring**: Automatically assigns different, clear colours to notes from different MIDI channels

## Installation and Usage

To use the tool, you can simply install it using `pip`:

```shell
pip install midi-visualiser
```

It can then be used in the command line through the `visualiser` command. The command has two different modes:

1. **Visualising a single song**:

   ```shell
   visualiser path/to/your/song.mid
   ```

2. **Loading a playlist from a directory**:

   ```shell
   visualiser path/to/your/songs/folder/
   ```

   When a path to a directory is provided, all `.mid` files in the directory will be loaded and can then be switched between using the left and right arrow keys.

### Example Songs

The project is packaged with 10 example songs, which will be automatically loaded when the `visualiser` command is run without specifying any arguments.

## Playback Controls

The following keyboard shortcuts are available while the visualiser window is active:

| Key           | Action                                                   |
| :------------ | :------------------------------------------------------- |
| **Space**     | Play / Pause the current song.                           |
| **R**         | Reset the current song to the beginning.                 |
| **←** / **→** | Cycle to the previous/next song in the current playlist. |
| **Q**         | Close the application window.                            |

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) as a package and virtual environment manager. To set up the project for development, follow these steps:

1. **Clone the repository**:

   ```sh
   git clone https://github.com/benjaminrall/midi-visualiser.git
   cd midi-visualiser
   ```

2. **Create the virtual environment using [uv](https://github.com/astral-sh/uv)**:

   ```sh
   uv venv
   ```

3. **Install the project in editable mode**:

   ```sh
   uv pip install -e .
   ```

   This will allow use of the `visualiser` command such that any changes made to the source code will be immediately reflected.

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](./LICENSE) file for details.
