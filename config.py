# Professional MIDI Music Application - Configuration
import os
from pathlib import Path

# Application settings
APP_NAME = "Yamaha PSR-i455 Professional Studio"
APP_VERSION = "1.0.0"
AUTHOR = "Musician Grade Application"

# MIDI Configuration
MIDI_INPUT_PORT = "Digital Keyboard 0"
MIDI_OUTPUT_PORT = "Digital Keyboard 1"
MIDI_BUFFER_SIZE = 4096

# Audio Configuration
SAMPLE_RATE = 44100
BUFFER_SIZE = 512

# UI Configuration
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
REFRESH_RATE = 60  # FPS

# Paths
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
RECORDINGS_DIR = BASE_DIR / "recordings"
EXPORTS_DIR = BASE_DIR / "exports"

# Create directories if they don't exist
for dir_path in [SESSIONS_DIR, RECORDINGS_DIR, EXPORTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Piano Configuration
PIANO_KEYS = 88  # Full 88-key piano
PIANO_START_NOTE = 21  # A0
PIANO_END_NOTE = 108  # C8

# MIDI Configuration Constants
NOTES_PER_OCTAVE = 12
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Performance thresholds
MAX_LATENCY_MS = 10
VELOCITY_THRESHOLD = 10

# Color scheme (Dark mode - Professional)
COLORS = {
    'background': (20, 20, 25),
    'white_key': (245, 245, 245),
    'black_key': (40, 40, 45),
    'black': (0, 0, 0),
    'active_white': (100, 200, 255),
    'active_black': (100, 200, 255),
    'accent': (0, 150, 255),
    'text': (220, 220, 225),
    'grid': (60, 60, 70),
    'red': (220, 80, 80),
    'green': (100, 200, 100),
    'yellow': (200, 180, 80),
}

# Recording settings
DEFAULT_BPM = 120
QUANTIZE_OPTIONS = [2, 4, 8, 16, 32]  # note divisions
MAX_TRACKS = 16
