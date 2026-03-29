# Professional MIDI Effects Processing
import mido
import threading
import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReverbEffect:
    """MIDI Reverb via CC automation"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.midi_output = midi_output
        self.level = 0  # 0-127
        self.decay_time = 1.5  # seconds
        self.enabled = True
    
    def set_level(self, level: int):
        """Set reverb level (0-127)"""
        self.level = max(0, min(127, level))
        self._send_cc(91, self.level)
        logger.info(f"Reverb: {self.level}")
    
    def _send_cc(self, control: int, value: int):
        """Send control change"""
        try:
            for channel in range(16):
                msg = mido.Message('control_change', control=control, value=value, channel=channel)
                self.midi_output.send(msg)
        except Exception as e:
            logger.error(f"Reverb CC error: {e}")


class DelayEffect:
    """MIDI Delay effect"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.midi_output = midi_output
        self.level = 0  # 0-127
        self.time_ms = 500  # Delay time in milliseconds
        self.feedback = 50  # Feedback amount (0-100)
        self.enabled = False
        self.delay_notes: List[Dict] = []
        self.thread = None
        self.running = False
    
    def set_level(self, level: int):
        """Set delay level"""
        self.level = max(0, min(127, level))
        logger.info(f"Delay Level: {self.level}")
    
    def set_time(self, time_ms: int):
        """Set delay time in milliseconds"""
        self.time_ms = max(50, min(2000, time_ms))
        logger.info(f"Delay Time: {self.time_ms}ms")
    
    def set_feedback(self, feedback: int):
        """Set feedback amount (0-100)"""
        self.feedback = max(0, min(100, feedback))
    
    def enable(self):
        """Enable delay"""
        if not self.enabled:
            self.enabled = True
            self.running = True
            self.thread = threading.Thread(target=self._delay_loop, daemon=True)
            self.thread.start()
    
    def disable(self):
        """Disable delay"""
        self.enabled = False
        self.running = False
    
    def process_note(self, note: int, velocity: int, duration: float):
        """Process note through delay"""
        if self.enabled and self.level > 0:
            self.delay_notes.append({
                'note': note,
                'velocity': int(velocity * self.feedback / 100),
                'time': time.time(),
                'duration': duration
            })
    
    def _delay_loop(self):
        """Process delayed notes"""
        while self.running:
            current_time = time.time()
            delay_time = self.time_ms / 1000.0
            
            for delay_note in self.delay_notes[:]:
                if current_time - delay_note['time'] >= delay_time:
                    # Play delayed note
                    if delay_note['velocity'] > 1:
                        try:
                            msg_on = mido.Message('note_on', note=delay_note['note'], velocity=delay_note['velocity'])
                            self.midi_output.send(msg_on)
                            
                            time.sleep(0.1)
                            
                            msg_off = mido.Message('note_off', note=delay_note['note'])
                            self.midi_output.send(msg_off)
                        except:
                            pass
                    
                    self.delay_notes.remove(delay_note)
            
            time.sleep(0.01)


class ChorusEffect:
    """MIDI Chorus effect via CC"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.midi_output = midi_output
        self.level = 0  # 0-127
        self.speed = 1.0  # Hz
        self.depth = 50  # 0-100
        self.enabled = True
    
    def set_level(self, level: int):
        """Set chorus level"""
        self.level = max(0, min(127, level))
        self._send_cc(93, self.level)
        logger.info(f"Chorus: {self.level}")
    
    def set_speed(self, speed: float):
        """Set chorus speed in Hz"""
        self.speed = max(0.1, min(10.0, speed))
    
    def _send_cc(self, control: int, value: int):
        """Send control change"""
        try:
            for channel in range(16):
                msg = mido.Message('control_change', control=control, value=value, channel=channel)
                self.midi_output.send(msg)
        except Exception as e:
            logger.error(f"Chorus CC error: {e}")


class CompressorEffect:
    """MIDI dynamic compression"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.midi_output = midi_output
        self.threshold = 100  # Threshold velocity (0-127)
        self.ratio = 4  # Compression ratio
        self.attack_ms = 10
        self.release_ms = 100
    
    def process_velocity(self, velocity: int) -> int:
        """Process velocity through compressor"""
        if velocity > self.threshold:
            excess = velocity - self.threshold
            compressed = excess / self.ratio
            return int(self.threshold + compressed)
        return velocity


class EffectsChain:
    """Chain multiple effects together"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.reverb = ReverbEffect(midi_output)
        self.delay = DelayEffect(midi_output)
        self.chorus = ChorusEffect(midi_output)
        self.compressor = CompressorEffect(midi_output)
        self.enabled_effects = []
    
    def enable_reverb(self, level: int = 50):
        """Enable reverb in chain"""
        self.reverb.set_level(level)
        self.enabled_effects.append('reverb')
    
    def enable_delay(self, level: int = 30, time_ms: int = 500):
        """Enable delay in chain"""
        self.delay.set_level(level)
        self.delay.set_time(time_ms)
        self.delay.enable()
        self.enabled_effects.append('delay')
    
    def enable_chorus(self, level: int = 40):
        """Enable chorus in chain"""
        self.chorus.set_level(level)
        self.enabled_effects.append('chorus')
    
    def disable_all(self):
        """Disable all effects"""
        self.delay.disable()
        self.reverb.set_level(0)
        self.chorus.set_level(0)
        self.enabled_effects = []
    
    def get_status(self) -> dict:
        """Get effects status"""
        return {
            'enabled_effects': self.enabled_effects,
            'reverb_level': self.reverb.level,
            'delay_level': self.delay.level,
            'delay_time_ms': self.delay.time_ms,
            'chorus_level': self.chorus.level
        }
