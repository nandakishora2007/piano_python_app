# Music Theory utilities for professional analysis
from typing import List, Set, Tuple
from enum import Enum
from config import NOTES_PER_OCTAVE, NOTE_NAMES


class Scale:
    """Music scale definitions"""
    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    MINOR = [0, 2, 3, 5, 7, 8, 10]
    HARMONIC_MINOR = [0, 2, 3, 5, 7, 8, 11]
    MELODIC_MINOR = [0, 2, 3, 5, 7, 9, 11]
    DORIAN = [0, 2, 3, 5, 7, 9, 10]
    PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
    LYDIAN = [0, 2, 4, 6, 7, 9, 11]
    MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
    BLUES = [0, 3, 5, 6, 7, 10]
    PENTATONIC = [0, 2, 4, 7, 9]
    WHOLE_TONE = [0, 2, 4, 6, 8, 10]
    
    ALL = {
        'Major': MAJOR,
        'Minor': MINOR,
        'Harmonic Minor': HARMONIC_MINOR,
        'Melodic Minor': MELODIC_MINOR,
        'Dorian': DORIAN,
        'Phrygian': PHRYGIAN,
        'Lydian': LYDIAN,
        'Mixolydian': MIXOLYDIAN,
        'Blues': BLUES,
        'Pentatonic': PENTATONIC,
        'Whole Tone': WHOLE_TONE,
    }


class Chord:
    """Chord definitions (intervals from root)"""
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    DIMINISHED = [0, 3, 6]
    AUGMENTED = [0, 4, 8]
    MAJOR_7 = [0, 4, 7, 11]
    MINOR_7 = [0, 3, 7, 10]
    DOMINANT_7 = [0, 4, 7, 10]
    MAJOR_9 = [0, 4, 7, 11, 14]
    MINOR_9 = [0, 3, 7, 10, 14]
    SUSPENDED_2 = [0, 2, 7]
    SUSPENDED_4 = [0, 5, 7]
    
    ALL = {
        'Major': MAJOR,
        'Minor': MINOR,
        'Diminished': DIMINISHED,
        'Augmented': AUGMENTED,
        'Major 7': MAJOR_7,
        'Minor 7': MINOR_7,
        'Dominant 7': DOMINANT_7,
        'Major 9': MAJOR_9,
        'Minor 9': MINOR_9,
        'Sus2': SUSPENDED_2,
        'Sus4': SUSPENDED_4,
    }


class MusicTheory:
    """Music theory analysis tools"""
    
    @staticmethod
    def note_to_name(note: int) -> str:
        """Convert MIDI note number to note name"""
        note_in_octave = note % NOTES_PER_OCTAVE
        octave = note // NOTES_PER_OCTAVE - 1
        return f"{NOTE_NAMES[note_in_octave]}{octave}"
    
    @staticmethod
    def note_to_letter(note: int) -> str:
        """Get just the letter name of a note"""
        note_in_octave = note % NOTES_PER_OCTAVE
        return NOTE_NAMES[note_in_octave]
    
    @staticmethod
    def get_scale_notes(root_note: int, scale_intervals: List[int]) -> Set[int]:
        """Get all notes in a scale starting from root (within 88 keys)"""
        from config import PIANO_START_NOTE, PIANO_END_NOTE
        scale_notes = set()
        
        note = root_note % NOTES_PER_OCTAVE
        for octave_offset in range(8):  # Cover multiple octaves
            for interval in scale_intervals:
                current_note = note + interval + (octave_offset * NOTES_PER_OCTAVE)
                if PIANO_START_NOTE <= current_note <= PIANO_END_NOTE:
                    scale_notes.add(current_note)
        
        return scale_notes
    
    @staticmethod
    def detect_chord(notes: Set[int]) -> Tuple[str, str, int]:
        """
        Detect chord from a set of notes
        Returns: (root_note_name, chord_type, confidence_0_to_100)
        """
        if len(notes) < 2:
            return "Unknown", "No chord", 0
        
        sorted_notes = sorted(notes)
        bass_note = sorted_notes[0]
        root_offset = (bass_note % NOTES_PER_OCTAVE)
        
        # Normalize intervals relative to bass note
        intervals = [(n % NOTES_PER_OCTAVE - root_offset) % NOTES_PER_OCTAVE 
                     for n in sorted_notes]
        intervals = sorted(set(intervals))
        
        # Try to match against known chords
        best_match = "Unknown"
        best_confidence = 0
        
        for chord_name, chord_intervals in Chord.ALL.items():
            matching = len(set(chord_intervals) & set(intervals))
            total = len(set(chord_intervals) | set(intervals))
            confidence = (matching / total) * 100 if total > 0 else 0
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = chord_name
        
        root_note_name = MusicTheory.note_to_name(bass_note)
        
        return root_note_name, best_match, int(best_confidence)
    
    @staticmethod
    def detect_scale(notes: Set[int]) -> Tuple[str, int]:
        """
        Detect the likely scale from played notes
        Returns: (scale_name, confidence_0_to_100)
        """
        if len(notes) < 3:
            return "Unknown", 0
        
        root_note = min(notes)
        root_offset = root_note % NOTES_PER_OCTAVE
        
        # Normalize intervals
        intervals = [(n % NOTES_PER_OCTAVE - root_offset) % NOTES_PER_OCTAVE 
                     for n in notes]
        intervals = sorted(set(intervals))
        
        best_match = "Unknown"
        best_confidence = 0
        
        for scale_name, scale_intervals in Scale.ALL.items():
            matching = len(set(scale_intervals) & set(intervals))
            total = len(scale_intervals)
            confidence = (matching / total) * 100 if total > 0 else 0
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = scale_name
        
        return best_match, int(best_confidence)
    
    @staticmethod
    def get_interval_semitones(note1: int, note2: int) -> int:
        """Get interval between two notes in semitones"""
        return abs(note2 - note1)
    
    @staticmethod
    def transpose(notes: List[int], semitones: int) -> List[int]:
        """Transpose notes by given semitones"""
        return [n + semitones for n in notes]
    
    @staticmethod
    def get_relative_minor(major_root: int) -> int:
        """Get relative minor for a major key"""
        return major_root + 9  # 9 semitones down = 3 semitones up
    
    @staticmethod
    def get_relative_major(minor_root: int) -> int:
        """Get relative major for a minor key"""
        return minor_root + 3  # 3 semitones up = 9 semitones down
