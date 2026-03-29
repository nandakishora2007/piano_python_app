# Professional Piano Visualization with Real-time Display
import pygame
import math
from config import (
    PIANO_KEYS, PIANO_START_NOTE, PIANO_END_NOTE, COLORS, NOTE_NAMES,
    NOTES_PER_OCTAVE
)


class PianoKeysRenderer:
    """Renders an 88-key piano keyboard visualization"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active_notes = set()
        
        # Calculate key dimensions
        white_keys_count = 52  # 88 keys have 52 white keys
        self.white_key_width = width / white_keys_count
        self.white_key_height = height
        self.black_key_width = self.white_key_width * 0.6
        self.black_key_height = height * 0.6
        
        # Note patterns for white and black keys
        self.white_key_notes = []
        self.black_key_notes = []
        self._build_key_map()
    
    def _build_key_map(self):
        """Build mapping of MIDI notes to key positions"""
        white_index = 0
        
        for note in range(PIANO_START_NOTE, PIANO_END_NOTE + 1):
            note_in_octave = note % NOTES_PER_OCTAVE
            
            # White keys: C, D, E, F, G, A, B
            if note_in_octave in [0, 2, 4, 5, 7, 9, 11]:
                self.white_key_notes.append((note, white_index))
                white_index += 1
            # Black keys: C#, D#, F#, G#, A#
            else:
                if note_in_octave in [1, 3, 6, 8, 10]:
                    self.black_key_notes.append((note, white_index - 1))
    
    def update_active_notes(self, notes: set):
        """Update which notes are currently active"""
        self.active_notes = notes
    
    def draw(self):
        """Draw the piano keyboard"""
        # Draw white keys
        for note, white_index in self.white_key_notes:
            x = self.x + white_index * self.white_key_width
            y = self.y
            
            is_active = note in self.active_notes
            color = COLORS['active_white'] if is_active else COLORS['white_key']
            border_color = COLORS['accent'] if is_active else (0, 0, 0)
            border_width = 3 if is_active else 1
            
            pygame.draw.rect(self.surface, color, 
                           (x, y, self.white_key_width, self.white_key_height))
            pygame.draw.rect(self.surface, border_color, 
                           (x, y, self.white_key_width, self.white_key_height), 
                           border_width)
        
        # Draw black keys
        for note, white_index in self.black_key_notes:
            x = self.x + (white_index + 1) * self.white_key_width - self.black_key_width / 2
            y = self.y
            
            is_active = note in self.active_notes
            color = COLORS['active_black'] if is_active else COLORS['black_key']
            border_color = COLORS['accent'] if is_active else (50, 50, 50)
            border_width = 3 if is_active else 1
            
            pygame.draw.rect(self.surface, color, 
                           (x, y, self.black_key_width, self.black_key_height))
            pygame.draw.rect(self.surface, border_color, 
                           (x, y, self.black_key_width, self.black_key_height), 
                           border_width)


class DisplayPanel:
    """UI panel for displaying information"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = {}
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)
    
    def update_data(self, data: dict):
        """Update display data"""
        self.data = data
    
    def draw(self):
        """Draw the panel"""
        # Draw background
        pygame.draw.rect(self.surface, COLORS['background'],
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.surface, COLORS['grid'],
                        (self.x, self.y, self.width, self.height), 2)
        
        # Draw data
        y_offset = self.y + 15
        for key, value in self.data.items():
            if isinstance(value, str):
                text = f"{key}: {value}"
                color = COLORS['text']
            else:
                text = f"{key}: {value}"
                color = COLORS['text']
            
            txt_surface = self.font_medium.render(text, True, color)
            self.surface.blit(txt_surface, (self.x + 15, y_offset))
            y_offset += 35


class VelocityMeter:
    """Displays MIDI velocity in real-time"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = 0
        self.font = pygame.font.Font(None, 24)
    
    def update_velocity(self, velocity: int):
        """Update velocity value"""
        self.velocity = min(127, max(0, velocity))
    
    def draw(self):
        """Draw velocity meter"""
        # Background
        pygame.draw.rect(self.surface, COLORS['black'],
                        (self.x, self.y, self.width, self.height))
        
        # Gradient bar
        bar_width = (self.velocity / 127) * self.width
        color_intensity = int((self.velocity / 127) * 255)
        color = (100, 200, color_intensity)
        
        pygame.draw.rect(self.surface, color,
                        (self.x, self.y, bar_width, self.height))
        
        # Border
        pygame.draw.rect(self.surface, COLORS['accent'],
                        (self.x, self.y, self.width, self.height), 2)
        
        # Text
        text = self.font.render(f"Velocity: {self.velocity}", True, COLORS['text'])
        self.surface.blit(text, (self.x + 10, self.y + 5))


class ScaleVisualization:
    """Shows notes in the current scale"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale_notes = set()
        self.font = pygame.font.Font(None, 20)
    
    def update_scale(self, scale_notes: set):
        """Update scale notes"""
        self.scale_notes = scale_notes
    
    def draw(self):
        """Draw scale visualization"""
        # Background
        pygame.draw.rect(self.surface, COLORS['background'],
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.surface, COLORS['grid'],
                        (self.x, self.y, self.width, self.height), 1)
        
        # Draw scale notes
        x_offset = self.x + 10
        y_offset = self.y + 10
        
        font_small = pygame.font.Font(None, 16)
        
        for i, note in enumerate(sorted(self.scale_notes)[:12]):
            note_in_octave = note % NOTES_PER_OCTAVE
            note_name = NOTE_NAMES[note_in_octave]
            
            txt = font_small.render(note_name, True, COLORS['accent'])
            self.surface.blit(txt, (x_offset, y_offset))
            x_offset += 30
            
            if (i + 1) % 4 == 0:
                y_offset += 25
                x_offset = self.x + 10
