# MIDI File Importer - Load songs and compositions
import mido
from pathlib import Path
from typing import Optional, List, Dict
from recording import RecordingSession, MIDITrack
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIDIImporter:
    """Import MIDI files as recording sessions"""
    
    def __init__(self):
        self.last_imported: Optional[RecordingSession] = None
    
    def import_midi_file(self, filepath: str) -> Optional[RecordingSession]:
        """
        Import MIDI file as recording session
        
        Args:
            filepath: Path to .mid file
            
        Returns:
            RecordingSession or None if import fails
        """
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                logger.error(f"File not found: {filepath}")
                return None
            
            # Load MIDI file
            mid = mido.MidiFile(filepath)
            
            # Create session
            session_name = file_path.stem
            session = RecordingSession(session_name, bpm=120)
            
            # Get tempo from MIDI
            for msg in mid.tracks[0]:
                if msg.type == 'set_tempo':
                    session.bpm = int(mido.tempo2bpm(msg.tempo))
                    break
            
            # Import tracks
            current_time = 0.0
            for track_idx, midi_track in enumerate(mid.tracks):
                track_name = f"Track {track_idx + 1}"
                
                # Try to get track name from MIDI
                for msg in midi_track:
                    if msg.type == 'track_name':
                        track_name = msg.name.strip()
                        break
                
                # Create session track
                session.add_track(track_name)
                session_track = session.tracks[track_idx]
                
                # Import messages
                current_time = 0.0
                for msg in midi_track:
                    current_time += msg.time
                    
                    if msg.type in ['note_on', 'note_off']:
                        # Convert to absolute time in seconds
                        time_seconds = current_time / mid.ticks_per_beat * (60.0 / session.bpm)
                        
                        session_track.add_message({
                            'type': msg.type,
                            'note': msg.note,
                            'velocity': msg.velocity,
                            'time': time_seconds,
                            'channel': msg.channel
                        })
            
            self.last_imported = session
            logger.info(f"✓ Imported MIDI: {session_name} ({len(session.tracks)} tracks)")
            return session
        
        except Exception as e:
            logger.error(f"✗ Failed to import MIDI: {e}")
            return None
    
    def import_from_directory(self, directory: str) -> List[RecordingSession]:
        """Import all MIDI files from directory"""
        sessions = []
        dir_path = Path(directory)
        
        for mid_file in dir_path.glob("*.mid"):
            session = self.import_midi_file(str(mid_file))
            if session:
                sessions.append(session)
        
        logger.info(f"✓ Imported {len(sessions)} MIDI files")
        return sessions
    
    def get_midi_info(self, filepath: str) -> Dict:
        """Get information about MIDI file"""
        try:
            mid = mido.MidiFile(filepath)
            
            # Calculate total time
            total_ticks = 0
            for track in mid.tracks:
                track_ticks = sum(msg.time for msg in track)
                total_ticks = max(total_ticks, track_ticks)
            
            # Calculate duration in seconds (assume 120 BPM if not specified)
            bpm = 120
            for msg in mid.tracks[0]:
                if msg.type == 'set_tempo':
                    bpm = int(mido.tempo2bpm(msg.tempo))
                    break
            
            duration_seconds = total_ticks / mid.ticks_per_beat * (60.0 / bpm)
            
            return {
                'filename': Path(filepath).name,
                'tracks': len(mid.tracks),
                'ticks_per_beat': mid.ticks_per_beat,
                'duration_seconds': round(duration_seconds, 2),
                'estimated_bpm': bpm
            }
        except Exception as e:
            logger.error(f"Cannot get MIDI info: {e}")
            return {}


class MIDIFileManager:
    """Manage MIDI file library"""
    
    def __init__(self, library_dir: str = "midi_library"):
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(exist_ok=True)
        self.library: List[Dict] = []
        self._scan_library()
    
    def _scan_library(self):
        """Scan directory for MIDI files"""
        self.library = []
        for mid_file in self.library_dir.glob("*.mid"):
            info = self._get_file_info(mid_file)
            self.library.append(info)
        
        logger.info(f"Library: {len(self.library)} MIDI files")
    
    def _get_file_info(self, filepath: Path) -> Dict:
        """Get file information"""
        try:
            mid = mido.MidiFile(str(filepath))
            
            # Count notes
            note_count = 0
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'note_on':
                        note_count += 1
            
            return {
                'filename': filepath.name,
                'path': str(filepath),
                'tracks': len(mid.tracks),
                'notes': note_count,
                'file_size_kb': filepath.stat().st_size / 1024
            }
        except:
            return {'filename': filepath.name, 'error': 'Cannot read file'}
    
    def add_to_library(self, filepath: str):
        """Add MIDI file to library"""
        src = Path(filepath)
        if src.exists():
            import shutil
            dest = self.library_dir / src.name
            shutil.copy2(src, dest)
            self._scan_library()
            logger.info(f"✓ Added to library: {src.name}")
    
    def get_library_list(self) -> List[str]:
        """Get list of files in library"""
        return [f['filename'] for f in self.library]
    
    def search_library(self, query: str) -> List[Dict]:
        """Search library for files matching query"""
        query_lower = query.lower()
        return [f for f in self.library if query_lower in f['filename'].lower()]
