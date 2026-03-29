# Waveform Visualization for Recordings
import pygame
from typing import List, Dict, Optional
from config import COLORS
import math


class WaveformRenderer:
    """Display audio waveform visualization"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.messages: List[Dict] = []
        self.zoom_level = 1.0
        self.offset = 0.0  # Horizontal scroll
        self.font = pygame.font.Font(None, 16)
    
    def update_messages(self, messages: List[Dict]):
        """Update with MIDI messages"""
        self.messages = messages
    
    def set_zoom(self, zoom: float):
        """Set zoom level (0.5x to 4.0x)"""
        self.zoom_level = max(0.5, min(4.0, zoom))
    
    def scroll(self, amount: float):
        """Horizontal scroll"""
        self.offset = max(0, self.offset + amount)
    
    def draw(self):
        """Draw waveform"""
        # Background
        pygame.draw.rect(self.surface, COLORS['background'],
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.surface, COLORS['grid'],
                        (self.x, self.y, self.width, self.height), 1)
        
        if not self.messages:
            # Draw placeholder
            text = self.font.render("No recording data", True, COLORS['text'])
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            self.surface.blit(text, text_rect)
            return
        
        # Get max time
        max_time = max(msg.get('time', 0) for msg in self.messages) if self.messages else 1.0
        
        # Draw notes as blocks
        for msg in self.messages:
            if msg['type'] == 'note_on':
                # Find corresponding note off
                note_off_msg = None
                for other_msg in self.messages:
                    if (other_msg['type'] == 'note_off' and 
                        other_msg['note'] == msg['note'] and
                        other_msg['time'] > msg['time']):
                        note_off_msg = other_msg
                        break
                
                if note_off_msg:
                    # Calculate pixel position
                    start_x = self.x + int((msg['time'] - self.offset) / max_time * self.width * self.zoom_level)
                    end_x = self.x + int((note_off_msg['time'] - self.offset) / max_time * self.width * self.zoom_level)
                    
                    # Skip if off-screen
                    if end_x < self.x or start_x > self.x + self.width:
                        continue
                    
                    # Calculate note height (pitch)
                    note_height = int((msg['note'] / 127) * self.height)
                    y_pos = self.y + self.height - note_height
                    block_height = max(2, int(self.height / 88))
                    
                    # Determine color based on velocity
                    velocity = msg.get('velocity', 64)
                    color_intensity = int((velocity / 127) * 255)
                    color = (100, color_intensity, 200)
                    
                    # Draw note block
                    width = max(1, end_x - start_x)
                    pygame.draw.rect(self.surface, color,
                                   (start_x, y_pos, width, block_height))
                    pygame.draw.rect(self.surface, COLORS['accent'],
                                   (start_x, y_pos, width, block_height), 1)
        
        # Draw timeline
        self._draw_timeline(max_time)
    
    def _draw_timeline(self, max_time: float):
        """Draw time ruler"""
        # Draw tick marks and times
        num_ticks = max(5, int(self.width / 60))
        tick_interval = max_time / num_ticks
        
        for i in range(num_ticks + 1):
            time_val = i * tick_interval
            x_pos = self.x + (time_val - self.offset) / max_time * self.width * self.zoom_level
            
            if self.x <= x_pos <= self.x + self.width:
                # Draw tick
                pygame.draw.line(self.surface, COLORS['grid'],
                               (x_pos, self.y + self.height - 10),
                               (x_pos, self.y + self.height), 1)
                
                # Draw time label
                time_text = f"{time_val:.1f}s"
                text = self.font.render(time_text, True, COLORS['text'])
                self.surface.blit(text, (x_pos - 15, self.y + self.height - 20))


class NoteRollEditor:
    """Piano roll-style editor visualization"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.messages: List[Dict] = []
        self.selected_note = None
        self.font = pygame.font.Font(None, 14)
    
    def update_messages(self, messages: List[Dict]):
        """Update with MIDI messages"""
        self.messages = messages
    
    def draw(self):
        """Draw piano roll"""
        # Background
        pygame.draw.rect(self.surface, COLORS['background'],
                        (self.x, self.y, self.width, self.height))
        
        # Draw staff lines (keyboard keys)
        key_height = self.height / 88
        
        for i in range(88):
            y_pos = self.y + i * key_height
            
            # Alternate colors for white and black keys
            note = 21 + i  # MIDI note 21-108
            note_in_octave = note % 12
            
            if note_in_octave in [1, 3, 6, 8, 10]:  # Black keys
                pygame.draw.line(self.surface, COLORS['grid'],
                               (self.x, y_pos), (self.x + self.width, y_pos), 1)
        
        # Draw notes
        if self.messages:
            max_time = max(msg.get('time', 0) for msg in self.messages)
            
            for msg in self.messages:
                if msg['type'] == 'note_on':
                    note = msg['note']
                    if 21 <= note <= 108:  # Valid piano range
                        key_pos = note - 21
                        y_pos = self.y + key_pos * key_height
                        x_pos = self.x + (msg['time'] / max_time) * self.width if max_time > 0 else self.x
                        
                        # Draw note as circle
                        pygame.draw.circle(self.surface, COLORS['accent'],
                                         (int(x_pos), int(y_pos + key_height // 2)), 4)
        
        # Border
        pygame.draw.rect(self.surface, COLORS['grid'],
                        (self.x, self.y, self.width, self.height), 2)


class PerformanceAnalyzer:
    """Visualize performance metrics"""
    
    def __init__(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_data: List[int] = []
        self.timing_data: List[float] = []
        self.font = pygame.font.Font(None, 18)
    
    def update_data(self, messages: List[Dict]):
        """Update with performance data"""
        velocities = [msg.get('velocity', 64) for msg in messages if msg['type'] == 'note_on']
        self.velocity_data = velocities
        
        # Calculate timing deviations
        timings = [msg.get('time', 0) for msg in messages]
        if len(timings) > 1:
            self.timing_data = [timings[i+1] - timings[i] for i in range(len(timings)-1)]
    
    def draw(self):
        """Draw performance analysis"""
        # Background
        pygame.draw.rect(self.surface, COLORS['background'],
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.surface, COLORS['grid'],
                        (self.x, self.y, self.width, self.height), 1)
        
        # Draw velocity histogram
        if self.velocity_data:
            avg_velocity = sum(self.velocity_data) / len(self.velocity_data)
            max_velocity = max(self.velocity_data)
            min_velocity = min(self.velocity_data)
            
            # Display stats
            y_offset = self.y + 15
            stats = [
                f"Notes: {len(self.velocity_data)}",
                f"Avg Vel: {int(avg_velocity)}",
                f"Max Vel: {max_velocity}",
                f"Min Vel: {min_velocity}"
            ]
            
            for stat in stats:
                text = self.font.render(stat, True, COLORS['text'])
                self.surface.blit(text, (self.x + 15, y_offset))
                y_offset += 25
            
            # Draw velocity bar graph
            bar_width = (self.width - 30) / len(self.velocity_data[:10])
            for i, vel in enumerate(self.velocity_data[:10]):
                bar_height = int((vel / 127) * 50)
                x_pos = self.x + 15 + i * bar_width
                y_pos = self.y + 120 - bar_height
                pygame.draw.rect(self.surface, COLORS['accent'],
                               (x_pos, y_pos, bar_width - 2, bar_height))
