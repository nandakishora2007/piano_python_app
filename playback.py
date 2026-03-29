# Professional MIDI Playback Engine with Real-time Control
import mido
import threading
import time
from typing import Optional, List, Callable
from recording import RecordingSession, MIDITrack
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaybackEngine:
    """Advanced MIDI playback with control and analysis"""
    
    def __init__(self, midi_output: mido.ports.BaseOutput):
        self.midi_output = midi_output
        self.current_session: Optional[RecordingSession] = None
        self.is_playing = False
        self.is_paused = False
        self.playback_thread = None
        self.playback_position = 0.0  # Current playback time in seconds
        self.playback_speed = 1.0  # 0.5x to 2.0x
        self.loop_enabled = False
        self.loop_start = 0.0
        self.loop_end = None
        self.callbacks: List[Callable] = []
        self.current_track_index = 0
        self.solo_track_index = None
        self.muted_tracks = set()
    
    def load_session(self, session: RecordingSession) -> bool:
        """Load a session for playback"""
        if not session.tracks:
            logger.error("Cannot play empty session")
            return False
        
        self.current_session = session
        self.playback_position = 0.0
        logger.info(f"✓ Loaded session: {session.name}")
        return True
    
    def play(self):
        """Start playback"""
        if not self.current_session or not self.current_session.tracks:
            logger.error("No session loaded")
            return
        
        if not self.is_playing:
            self.is_playing = True
            self.is_paused = False
            self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self.playback_thread.start()
            logger.info("▶ Playback started")
            self._fire_callback('play')
    
    def pause(self):
        """Pause playback"""
        if self.is_playing:
            self.is_paused = True
            logger.info("⏸ Playback paused")
            self._fire_callback('pause')
    
    def resume(self):
        """Resume from pause"""
        if self.is_paused:
            self.is_paused = False
            logger.info("▶ Playback resumed")
            self._fire_callback('resume')
    
    def stop(self):
        """Stop playback"""
        self.is_playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=1)
        self._all_notes_off()
        self.playback_position = 0.0
        logger.info("⏹ Playback stopped")
        self._fire_callback('stop')
    
    def seek(self, position: float):
        """Seek to position in seconds"""
        self.playback_position = max(0, position)
        logger.info(f"⏩ Seeked to {self.playback_position:.2f}s")
    
    def set_speed(self, speed: float):
        """Set playback speed (0.5x to 2.0x)"""
        self.playback_speed = max(0.5, min(2.0, speed))
        logger.info(f"Speed: {self.playback_speed}x")
    
    def set_loop(self, enabled: bool, start: float = 0.0, end: Optional[float] = None):
        """Enable/disable looping"""
        self.loop_enabled = enabled
        self.loop_start = start
        self.loop_end = end
        status = "enabled" if enabled else "disabled"
        logger.info(f"Loop {status}")
    
    def solo_track(self, track_index: int):
        """Solo a specific track"""
        if 0 <= track_index < len(self.current_session.tracks):
            self.solo_track_index = track_index
            logger.info(f"Solo: {self.current_session.tracks[track_index].name}")
    
    def mute_track(self, track_index: int, muted: bool = True):
        """Mute/unmute a track"""
        if 0 <= track_index < len(self.current_session.tracks):
            if muted:
                self.muted_tracks.add(track_index)
            else:
                self.muted_tracks.discard(track_index)
            
            track_name = self.current_session.tracks[track_index].name
            status = "muted" if muted else "unmuted"
            logger.info(f"{track_name} {status}")
    
    def _playback_loop(self):
        """Main playback loop"""
        loop_end = self.loop_end or self._get_session_duration()
        
        while self.is_playing:
            if not self.is_paused:
                # Send all notes that should be playing at this position
                self._play_messages_at_position(self.playback_position)
                
                # Update position
                self.playback_position += 0.01 / self.playback_speed  # 10ms steps
                
                # Handle looping
                if self.loop_enabled and self.playback_position >= loop_end:
                    self.playback_position = self.loop_start
                elif self.playback_position >= loop_end:
                    self.stop()
                    return
                
                self._fire_callback('position', self.playback_position)
            
            time.sleep(0.01)
    
    def _play_messages_at_position(self, position: float):
        """Play MIDI messages at current position"""
        time_window = 0.05  # 50ms window
        
        for track_idx, track in enumerate(self.current_session.tracks):
            # Check if track should be played
            if self.solo_track_index is not None and track_idx != self.solo_track_index:
                continue
            if track_idx in self.muted_tracks:
                continue
            
            for msg in track.messages:
                msg_time = msg.get('time', 0)
                
                # Check if this message should be played now
                if position <= msg_time < position + time_window:
                    try:
                        if msg['type'] in ['note_on', 'note_off']:
                            m = mido.Message(
                                msg['type'],
                                note=msg['note'],
                                velocity=msg['velocity'],
                                channel=msg.get('channel', 0)
                            )
                            self.midi_output.send(m)
                    except Exception as e:
                        logger.error(f"Playback error: {e}")
    
    def _get_session_duration(self) -> float:
        """Get total session duration"""
        if not self.current_session or not self.current_session.tracks:
            return 0.0
        return max(track.get_duration() for track in self.current_session.tracks)
    
    def _all_notes_off(self):
        """Send all notes off to stop hanging notes"""
        for channel in range(16):
            msg = mido.Message('control_change', control=123, value=0, channel=channel)
            try:
                self.midi_output.send(msg)
            except:
                pass
    
    def register_callback(self, callback: Callable):
        """Register playback callback"""
        self.callbacks.append(callback)
    
    def _fire_callback(self, event: str, data: any = None):
        """Fire registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def get_status(self) -> dict:
        """Get playback status"""
        return {
            'playing': self.is_playing,
            'paused': self.is_paused,
            'position': round(self.playback_position, 2),
            'duration': round(self._get_session_duration(), 2),
            'speed': self.playback_speed,
            'looping': self.loop_enabled,
            'session': self.current_session.name if self.current_session else None
        }
