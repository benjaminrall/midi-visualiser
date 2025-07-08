# MIDI Visualiser
A real-time MIDI player and visualiser built in Python.

![MIDI Visualiser Demonstration GIF](https://github.com/user-attachments/assets/6bbbe8f7-e93b-4289-8eb1-d0823b3c3bfe)

## Instructions for use
Clone the project
```bash
git clone https://github.com/benjaminrall/midi-visualiser.git
```

Navigate to the project directory
```bash
cd midi-visualiser
```

Install required packages
```bash
pip install -r requirements.txt
```

Run program
```bash
python main.py [path]
```
If a valid path to a MIDI file is specified then it will be loaded and run.
Otherwise, it will default to loading preset songs from the 'songs' folder.

Use the space key to play/pause the MIDI file. The current state is indicated by a play/pause icon in the top left of the window. The song will automatically pause if the window is moved to avoid desync.

Once a song finishes playing, it will automatically reset to the start of the file. You can do this manually at any time by pressing the R key.

To switch to a new MIDI file, press the I key and then type a new file path into the terminal.

You can switch between the preset songs by using the left and right arrow keys.
