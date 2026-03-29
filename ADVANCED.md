# Advanced Usage Guide - Yamaha PSR-i455 Professional MIDI Studio

## Custom Scale Definitions

### Adding Your Own Scales

Edit `music_theory.py` in the `Scale` class to add custom scales:

```python
class Scale:
    CUSTOM_JAZZ = [0, 2, 3, 5, 7, 8, 10]  # Dorian with flat 9
    CHROMATIC = list(range(12))  # All 12 semitones
    AUGMENTED = [0, 3, 4, 7, 8, 11]  # Whole tone derivative
```

Then update `Scale.ALL`:
```python
'Custom Jazz': CUSTOM_JAZZ,
'Chromatic': CHROMATIC,
```

## Advanced MIDI Configuration

### Using Different Channels

```python
# In studio.py, modify track creation:
track = RecordingSession()
track.add_track("Bass", channel=0)
track.add_track("Melody", channel=1)
track.add_track("Drums", channel=9)  # Drums on channel 10
```

### Sending Control Changes

```python
# Modify volume, effects, etc.
midi.send_control_change(control=7, value=100)   # Volume
midi.send_control_change(control=10, value=64)   # Pan
midi.send_control_change(control=91, value=50)   # Reverb
```

## Performance Optimization

### Latency Tuning

1. **Windows Audio**: Reduce ASIO buffer size in Yamaha settings
2. **Python Settings**: Adjust in `config.py`:
```python
MIDI_BUFFER_SIZE = 2048  # Smaller = lower latency (but more CPU)
BUFFER_SIZE = 256        # For best real-time performance
```

3. **Process Priority** (Windows):
```powershell
# Run in PowerShell as Admin
$process = Get-Process python
$process.PriorityClass = 'High'
```

## Extending the Application

### Adding a Metronome

```python
import threading

class Metronome:
    def __init__(self, bpm: int, midi_handler: MIDIHandler):
        self.bpm = bpm
        self.midi = midi_handler
        self.running = False
        self.click_note = 76  # A5
    
    def start(self):
        self.running = True
        threading.Thread(target=self._beat_loop, daemon=True).start()
    
    def _beat_loop(self):
        interval = 60 / self.bpm
        while self.running:
            self.midi.send_note_on(self.click_note, 100)
            time.sleep(0.1)
            self.midi.send_note_off(self.click_note)
            time.sleep(interval - 0.1)
```

### Custom Note Filters

```python
class NoteFilter:
    """Filter notes to a specific range or scale"""
    
    def __init__(self, min_note: int = 36, max_note: int = 96):
        self.min_note = min_note
        self.max_note = max_note
    
    def is_valid(self, note: int) -> bool:
        return self.min_note <= note <= self.max_note
```

## Session Templates

Create reusable session templates:

```python
# Create template in Python:
def create_orchestral_template():
    session = RecordingSession("Orchestral Arrangement", bpm=90)
    session.add_track("Strings")
    session.add_track("Woodwinds")
    session.add_track("Brass")
    session.add_track("Percussion")
    return session
```

## Integration with DAWs

### Ableton Live
1. Export MIDI: Press [E]
2. Drag .mid file into Ableton
3. Adjust quantization and timing

### Logic Pro
1. Export: MIDI file
2. Import: File > Import > MIDI File
3. Edit in Logic Project

### Pro Tools
1. Export MIDI (Yamaha format)
2. Import: File > Import > MIDI
3. Map to virtual instruments

## MIDI CC Mappings for Yamaha PSR-i455

Common control changes:

| CC # | Function | Range |
|------|----------|-------|
| 7 | Master Volume | 0-127 |
| 10 | Pan | 0-127 |
| 64 | Sustain Pedal | 0-127 |
| 91 | Reverb Effect | 0-127 |
| 93 | Chorus Effect | 0-127 |
| 120 | All Sound Off | - |
| 121 | Reset All Controllers | - |
| 123 | All Notes Off | - |

## Batch Processing Recordings

### Convert All MIDI Files to JSON

```python
from pathlib import Path
from recording import RecordingSession

midi_dir = Path("exports")
for midi_file in midi_dir.glob("*.mid"):
    session = RecordingSession()
    # Load MIDI - extend RecordingSession with import_midi() method
    session.save_session(midi_file.with_suffix('.json'))
```

## Performance Recording & Analysis

### Track Statistics

```python
def get_session_statistics(session: RecordingSession):
    stats = session.get_stats()
    
    # Additional analysis
    total_velocity = sum(msg.get('velocity', 0) 
                        for track in session.tracks 
                        for msg in track.messages)
    
    avg_velocity = total_velocity / stats['total_notes'] if stats['total_notes'] > 0 else 0
    
    return {
        **stats,
        'average_velocity': round(avg_velocity, 1),
        'tracks': [
            {
                'name': t.name,
                'note_count': len(t.messages),
                'duration': t.get_duration()
            }
            for t in session.tracks
        ]
    }
```

## Custom UI Themes

Modify `config.py` COLORS dictionary:

```python
COLORS = {
    'background': (15, 15, 20),      # Darker
    'white_key': (250, 250, 250),    # Brighter
    'black_key': (35, 35, 40),       # Adjusted
    'active_white': (80, 200, 250),  # Cyan
    'active_black': (80, 200, 250),
    'accent': (255, 100, 100),       # Red accent
    'text': (220, 220, 225),
}
```

## Keyboard Range Limitations

Restrict playable range:

```python
class RangeFilter:
    def __init__(self, min_note: int = 48, max_note: int = 84):
        self.min_note = min_note
        self.max_note = max_note
    
    def filter_notes(self, notes: set) -> set:
        return {n for n in notes if self.min_note <= n <= self.max_note}
```

## Backup and Recovery

### Auto-save Mechanism

Modify `studio.py` to save every N messages:

```python
AUTOSAVE_INTERVAL = 50  # Save every 50 messages

def _on_midi_message(self, msg):
    # ... existing code ...
    
    if self.session.get_stats()['total_notes'] % AUTOSAVE_INTERVAL == 0:
        self.session.save_session(SESSIONS_DIR / f"{self.session.name}_backup.json")
```

## Troubleshooting Advanced Issues

### High CPU Usage
1. Reduce REFRESH_RATE in config.py (40-50 FPS)
2. Disable scale visualization temporarily
3. Limit number of active tracks

### MIDI Timing Issues
1. Check system clock sync
2. Increase buffer sizes slightly
3. Disable other MIDI apps
4. Check USB cable integrity

### Memory Leaks
1. Monitor with `memory_profiler`:
```bash
pip install memory_profiler
python -m memory_profiler studio.py
```

2. Check for circular references in sessions
3. Clear message buffers periodically

## Contributing & Customization

Fork the code and add features like:
- Arpeggiator
- Auto-accompaniment
- Microtonal support
- Real-time effects
- Network MIDI (RTP-MIDI)
- OSC support
- Chord progression templates

---

For questions or advanced customization, modify the modules and restart the application.
