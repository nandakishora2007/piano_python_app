# Professional MIDI Handler with real-time capabilities
import mido
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MIDIMessage:
    """Structured MIDI message with timestamp"""
    type: str
    note: int = 0
    velocity: int = 0
    time: float = 0.0
    channel: int = 0
    program: Optional[int] = None
    control: Optional[int] = None
    value: Optional[int] = None


class MIDIHandler:
    """Professional MIDI input/output handler with low-latency support"""
    
    def __init__(self, input_port: str, output_port: str):
        self.input_port_name = input_port
        self.output_port_name = output_port
        self.inport = None
        self.outport = None
        self.is_connected = False
        self.message_callbacks: List[Callable] = []
        self.message_buffer = deque(maxlen=1000)
        self.listener_thread = None
        self.running = False
        self.latency_samples = deque(maxlen=100)
        
        self.connect()

    def _select_port(self, requested_port: str, available_ports: List[str], direction: str) -> Optional[str]:
        """Select a MIDI port by exact match, fuzzy match, or first available fallback."""
        if not available_ports:
            logger.warning(f"No MIDI {direction} ports available")
            return None

        if requested_port in available_ports:
            return requested_port

        if requested_port:
            requested_lower = requested_port.lower()
            for port_name in available_ports:
                port_lower = port_name.lower()
                if requested_lower in port_lower or port_lower in requested_lower:
                    logger.info(
                        f"Using closest MIDI {direction} match: '{port_name}' (requested '{requested_port}')"
                    )
                    return port_name

        fallback_port = available_ports[0]
        logger.info(
            f"Using first available MIDI {direction} port: '{fallback_port}' (requested '{requested_port}')"
        )
        return fallback_port

    def get_available_ports(self) -> tuple[List[str], List[str]]:
        """Return available MIDI input and output ports."""
        return mido.get_input_names(), mido.get_output_names()

    def reconnect(self, input_port: Optional[str] = None, output_port: Optional[str] = None) -> bool:
        """Reconnect MIDI ports at runtime."""
        was_running = self.running

        self.stop_listening()

        if self.inport:
            try:
                self.inport.close()
            except Exception:
                pass
            self.inport = None

        if self.outport:
            try:
                self.outport.close()
            except Exception:
                pass
            self.outport = None

        self.is_connected = False

        if input_port is not None:
            self.input_port_name = input_port
        if output_port is not None:
            self.output_port_name = output_port

        ok = self.connect()
        if ok and was_running:
            self.start_listening()
        return ok
    
    def connect(self) -> bool:
        """Connect to MIDI ports"""
        try:
            # Get available ports
            input_names = mido.get_input_names()
            output_names = mido.get_output_names()
            
            logger.info(f"Available inputs: {input_names}")
            logger.info(f"Available outputs: {output_names}")

            selected_input = self._select_port(self.input_port_name, input_names, "input")
            selected_output = self._select_port(self.output_port_name, output_names, "output")

            if not selected_input:
                raise RuntimeError("No MIDI input device found")
            
            # Connect to ports
            self.inport = mido.open_input(selected_input)
            self.input_port_name = selected_input

            if selected_output:
                self.outport = mido.open_output(selected_output)
                self.output_port_name = selected_output
            else:
                self.outport = None
                self.output_port_name = ""
                logger.warning("Connected input-only: no MIDI output port selected")
            
            self.is_connected = True
            logger.info(
                f"✓ Connected MIDI input='{self.input_port_name}' output='{self.output_port_name or 'None'}'"
            )
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to MIDI: {e}")
            self.is_connected = False
            return False
    
    def start_listening(self):
        """Start MIDI input listener thread"""
        if self.is_connected and not self.running:
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            logger.info("MIDI listener started")
    
    def stop_listening(self):
        """Stop MIDI input listener thread"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
        logger.info("MIDI listener stopped")
    
    def _listen_loop(self):
        """Main MIDI listening loop"""
        while self.running:
            try:
                if self.inport:
                    for msg in self.inport.iter_pending():
                        timestamp = time.time()
                        self._process_message(msg, timestamp)
            except Exception as e:
                logger.error(f"Error in MIDI listen loop: {e}")
            time.sleep(0.001)  # Small sleep to prevent CPU spinning
    
    def _process_message(self, msg: mido.Message, timestamp: float):
        """Process incoming MIDI message"""
        try:
            if msg.type not in ['note_on', 'note_off', 'program_change', 'control_change']:
                return

            midi_msg = MIDIMessage(
                type=msg.type,
                note=getattr(msg, 'note', 0),
                velocity=getattr(msg, 'velocity', 0),
                time=timestamp,
                channel=getattr(msg, 'channel', 0),
                program=getattr(msg, 'program', None),
                control=getattr(msg, 'control', None),
                value=getattr(msg, 'value', None),
            )

            # Store in buffer
            self.message_buffer.append(midi_msg)

            # Call registered callbacks
            for callback in self.message_callbacks:
                callback(midi_msg)

            # Pass through to output
            self.send_message(msg)
        except Exception as e:
            logger.error(f"Error processing MIDI message: {e}")
    
    def register_callback(self, callback: Callable):
        """Register a callback for MIDI messages"""
        self.message_callbacks.append(callback)
    
    def send_message(self, msg: mido.Message):
        """Send MIDI message to output"""
        try:
            if self.outport:
                self.outport.send(msg)
        except Exception as e:
            logger.error(f"Error sending MIDI message: {e}")
    
    def send_note_on(self, note: int, velocity: int = 100, channel: int = 0):
        """Send Note On message"""
        msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
        self.send_message(msg)
    
    def send_note_off(self, note: int, velocity: int = 0, channel: int = 0):
        """Send Note Off message"""
        msg = mido.Message('note_off', note=note, velocity=velocity, channel=channel)
        self.send_message(msg)
    
    def send_control_change(self, control: int, value: int, channel: int = 0):
        """Send Control Change message"""
        msg = mido.Message('control_change', control=control, value=value, channel=channel)
        self.send_message(msg)
    
    def send_program_change(self, program: int, channel: int = 0):
        """Send Program Change message"""
        msg = mido.Message('program_change', program=program, channel=channel)
        self.send_message(msg)
    
    def get_message_history(self, count: int = 10) -> List[MIDIMessage]:
        """Get recent MIDI messages"""
        return list(self.message_buffer)[-count:]
    
    def get_average_latency(self) -> float:
        """Get average MIDI latency"""
        if self.latency_samples:
            return sum(self.latency_samples) / len(self.latency_samples)
        return 0.0
    
    def disconnect(self):
        """Disconnect from MIDI ports"""
        self.stop_listening()
        if self.inport:
            self.inport.close()
        if self.outport:
            self.outport.close()
        self.is_connected = False
        logger.info("MIDI disconnected")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.disconnect()
        except:
            pass
