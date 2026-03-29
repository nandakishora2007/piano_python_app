# Yamaha PSR-i455 Professional MIDI Studio

A professional-grade music production application for musicians using the Yamaha PSR-i455 keyboard.

## Features

### 🎹 Core Capabilities
- **Real-time MIDI I/O**: Direct connection to Yamaha PSR-i455
- **Multi-track Recording**: Record multiple tracks and layer performances
- **Professional Keyboard Visualization**: Full 88-key piano display with real-time note feedback
- **Session Management**: Save and load recording sessions in JSON format
- **MIDI File Export**: Export recordings as standard .mid files for use in DAWs

### 🎵 Music Theory & Analyzer
- **Chord Recognition**: Real-time detection of played chords with confidence scoring
- **Scale Detection**: Identify scales from played notes
- **Scale Visualization**: Visual display of scale degrees on the keyboard
- **Note Analysis**: Detailed information about played notes and intervals
- **Performance Metrics**: Velocity tracking, latency monitoring, and statistics

### 🎛️ Controls & Settings
- **BPM Control**: Adjustable tempo from 40-300 BPM
- **Scale Selection**: 11 different scales (Major, Minor, Pentatonic, Blues, etc.)
- **Multi-track Support**: Up to 16 simultaneous tracks
- **Recording Status**: Clear visual feedback for recording state
- **Session Metadata**: Track composer, style, key, and notes

### 📊 Professional UI
- Real-time velocity meter with gradient visualization
- Control panel showing session status and BPM
- Information panel with chord/scale analysis
- Performance FPS and latency display
- Dark professional color scheme optimized for extended sessions

## Installation

### Prerequisites
- Python 3.8+
- Yamaha PSR-i455 keyboard connected via USB

### Setup

1. **Create Virtual Environment**:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify MIDI Connections**:
```bash
python main.py
```
This will list available MIDI ports. Verify your Yamaha appears in both INPUT and OUTPUT.

## Usage

### Starting the Application

```bash
python studio.py
```

### Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **R** | Start Recording |
| **T** | Stop Recording |
| **P** | Playback (in development) |
| **C** | Clear Current Track |
| **E** | Export to MIDI |
| **S** | Save Session |
| **L** | Load Session |
| **+** | Increase BPM |
| **-** | Decrease BPM |
| **1** | Major Scale |
| **2** | Minor Scale |
| **3** | Pentatonic Scale |
| **4** | Blues Scale |
| **5** | Harmonic Minor Scale |
| **Q** | Quit Application |

### Workflow

1. **Start Recording**: Press [R] to begin recording. The display will show "🔴 RECORDING"
2. **Play Your Ideas**: Use your Yamaha keyboard to perform. The app displays:
   - Active notes on the 88-key visualization
   - Detected chords and confidence level
   - Identified scale from your playing
   - Real-time velocity feedback
3. **Stop Recording**: Press [T] to stop
4. **Analyze**: Review the detected scales and chords from your session
5. **Save**: Press [S] to save session, or [E] to export as MIDI for your DAW

## File Structure

```
piano/
├── studio.py                 # Main application
├── config.py                 # Configuration settings
├── midi_handler.py          # MIDI I/O with threading
├── recording.py             # Session and track management
├── music_theory.py          # Chord/scale analysis
├── renderer.py              # UI visualization components
├── requirements.txt         # Python dependencies
│
├── sessions/                # Saved session files (.json)
├── recordings/              # MIDI recordings
├── exports/                 # Exported MIDI files
└── README.md               # This file
```

## Audio Analysis

### Chord Recognition
The application analyzes played notes and identifies:
- Root note of the chord
- Chord type (Major, Minor, Diminished, 7th extensions, etc.)
- Confidence percentage (0-100%)

Supported chords include: Major, Minor, Diminished, Augmented, Major 7, Minor 7, Dominant 7, Major 9, Minor 9, Sus2, Sus4

### Scale Detection
Identifies the scale from played notes among:
- Major
- Minor (3 variants: Natural, Harmonic, Melodic)
- Modal scales (Dorian, Phrygian, Lydian, Mixolydian)
- Blues
- Pentatonic
- Whole Tone

## Performance Metrics

- **Latency**: MIDI input latency displayed in milliseconds
- **FPS**: Frame rate in top-right corner
- **CPU Load**: Optimized for low-latency performance
- **Note Count**: Total number of recorded notes

## Session Format

Sessions are saved as JSON with full MIDI data:

```json
{
  "name": "Session Name",
  "bpm": 120,
  "time_signature": {
    "numerator": 4,
    "denominator": 4
  },
  "metadata": {
    "composer": "Your Name",
    "style": "Genre/Style",
    "key": "C Major",
    "notes": "Any notes about the session"
  },
  "tracks": [
    {
      "name": "Track 1",
      "channel": 0,
      "messages": [...]
    }
  ]
}
```

## MIDI Export

Exports standard .mid files compatible with:
- DAWs (Ableton, Logic, Pro Tools, Reaper, Cubase, etc.)
- Music notation software
- MIDI processors and tools
- Other hardware synthesizers

## Advanced Features

### Custom Scales
Edit `music_theory.py` to add custom scales:

```python
CUSTOM_SCALE = [0, 2, 4, 6, 8, 10]  # Whole tone example
```

### MIDI Controllers
Modify `midi_handler.py` to add custom CC messages, program changes, etc.:

```python
handler.send_control_change(7, 100)  # Master volume
handler.send_program_change(0)       # Program select
```

### Custom Track Workflow
Add tracks programmatically:

```python
session.add_track("Bass")
session.add_track("Melody")
session.add_track("Chords")
session.select_track(0)  # Select Bass track
```

## Troubleshooting

### MIDI Connection Issues

1. **Check MIDI ports**:
```bash
python main.py
```
Verify "Digital Keyboard 0" and "Digital Keyboard 1" appear in the output

2. **Restart MIDI services** (Windows):
```powershell
# In PowerShell as Administrator
Restart-Service AudioEndpointBuilder
```

3. **Update Yamaha drivers**: Visit Yamaha support website for latest USB drivers

### Performance Issues

- Close other MIDI applications
- Disable unnecessary background processes
- Use a USB 3.0 port or powered USB hub
- Reduce number of active tracks if needed

### Recording Quality

- Ensure Yamaha velocity is set to ON
- Use local control OFF if experiencing double notes
- Check MIDI channel assignment matches track channel

## Development Notes

### Architecture
- **Modular design**: Separate concerns (MIDI, Theory, Recording, UI)
- **Threading**: MIDI input runs on dedicated thread for low-latency
- **Callback system**: Non-blocking message processing
- **Configuration-driven**: Easy customization via config.py

### Future Enhancements
- Playlist management
- MIDI effects/processors
- Undo/Redo system
- Quantization engine
- Automatic accompaniment
- Performance recording and analysis
- VST plugin hosting

## License

Professional use encouraged. Feedback and improvements welcome.

## Credits

Built for musicians by musicians using Python, pygame, and mido.

---

**Yamaha PSR-i455 Professional MIDI Studio** - Elevate your musical workflow.
