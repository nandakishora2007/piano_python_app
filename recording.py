# Professional MIDI Recording and Playback Engine
import mido
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TimeSignature:
    """Time signature definition"""
    numerator: int = 4
    denominator: int = 4


class MIDITrack:
    """A single MIDI track with timing information"""
    
    def __init__(self, name: str = "Track 1", channel: int = 0):
        self.name = name
        self.channel = channel
        self.messages: List[Dict] = []
        self.is_recording = False
        self.record_start_time = None
    
    def add_message(self, msg_dict: Dict):
        """Add a MIDI message to track"""
        self.messages.append(msg_dict)
    
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.record_start_time = None
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
    
    def get_duration(self) -> float:
        """Get track duration in seconds"""
        if not self.messages:
            return 0.0
        return max(msg['time'] for msg in self.messages)


class RecordingSession:
    """Professional recording session with multiple tracks"""
    
    def __init__(self, name: str = "Untitled", bpm: int = 120):
        self.name = name
        self.bpm = bpm
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.tracks: List[MIDITrack] = []
        self.active_track_index = 0
        self.time_signature = TimeSignature()
        self.is_playing = False
        self.is_recording = False
        self.start_time = None
        self.metadata = {
            'composer': '',
            'style': '',
            'key': 'C Major',
            'notes': ''
        }
    
    def add_track(self, name: str = None) -> MIDITrack:
        """Add a new track to session"""
        if name is None:
            name = f"Track {len(self.tracks) + 1}"
        track = MIDITrack(name, channel=len(self.tracks) % 16)
        self.tracks.append(track)
        logger.info(f"Added track: {name}")
        return track
    
    def select_track(self, index: int) -> bool:
        """Select active track by index"""
        if 0 <= index < len(self.tracks):
            self.active_track_index = index
            return True
        return False
    
    def get_active_track(self) -> Optional[MIDITrack]:
        """Get currently active track"""
        if 0 <= self.active_track_index < len(self.tracks):
            return self.tracks[self.active_track_index]
        return None
    
    def start_recording(self):
        """Start recording to active track"""
        if track := self.get_active_track():
            track.start_recording()
            self.is_recording = True
            logger.info(f"Recording started on {track.name}")
    
    def stop_recording(self):
        """Stop recording"""
        if track := self.get_active_track():
            track.stop_recording()
            self.is_recording = False
            logger.info(f"Recording stopped. {len(track.messages)} messages recorded")
    
    def get_duration(self) -> float:
        """Get total session duration"""
        if not self.tracks:
            return 0.0
        return max(track.get_duration() for track in self.tracks)
    
    def export_to_file(self, filepath: str) -> bool:
        """Export session as MIDI file"""
        try:
            mid = mido.MidiFile(type=0)
            
            for track in self.tracks:
                m_track = mido.MidiTrack()
                
                if track.messages:
                    last_time = 0
                    for msg_dict in track.messages:
                        delta = msg_dict['time'] - last_time
                        
                        if msg_dict['type'] in ['note_on', 'note_off']:
                            m_msg = mido.Message(
                                msg_dict['type'],
                                note=msg_dict['note'],
                                velocity=msg_dict['velocity'],
                                time=int(delta * 1000),
                                channel=msg_dict['channel']
                            )
                        else:
                            continue
                        
                        m_track.append(m_msg)
                        last_time = msg_dict['time']
                
                mid.tracks.append(m_track)
            
            mid.save(filepath)
            logger.info(f"✓ Exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"✗ Export failed: {e}")
            return False
    
    def save_session(self, filepath: str) -> bool:
        """Save session to JSON"""
        try:
            session_data = {
                'name': self.name,
                'bpm': self.bpm,
                'time_signature': {
                    'numerator': self.time_signature.numerator,
                    'denominator': self.time_signature.denominator
                },
                'metadata': self.metadata,
                'tracks': [
                    {
                        'name': track.name,
                        'channel': track.channel,
                        'messages': track.messages
                    }
                    for track in self.tracks
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"✓ Session saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"✗ Save failed: {e}")
            return False
    
    def load_session(self, filepath: str) -> bool:
        """Load session from JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.name = data['name']
            self.bpm = data['bpm']
            self.time_signature.numerator = data['time_signature']['numerator']
            self.time_signature.denominator = data['time_signature']['denominator']
            self.metadata = data['metadata']
            
            self.tracks.clear()
            for track_data in data['tracks']:
                track = self.add_track(track_data['name'])
                track.channel = track_data['channel']
                track.messages = track_data['messages']
            
            logger.info(f"✓ Session loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"✗ Load failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        total_notes = sum(len(track.messages) for track in self.tracks)
        total_duration = self.get_duration()
        
        return {
            'session_name': self.name,
            'bpm': self.bpm,
            'tracks': len(self.tracks),
            'total_notes': total_notes,
            'duration_seconds': round(total_duration, 2),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
