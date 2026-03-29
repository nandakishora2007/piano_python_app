# Professional Arpeggiator Engine
from enum import Enum
from typing import List, Set
import mido
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArpeggiatorMode(Enum):
    """Arpeggiator patterns"""
    UP = "up"
    DOWN = "down"
    UP_DOWN = "up_down"
    DOWN_UP = "down_up"
    RANDOM = "random"
    PING_PONG = "ping_pong"
    CHORD = "chord"
    CHORD_UP = "chord_up"


class ArpeggiatorSpeed(Enum):
    """Arpeggiator note durations"""
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25
    THIRTY_SECOND = 0.125


class Arpeggiator:
    """Advanced MIDI arpeggiator"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput, bpm: int = 120):
        self.midi_output = midi_output
        self.bpm = bpm
        self.mode = ArpeggiatorMode.UP
        self.speed = ArpeggiatorSpeed.SIXTEENTH
        self.octaves = 1  # Number of octaves to span
        self.enabled = False
        self.running = False
        self.thread = None
        self.active_notes: Set[int] = set()
        self.velocity = 100
        self.channel = 0
    
    def set_mode(self, mode: ArpeggiatorMode):
        """Set arpeggiator pattern"""
        self.mode = mode
        logger.info(f"Arpeggio mode: {mode.value}")
    
    def set_speed(self, speed: ArpeggiatorSpeed):
        """Set arpeggiator speed"""
        self.speed = speed
        logger.info(f"Arpeggio speed: {speed.name}")
    
    def set_octaves(self, octaves: int):
        """Set number of octaves to span"""
        self.octaves = max(1, min(4, octaves))
    
    def enable(self):
        """Enable arpeggiator"""
        self.enabled = True
        if not self.running:
            self.start()
    
    def disable(self):
        """Disable arpeggiator"""
        self.enabled = False
    
    def start(self):
        """Start arpeggiator"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._arpeggio_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop arpeggiator"""
        self.running = False
        self._all_notes_off()
        if self.thread:
            self.thread.join(timeout=1)
    
    def on_note_on(self, note: int, velocity: int = 100):
        """Handle note on"""
        self.active_notes.add(note)
        self.velocity = velocity
    
    def on_note_off(self, note: int):
        """Handle note off"""
        self.active_notes.discard(note)
    
    def _arpeggio_loop(self):
        """Main arpeggiator loop"""
        note_duration = (60.0 / self.bpm) * self.speed.value
        
        while self.running:
            if self.enabled and self.active_notes:
                # Get notes in order
                sorted_notes = sorted(self.active_notes)
                
                # Generate arpeggio pattern
                pattern = self._generate_pattern(sorted_notes)
                
                # Play pattern
                for note in pattern:
                    if not self.enabled or not self.active_notes:
                        break
                    
                    try:
                        # Note on
                        msg_on = mido.Message('note_on', note=note, velocity=self.velocity, channel=self.channel)
                        self.midi_output.send(msg_on)
                        
                        time.sleep(note_duration * 0.8)  # Leave small gap
                        
                        # Note off
                        msg_off = mido.Message('note_off', note=note, channel=self.channel)
                        self.midi_output.send(msg_off)
                        
                        time.sleep(note_duration * 0.2)
                    except Exception as e:
                        logger.error(f"Arpeggiator error: {e}")
            else:
                time.sleep(0.01)
    
    def _generate_pattern(self, base_notes: List[int]) -> List[int]:
        """Generate arpeggio pattern based on mode"""
        pattern = []
        
        if self.mode == ArpeggiatorMode.CHORD:
            # Play all notes at once
            pattern = base_notes * self.octaves
        
        elif self.mode == ArpeggiatorMode.UP:
            # Ascending pattern
            for octave in range(self.octaves):
                for note in base_notes:
                    pattern.append(note + octave * 12)
        
        elif self.mode == ArpeggiatorMode.DOWN:
            # Descending pattern
            for octave in range(self.octaves - 1, -1, -1):
                for note in reversed(base_notes):
                    pattern.append(note + octave * 12)
        
        elif self.mode == ArpeggiatorMode.UP_DOWN:
            # Up then down
            up_pattern = []
            for octave in range(self.octaves):
                for note in base_notes:
                    up_pattern.append(note + octave * 12)
            
            down_pattern = list(reversed(up_pattern))
            pattern = up_pattern + down_pattern[1:-1]  # Avoid duplicating endpoints
        
        elif self.mode == ArpeggiatorMode.DOWN_UP:
            # Down then up
            down_pattern = []
            for octave in range(self.octaves - 1, -1, -1):
                for note in reversed(base_notes):
                    down_pattern.append(note + octave * 12)
            
            up_pattern = list(reversed(down_pattern))
            pattern = down_pattern + up_pattern[1:-1]
        
        elif self.mode == ArpeggiatorMode.RANDOM:
            # Random order
            import random
            expanded = []
            for octave in range(self.octaves):
                for note in base_notes:
                    expanded.append(note + octave * 12)
            random.shuffle(expanded)
            pattern = expanded
        
        elif self.mode == ArpeggiatorMode.PING_PONG:
            # Alternating up and down
            for _ in range(self.octaves):
                for note in base_notes:
                    pattern.append(note)
                for note in reversed(base_notes):
                    pattern.append(note)
        
        return pattern
    
    def _all_notes_off(self):
        """Stop all playing notes"""
        for channel in range(16):
            msg = mido.Message('control_change', control=123, value=0, channel=channel)
            try:
                self.midi_output.send(msg)
            except:
                pass
