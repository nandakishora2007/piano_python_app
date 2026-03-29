# MIDI Monitor - Real-time MIDI data inspection and analysis
import mido
import time
import logging
from collections import defaultdict
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIDIMonitor:
    """Monitor and analyze MIDI stream in real-time"""
    
    def __init__(self, input_port_name: str = 'Digital Keyboard 0'):
        self.input_port_name = input_port_name
        self.inport = None
        self.messages = []
        self.message_count = defaultdict(int)
        self.note_histogram = defaultdict(int)
        self.velocity_histogram = defaultdict(int)
        self.running = False
        
        self.connect()
    
    def connect(self) -> bool:
        """Connect to input port"""
        try:
            self.inport = mido.open_input(self.input_port_name)
            logger.info(f"✓ Connected to {self.input_port_name}")
            return True
        except Exception as e:
            logger.error(f"✗ Cannot connect: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring MIDI messages"""
        if not self.inport:
            logger.error("Not connected")
            return
        
        logger.info("Monitoring MIDI (Ctrl+C to stop)...")
        logger.info("-" * 80)
        logger.info(f"{'Time':>10} | {'Type':<15} | {'Note':<8} | {'Velocity':<10} | {'Channel':<8}")
        logger.info("-" * 80)
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                for msg in self.inport.iter_pending():
                    elapsed = time.time() - start_time
                    self._process_message(msg, elapsed)
                time.sleep(0.001)
        
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped")
        
        finally:
            self._print_statistics()
            self.disconnect()
    
    def _process_message(self, msg: mido.Message, elapsed: float):
        """Process and display a MIDI message"""
        self.messages.append((msg, elapsed))
        self.message_count[msg.type] += 1
        
        # Format output
        msg_type = msg.type
        note_str = f"{msg.note}" if hasattr(msg, 'note') else "-"
        velocity_str = f"{msg.velocity}" if hasattr(msg, 'velocity') else "-"
        channel_str = f"{msg.channel}" if hasattr(msg, 'channel') else "-"
        
        # Track histograms
        if msg.type in ['note_on', 'note_off']:
            self.note_histogram[msg.note] += 1
            if hasattr(msg, 'velocity'):
                self.velocity_histogram[msg.velocity] += 1
        
        # Print message
        logger.info(f"{elapsed:>10.3f} | {msg_type:<15} | {note_str:<8} | {velocity_str:<10} | {channel_str:<8}")
    
    def _print_statistics(self):
        """Print collected statistics"""
        logger.info("\n" + "=" * 80)
        logger.info("STATISTICS")
        logger.info("=" * 80)
        
        logger.info("\nMessage Count by Type:")
        for msg_type, count in sorted(self.message_count.items()):
            logger.info(f"  {msg_type}: {count}")
        
        if self.note_histogram:
            logger.info("\nMost Pressed Notes:")
            sorted_notes = sorted(self.note_histogram.items(), key=lambda x: x[1], reverse=True)
            for note, count in sorted_notes[:10]:
                from music_theory import MusicTheory
                note_name = MusicTheory.note_to_name(note)
                logger.info(f"  {note_name} (MIDI {note}): {count} times")
        
        if self.velocity_histogram:
            logger.info("\nVelocity Distribution:")
            for velocity in sorted(self.velocity_histogram.keys()):
                count = self.velocity_histogram[velocity]
                bar = "█" * (count // 2)
                logger.info(f"  {velocity:>3}: {bar}")
        
        logger.info("\nTotal Messages: {}".format(len(self.messages)))
        logger.info("=" * 80)
    
    def disconnect(self):
        """Disconnect from port"""
        if self.inport:
            self.inport.close()
            logger.info("Disconnected")


class MIDIFilter:
    """Filter MIDI messages based on criteria"""
    
    def __init__(self, min_note: int = None, max_note: int = None, 
                 min_velocity: int = None, max_velocity: int = None):
        self.min_note = min_note
        self.max_note = max_note
        self.min_velocity = min_velocity
        self.max_velocity = max_velocity
    
    def passes(self, msg: mido.Message) -> bool:
        """Check if message passes all filters"""
        if msg.type not in ['note_on', 'note_off']:
            return True
        
        if self.min_note is not None and msg.note < self.min_note:
            return False
        if self.max_note is not None and msg.note > self.max_note:
            return False
        if self.min_velocity is not None and msg.velocity < self.min_velocity:
            return False
        if self.max_velocity is not None and msg.velocity > self.max_velocity:
            return False
        
        return True


class MIDICommandCenter:
    """Send MIDI commands and test Yamaha responses"""
    
    def __init__(self, output_port_name: str = 'Digital Keyboard 1'):
        self.output_port_name = output_port_name
        self.outport = None
        self.connect()
    
    def connect(self) -> bool:
        """Connect to output port"""
        try:
            self.outport = mido.open_output(self.output_port_name)
            logger.info(f"✓ Connected to {self.output_port_name}")
            return True
        except Exception as e:
            logger.error(f"✗ Cannot connect: {e}")
            return False
    
    def test_all_notes(self):
        """Send all 88 MIDI notes sequentially"""
        logger.info("Playing all 88 notes...")
        from config import PIANO_START_NOTE, PIANO_END_NOTE
        
        for note in range(PIANO_START_NOTE, PIANO_END_NOTE + 1):
            msg_on = mido.Message('note_on', note=note, velocity=100)
            self.outport.send(msg_on)
            time.sleep(0.05)
            
            msg_off = mido.Message('note_off', note=note)
            self.outport.send(msg_off)
        
        logger.info("✓ All notes played")
    
    def test_velocity_range(self):
        """Test velocity response from quiet to loud"""
        logger.info("Testing velocity range...")
        test_note = 60  # Middle C
        
        for velocity in range(1, 128, 10):
            msg_on = mido.Message('note_on', note=test_note, velocity=velocity)
            self.outport.send(msg_on)
            time.sleep(0.1)
            
            msg_off = mido.Message('note_off', note=test_note)
            self.outport.send(msg_off)
            time.sleep(0.1)
        
        logger.info("✓ Velocity test complete")
    
    def test_channels(self):
        """Test all 16 MIDI channels"""
        logger.info("Testing all MIDI channels...")
        test_note = 60
        
        for channel in range(16):
            msg_on = mido.Message('note_on', note=test_note, velocity=100, channel=channel)
            self.outport.send(msg_on)
            time.sleep(0.1)
            
            msg_off = mido.Message('note_off', note=test_note, channel=channel)
            self.outport.send(msg_off)
            time.sleep(0.1)
            
            logger.info(f"  Channel {channel + 1}: ✓")
        
        logger.info("✓ All channels tested")
    
    def test_pitch_bend(self):
        """Test pitch bend functionality"""
        logger.info("Testing pitch bend...")
        test_note = 60
        
        msg_on = mido.Message('note_on', note=test_note, velocity=100)
        self.outport.send(msg_on)
        
        for bend_value in range(0, 16384, 1000):
            msg_bend = mido.Message('pitchwheel', pitch=bend_value)
            self.outport.send(msg_bend)
            time.sleep(0.05)
        
        msg_off = mido.Message('note_off', note=test_note)
        self.outport.send(msg_off)
        
        logger.info("✓ Pitch bend test complete")
    
    def disconnect(self):
        """Disconnect from port"""
        if self.outport:
            self.outport.close()
            logger.info("Disconnected")


def main():
    """Run MIDI monitor"""
    import sys
    
    logger.info("\n" + "=" * 80)
    logger.info("YAMAHA PSR-i455 MIDI MONITOR")
    logger.info("=" * 80 + "\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            logger.info("Running MIDI output tests...")
            tester = MIDICommandCenter()
            
            logger.info("\n1. Testing all notes...")
            tester.test_all_notes()
            time.sleep(1)
            
            logger.info("\n2. Testing velocity...")
            tester.test_velocity_range()
            time.sleep(1)
            
            logger.info("\n3. Testing channels...")
            tester.test_channels()
            
            tester.disconnect()
            return
    
    # Start monitoring
    monitor = MIDIMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
