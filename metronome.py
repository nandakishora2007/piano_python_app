# Professional Metronome with Click Track
import mido
import threading
import time
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NoteValue(Enum):
    """Note values for metronome"""
    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25


class Metronome:
    """Professional metronome with audio click track"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput, bpm: int = 120):
        self.midi_output = midi_output
        self.bpm = bpm
        self.is_running = False
        self.thread = None
        self.click_note = 76  # A5 - high click
        self.accent_note = 60  # C4 - bass click for downbeat
        self.click_velocity = 100
        self.accent_velocity = 120
        self.enabled = True
        self.accent_enabled = True
        self.time_signature_num = 4
        self.time_signature_den = 4
        self.beat_counter = 0
    
    def set_bpm(self, bpm: int):
        """Change BPM"""
        self.bpm = max(20, min(300, bpm))
        logger.info(f"Metronome BPM: {self.bpm}")
    
    def set_time_signature(self, numerator: int, denominator: int):
        """Set time signature"""
        self.time_signature_num = numerator
        self.time_signature_den = denominator
        self.beat_counter = 0
    
    def start(self):
        """Start metronome"""
        if not self.is_running:
            self.is_running = True
            self.beat_counter = 0
            self.thread = threading.Thread(target=self._metronome_loop, daemon=True)
            self.thread.start()
            logger.info("✓ Metronome started")
    
    def stop(self):
        """Stop metronome"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("⏹ Metronome stopped")
    
    def toggle(self):
        """Toggle metronome on/off"""
        if self.is_running:
            self.stop()
        else:
            self.start()
    
    def _metronome_loop(self):
        """Main metronome loop"""
        beat_duration = 60.0 / self.bpm  # Duration of one quarter note
        
        while self.is_running:
            if self.enabled:
                # Determine if this is a downbeat
                is_downbeat = (self.beat_counter % self.time_signature_num) == 0
                
                # Send appropriate click
                if is_downbeat and self.accent_enabled:
                    self._send_click(self.accent_note, self.accent_velocity)
                else:
                    self._send_click(self.click_note, self.click_velocity)
                
                self.beat_counter += 1
            
            time.sleep(beat_duration)
    
    def _send_click(self, note: int, velocity: int):
        """Send a click via MIDI"""
        try:
            # Note on
            msg_on = mido.Message('note_on', note=note, velocity=velocity)
            self.midi_output.send(msg_on)
            time.sleep(0.05)  # Click duration
            
            # Note off
            msg_off = mido.Message('note_off', note=note)
            self.midi_output.send(msg_off)
        except Exception as e:
            logger.error(f"Metronome click error: {e}")
    
    def get_info(self) -> dict:
        """Get metronome info"""
        return {
            'bpm': self.bpm,
            'enabled': self.enabled,
            'running': self.is_running,
            'time_signature': f"{self.time_signature_num}/{self.time_signature_den}",
            'beat': self.beat_counter % self.time_signature_num
        }


class TempoMap:
    """Handle tempo changes and acceleration"""
    
    def __init__(self, initial_bpm: int = 120):
        self.initial_bpm = initial_bpm
        self.tempo_changes = []  # List of (beat, bpm) tuples
    
    def add_tempo_change(self, beat: int, bpm: int):
        """Add tempo change at specific beat"""
        self.tempo_changes.append((beat, bpm))
        self.tempo_changes.sort(key=lambda x: x[0])
    
    def get_bpm_at_beat(self, beat: int) -> int:
        """Get BPM at specific beat"""
        current_bpm = self.initial_bpm
        for change_beat, change_bpm in self.tempo_changes:
            if beat >= change_beat:
                current_bpm = change_bpm
        return current_bpm
    
    def accelerando(self, start_beat: int, end_beat: int, start_bpm: int, end_bpm: int):
        """Create gradual tempo increase"""
        num_changes = max(2, (end_beat - start_beat) // 4)
        for i in range(num_changes + 1):
            beat = start_beat + (end_beat - start_beat) * i // num_changes
            bpm = int(start_bpm + (end_bpm - start_bpm) * i / num_changes)
            self.add_tempo_change(beat, bpm)
    
    def ritardando(self, start_beat: int, end_beat: int, start_bpm: int, end_bpm: int):
        """Create gradual tempo decrease"""
        self.accelerando(start_beat, end_beat, start_bpm, end_bpm)
