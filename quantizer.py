# Professional MIDI Quantization Engine
from typing import List, Dict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantizeGrid(Enum):
    """Quantization grid options"""
    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25
    THIRTY_SECOND = 0.125
    TRIPLET_QUARTER = 2.0/3
    TRIPLET_EIGHTH = 1.0/3
    TRIPLET_SIXTEENTH = 1.0/6


class Quantizer:
    """Quantize MIDI timing to grid"""
    
    def __init__(self, grid: QuantizeGrid = QuantizeGrid.SIXTEENTH, bpm: int = 120):
        self.grid = grid
        self.bpm = bpm
        self.strength = 100  # 0-100, how much to quantize
        self.swing = 0  # -50 to 50, swing feel
    
    def set_grid(self, grid: QuantizeGrid):
        """Change quantization grid"""
        self.grid = grid
        logger.info(f"Quantize grid: {grid.name}")
    
    def set_strength(self, strength: int):
        """Set quantize strength (0=no quantize, 100=full quantize)"""
        self.strength = max(0, min(100, strength))
    
    def quantize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Quantize MIDI messages to grid"""
        if not messages or self.strength == 0:
            return messages
        
        quantized = []
        beat_duration = 60.0 / self.bpm  # Duration of one quarter note
        grid_duration = beat_duration * self.grid.value
        
        for msg in messages:
            original_time = msg.get('time', 0)
            
            # Calculate nearest grid position
            grid_position = round(original_time / grid_duration)
            quantized_time = grid_position * grid_duration
            
            # Apply swing
            if self.swing != 0 and grid_position % 2 == 1:
                swing_amount = (grid_duration / 2) * (self.swing / 100)
                quantized_time += swing_amount
            
            # Blend between original and quantized based on strength
            final_time = original_time + (quantized_time - original_time) * (self.strength / 100)
            
            quantized_msg = msg.copy()
            quantized_msg['time'] = final_time
            quantized.append(quantized_msg)
        
        logger.info(f"✓ Quantized {len(messages)} messages")
        return quantized
    
    def humanize(self, messages: List[Dict], amount: float = 0.05) -> List[Dict]:
        """Add subtle timing variations to make recordings more human"""
        import random
        
        humanized = []
        beat_duration = 60.0 / self.bpm
        max_deviation = beat_duration * amount
        
        for msg in messages:
            deviation = random.uniform(-max_deviation, max_deviation)
            humanized_msg = msg.copy()
            humanized_msg['time'] = msg['time'] + deviation
            humanized.append(humanized_msg)
        
        logger.info(f"✓ Humanized {len(messages)} messages")
        return humanized
    
    def time_stretch(self, messages: List[Dict], factor: float) -> List[Dict]:
        """Stretch or compress timing by factor (1.0 = no change)"""
        stretched = []
        
        if messages:
            base_time = messages[0]['time']
            
            for msg in messages:
                stretched_msg = msg.copy()
                relative_time = msg['time'] - base_time
                stretched_time = base_time + (relative_time * factor)
                stretched_msg['time'] = stretched_time
                stretched.append(stretched_msg)
        
        logger.info(f"✓ Time-stretched by {factor}x")
        return stretched
    
    def extract_notes_only(self, messages: List[Dict]) -> List[Dict]:
        """Remove non-note messages"""
        return [msg for msg in messages if msg['type'] in ['note_on', 'note_off']]
    
    def merge_notes(self, messages: List[Dict]) -> List[Dict]:
        """Merge overlapping note on/off pairs"""
        # Group by note
        note_groups = {}
        
        for msg in messages:
            note = msg.get('note')
            if note not in note_groups:
                note_groups[note] = []
            note_groups[note].append(msg)
        
        # Process each note
        merged = []
        for note, msgs in note_groups.items():
            note_on = None
            
            for msg in sorted(msgs, key=lambda x: x['time']):
                if msg['type'] == 'note_on':
                    note_on = msg
                elif msg['type'] == 'note_off' and note_on:
                    # Create note with duration
                    note_msg = note_on.copy()
                    note_msg['duration'] = msg['time'] - note_on['time']
                    merged.append(note_msg)
                    note_on = None
        
        return merged
