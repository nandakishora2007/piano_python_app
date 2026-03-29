# Smart Chord & Progression Suggester with AI-like suggestions
from music_theory import MusicTheory, Scale, Chord
from typing import List, Tuple, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChordSuggester:
    """Suggests chord progressions based on analysis"""
    
    # Common jazz progressions
    JAZZ_PROGRESSIONS = [
        ['ii', 'V', 'I'],  # Classic ii-V-I
        ['I', 'vi', 'ii', 'V'],  # Jazz standard progression
        ['I', 'IV', 'V'],  # Blues-based
        ['vi', 'IV', 'I', 'V'],  # Sad/introspective
        ['I', 'III', 'VI', 'II'],  # Modal interchange
        ['ii', 'V', 'I', 'vi'],  # Extended jazz
    ]
    
    # Scale-appropriate chords
    SCALE_CHORDS = {
        'Major': ['I', 'IV', 'V', 'vi', 'ii', 'iii'],
        'Minor': ['i', 'iv', 'V', 'VI', 'ii°', 'III'],
        'Dorian': ['i', 'IV', 'V', 'vi'],
        'Blues': ['I', 'IV', 'I', 'V'],
        'Pentatonic': ['I', 'IV', 'V'],
    }
    
    def __init__(self, key: int = 60, scale_name: str = 'Major'):
        self.key = key
        self.scale_name = scale_name
        self.history: List[str] = []  # Chord progression history
        self.confidence = 0
    
    def set_key(self, key: int):
        """Set musical key"""
        key_name = MusicTheory.note_to_name(key)
        self.key = key
        logger.info(f"Key: {key_name}")
    
    def set_scale(self, scale_name: str):
        """Set scale mode"""
        self.scale_name = scale_name
        logger.info(f"Scale: {scale_name}")
    
    def suggest_progressions(self, count: int = 3) -> List[List[str]]:
        """Suggest chord progressions for current scale"""
        scale_info = self.SCALE_CHORDS.get(self.scale_name, self.SCALE_CHORDS['Major'])
        
        suggestions = []
        
        # Get common progressions for this scale
        for progression in self.JAZZ_PROGRESSIONS:
            # Filter to only use chords in the scale
            filtered = [chord for chord in progression if self._chord_in_scale(chord)]
            if len(filtered) >= 2:
                suggestions.append(filtered)
        
        # Add scale-based progression
        suggestions.append(scale_info[:4])
        
        return suggestions[:count]
    
    def suggest_next_chord(self, current_chord: str = None) -> Tuple[str, int]:
        """Suggest next chord in progression"""
        # Common resolutions
        resolutions = {
            'I': ['IV', 'V', 'vi'],
            'ii': ['V', 'IV'],
            'IV': ['I', 'V', 'vi'],
            'V': ['I', 'vi'],
            'vi': ['ii', 'IV', 'V'],
            'iii': ['vi', 'IV'],
        }
        
        if current_chord in resolutions:
            next_chords = resolutions[current_chord]
            confidence = 80
        else:
            # Default suggestion
            next_chords = ['I', 'IV', 'V']
            confidence = 40
        
        # Prefer chord not recently used
        preferred = next(chord for chord in next_chords if chord not in self.history[-2:])
        
        return preferred, confidence
    
    def add_to_history(self, chord: str):
        """Add chord to progression history"""
        self.history.append(chord)
    
    def get_progression_analysis(self) -> dict:
        """Analyze current progression"""
        if not self.history:
            return {'progression': [], 'commonality': 0, 'style': 'Unknown'}
        
        progression = '-'.join(self.history[-4:])  # Last 4 chords
        commonality = self._calculate_commonality(self.history)
        style = self._detect_style(self.history)
        
        return {
            'progression': progression,
            'commonality': commonality,
            'style': style,
            'length': len(self.history)
        }
    
    def _chord_in_scale(self, chord: str) -> bool:
        """Check if chord naturally occurs in scale"""
        scale_chords = self.SCALE_CHORDS.get(self.scale_name, [])
        return any(chord in scale_chord for scale_chord in scale_chords)
    
    def _calculate_commonality(self, chord_history: List[str]) -> int:
        """Calculate how common the progression is (0-100)"""
        if len(chord_history) < 2:
            return 50
        
        # Check against known progressions
        recent = chord_history[-3:]
        matches = 0
        
        for progression in self.JAZZ_PROGRESSIONS:
            for i in range(len(progression) - len(recent) + 1):
                if progression[i:i+len(recent)] == recent:
                    matches += 1
        
        return min(100, 40 + matches * 20)
    
    def _detect_style(self, chord_history: List[str]) -> str:
        """Detect music style from progressions"""
        if not chord_history:
            return 'Unknown'
        
        # Simple heuristic
        if 'ii' in chord_history and 'V' in chord_history:
            return 'Jazz'
        elif 'I' in chord_history and 'IV' in chord_history and 'V' in chord_history:
            return 'Blues'
        elif 'vi' in chord_history and 'IV' in chord_history:
            return 'Pop'
        else:
            return 'Contemporary'


class ProgressionBuilder:
    """Build chord progressions interactively"""
    
    def __init__(self, root_key: int = 60):
        self.root_key = root_key
        self.progression: List[Tuple[str, int]] = []  # (chord_name, duration_beats)
    
    def add_chord(self, chord_name: str, duration_beats: int = 4):
        """Add chord to progression"""
        self.progression.append((chord_name, duration_beats))
    
    def remove_last_chord(self):
        """Remove last chord"""
        if self.progression:
            self.progression.pop()
    
    def to_midi_notes(self) -> List[List[int]]:
        """Convert progression to MIDI note groups"""
        notes = []
        
        for chord_name, _ in self.progression:
            chord_notes = self._get_chord_notes(chord_name)
            notes.append(chord_notes)
        
        return notes
    
    def _get_chord_notes(self, chord_name: str) -> List[int]:
        """Get MIDI notes for chord"""
        # This is simplified - in real app would use more sophisticated mapping
        root_offset = ord(chord_name[0].upper()) - ord('C')
        root_note = self.root_key + root_offset * 2  # Simplified semitone conversion
        
        # Get chord intervals
        for name, intervals in Chord.ALL.items():
            if name.lower() in chord_name.lower():
                return [root_note + interval for interval in intervals]
        
        # Default to major triad
        return [root_note, root_note + 4, root_note + 7]
    
    def get_progression_string(self) -> str:
        """Get progression as string"""
        return ' - '.join(chord for chord, _ in self.progression)
