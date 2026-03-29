# Professional MIDI Music Studio - ENHANCED EDITION
import pygame
import time
import logging
from config import *
from midi_handler import MIDIHandler
from recording import RecordingSession
from music_theory import MusicTheory, Scale
from renderer import PianoKeysRenderer, DisplayPanel, VelocityMeter, ScaleVisualization
from metronome import Metronome
from playback import PlaybackEngine
from quantizer import Quantizer, QuantizeGrid
from arpeggiator import Arpeggiator, ArpeggiatorMode
from chord_suggester import ChordSuggester
from effects import EffectsChain
from midi_importer import MIDIImporter
from waveform_renderer import WaveformRenderer, NoteRollEditor, PerformanceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicStudio:
    """Professional MIDI music production studio with advanced features"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.is_fullscreen = False
        self.screen = None
        self._apply_display_mode()
        pygame.display.set_caption(f"{APP_NAME} v{APP_VERSION} - ENHANCED")
        self.clock = pygame.time.Clock()
        
        # Initialize MIDI
        self.midi = MIDIHandler(MIDI_INPUT_PORT, MIDI_OUTPUT_PORT)
        self.midi.register_callback(self._on_midi_message)
        self.available_inputs = []
        self.available_outputs = []
        self._refresh_midi_ports()
        
        # Session management
        self.session = RecordingSession("Yamaha Session", bpm=DEFAULT_BPM)
        self.session.add_track("Main Track")
        
        # State
        self.active_notes = set()
        self.last_velocity = 0
        self.is_running = True
        self.current_scale = Scale.MAJOR
        self.root_note = 60  # Middle C
        self.scale_notes = set()
        self.current_program = 0
        self.bank_msb = 0
        self.bank_lsb = 0
        
        # ENHANCED FEATURES
        self.metronome = Metronome(self.midi.outport, bpm=DEFAULT_BPM)
        self.playback_engine = PlaybackEngine(self.midi.outport)
        self.quantizer = Quantizer(bpm=DEFAULT_BPM)
        self.arpeggiator = Arpeggiator(self.midi.outport, bpm=DEFAULT_BPM)
        self.chord_suggester = ChordSuggester(key=60, scale_name='Major')
        self.effects_chain = EffectsChain(self.midi.outport)
        self.midi_importer = MIDIImporter()
        
        # UI States
        self.show_waveform = False
        self.show_suggestions = False
        self.show_analysis = False
        self.quantize_strength = 0  # Disabled by default
        self.metronome_enabled = False
        self.arpeggiator_enabled = False
        self.effects_enabled = False
        
        # UI Components
        self._init_ui_components()
        
        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.latency_ms = 0
        
        logger.info("✓ Music Studio Enhanced Edition initialized")
        self._display_startup_info()
    
    def _init_ui_components(self):
        """Initialize all UI rendering components"""
        width = self.window_width
        height = self.window_height
        panel_margin = 10
        control_panel_width = 330
        control_panel_height = 170
        control_panel_x = width - control_panel_width - panel_margin
        control_panel_y = height - control_panel_height - panel_margin
        lower_content_right = max(650, control_panel_x - panel_margin)
        bottom_dock_height = control_panel_height + (panel_margin * 2)
        content_height = height - 290 - bottom_dock_height
        if content_height < 120:
            content_height = 120

        # Piano keyboard
        self.piano = PianoKeysRenderer(
            self.screen, 0, 0, width, 250
        )
        
        # Control panel (bottom dock)
        self.control_panel = DisplayPanel(
            self.screen,
            control_panel_x,
            control_panel_y,
            control_panel_width,
            control_panel_height,
        )
        
        # Info panel (left side)
        self.info_panel = DisplayPanel(
            self.screen, 10, 270, 300, content_height
        )
        
        # Velocity meter
        self.velocity_meter = VelocityMeter(
            self.screen, 320, 270, 300, 60
        )
        
        # Scale visualization
        self.scale_viz = ScaleVisualization(
            self.screen, 640, 270, 400, content_height
        )
        
        # Waveform visualizations
        self.waveform = WaveformRenderer(
            self.screen, 10, 400, lower_content_right - 10, 150
        )
        
        self.note_roll = NoteRollEditor(
            self.screen, 10, 560, lower_content_right - 10, 100
        )
        
        self.performance_analyzer = PerformanceAnalyzer(
            self.screen, max(10, control_panel_x - 290 - panel_margin), height - bottom_dock_height - 150, 280, 140
        )

    def _apply_display_mode(self):
        """Create or recreate the display surface for the active window mode."""
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.RESIZABLE,
            )

        self.window_width, self.window_height = self.screen.get_size()

    def _toggle_fullscreen(self):
        """Toggle between windowed and fullscreen modes."""
        self.is_fullscreen = not self.is_fullscreen
        self._apply_display_mode()
        self._init_ui_components()
        mode = "ON" if self.is_fullscreen else "OFF"
        logger.info(f"Fullscreen: {mode} ({self.window_width}x{self.window_height})")

    def _refresh_midi_ports(self):
        """Refresh available MIDI ports for runtime switching."""
        self.available_inputs, self.available_outputs = self.midi.get_available_ports()

    def _short_port_name(self, name: str, max_len: int = 20) -> str:
        """Return a compact display name for on-screen port labels."""
        if not name:
            return "None"
        return name if len(name) <= max_len else f"{name[:max_len - 3]}..."

    def _sync_midi_outputs(self):
        """Point all output-driven subsystems to the current MIDI out port."""
        output = self.midi.outport
        self.metronome.midi_output = output
        self.playback_engine.midi_output = output
        self.arpeggiator.midi_output = output
        self.effects_chain.reverb.midi_output = output
        self.effects_chain.delay.midi_output = output
        self.effects_chain.chorus.midi_output = output
        self.effects_chain.compressor.midi_output = output

    def _switch_midi_input(self):
        """Cycle to the next available MIDI input device."""
        self._refresh_midi_ports()
        if len(self.available_inputs) < 2:
            logger.info("MIDI input switch: only one input available")
            return

        current = self.midi.input_port_name
        current_index = self.available_inputs.index(current) if current in self.available_inputs else -1
        next_input = self.available_inputs[(current_index + 1) % len(self.available_inputs)]

        if self.midi.reconnect(input_port=next_input):
            self._sync_midi_outputs()
            logger.info(f"MIDI input switched to: {next_input}")
        else:
            logger.error("MIDI input switch failed")

    def _switch_midi_output(self):
        """Cycle to the next available MIDI output device."""
        self._refresh_midi_ports()
        if not self.available_outputs:
            logger.info("MIDI output switch: no outputs available")
            return

        current = self.midi.output_port_name
        current_index = self.available_outputs.index(current) if current in self.available_outputs else -1
        next_output = self.available_outputs[(current_index + 1) % len(self.available_outputs)]

        if self.midi.reconnect(output_port=next_output):
            self._sync_midi_outputs()
            logger.info(f"MIDI output switched to: {next_output}")
        else:
            logger.error("MIDI output switch failed")
    
    def _on_midi_message(self, msg):
        """Callback for incoming MIDI messages"""
        if msg.type == 'note_on' and msg.velocity > 0:
            self.active_notes.add(msg.note)
            self.last_velocity = msg.velocity
            
            # Feed to arpeggiator
            self.arpeggiator.on_note_on(msg.note, msg.velocity)
            
            # Record to active track
            if track := self.session.get_active_track():
                if track.is_recording:
                    track.add_message({
                        'type': 'note_on',
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'time': time.time(),
                        'channel': msg.channel
                    })
        
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            self.active_notes.discard(msg.note)
            self.arpeggiator.on_note_off(msg.note)
            
            # Record to active track
            if track := self.session.get_active_track():
                if track.is_recording:
                    track.add_message({
                        'type': 'note_off',
                        'note': msg.note,
                        'velocity': 0,
                        'time': time.time(),
                        'channel': msg.channel
                    })

        elif msg.type == 'program_change':
            self.current_program = msg.program if msg.program is not None else self.current_program
            logger.info(
                f"Voice changed: Program {self.current_program + 1} (Bank {self.bank_msb}:{self.bank_lsb})"
            )

        elif msg.type == 'control_change':
            if msg.control == 0 and msg.value is not None:
                self.bank_msb = msg.value
            elif msg.control == 32 and msg.value is not None:
                self.bank_lsb = msg.value
    
    def _update_scale_visualization(self):
        """Update scale notes based on root and current scale"""
        self.scale_notes = MusicTheory.get_scale_notes(self.root_note, self.current_scale)
    
    def _display_startup_info(self):
        """Display startup information"""
        logger.info("=" * 70)
        logger.info(f"  {APP_NAME} v{APP_VERSION} - ENHANCED EDITION")
        logger.info("=" * 70)
        logger.info("CORE CONTROLS:")
        logger.info("  [R] Record     [T] Stop       [S] Save        [E] Export")
        logger.info("  [C] Clear      [L] Load       [Q] Quit")
        logger.info("  [I] Next MIDI Input            [O] Next MIDI Output")
        logger.info("  [F11] Fullscreen Toggle       [Esc] Exit Fullscreen")
        logger.info("")
        logger.info("ADVANCED FEATURES:")
        logger.info("  [M] Metronome  [K] Playback   [A] Arpeggiator  [N] Suggestions")
        logger.info("  [W] Waveform   [F] Effects    [U] Quantize     [X] Analysis")
        logger.info("")
        logger.info("PARAMETERS:")
        logger.info("  [+/-] BPM      [1-5] Scale    [Alt+Enter] Fullscreen")
        logger.info("=" * 70)
    
    def _handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                self.window_width = max(1024, event.w)
                self.window_height = max(700, event.h)
                self._apply_display_mode()
                self._init_ui_components()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                    continue

                if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
                    self._toggle_fullscreen()
                    continue

                if event.key == pygame.K_ESCAPE and self.is_fullscreen:
                    self._toggle_fullscreen()
                    continue

                if event.key == pygame.K_i:
                    self._switch_midi_input()
                    continue

                if event.key == pygame.K_o:
                    self._switch_midi_output()
                    continue

                # Core Recording
                if event.key == pygame.K_r:
                    self.session.start_recording()
                    logger.info("▶ RECORDING STARTED")
                
                elif event.key == pygame.K_t:
                    self.session.stop_recording()
                    logger.info("⏹ RECORDING STOPPED")
                
                elif event.key == pygame.K_c:
                    if track := self.session.get_active_track():
                        track.clear()
                        logger.info(f"🗑 Cleared {track.name}")
                
                elif event.key == pygame.K_e:
                    self.session.export_to_file(EXPORTS_DIR / f"{self.session.name}.mid")
                
                elif event.key == pygame.K_s:
                    self.session.save_session(SESSIONS_DIR / f"{self.session.name}.json")
                
                elif event.key == pygame.K_l:
                    logger.info("Load function - select a file")
                
                # Parameters
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.session.bpm = min(300, self.session.bpm + 5)
                    self.metronome.set_bpm(self.session.bpm)
                    self.quantizer.bpm = self.session.bpm
                    self.arpeggiator.bpm = self.session.bpm
                    logger.info(f"BPM: {self.session.bpm}")
                
                elif event.key == pygame.K_MINUS:
                    self.session.bpm = max(40, self.session.bpm - 5)
                    self.metronome.set_bpm(self.session.bpm)
                    self.quantizer.bpm = self.session.bpm
                    self.arpeggiator.bpm = self.session.bpm
                    logger.info(f"BPM: {self.session.bpm}")
                
                # Scales
                elif event.key == pygame.K_1:
                    self.current_scale = Scale.MAJOR
                    self._update_scale_visualization()
                    logger.info("Scale: Major")
                
                elif event.key == pygame.K_2:
                    self.current_scale = Scale.MINOR
                    self._update_scale_visualization()
                    logger.info("Scale: Minor")
                
                elif event.key == pygame.K_3:
                    self.current_scale = Scale.PENTATONIC
                    self._update_scale_visualization()
                    logger.info("Scale: Pentatonic")
                
                elif event.key == pygame.K_4:
                    self.current_scale = Scale.BLUES
                    self._update_scale_visualization()
                    logger.info("Scale: Blues")
                
                elif event.key == pygame.K_5:
                    self.current_scale = Scale.HARMONIC_MINOR
                    self._update_scale_visualization()
                    logger.info("Scale: Harmonic Minor")
                
                # Advanced Features
                elif event.key == pygame.K_m:
                    self.metronome_enabled = not self.metronome_enabled
                    if self.metronome_enabled:
                        self.metronome.start()
                        logger.info("🔔 Metronome ON")
                    else:
                        self.metronome.stop()
                        logger.info("🔔 Metronome OFF")
                
                elif event.key == pygame.K_k:
                    if self.playback_engine.is_playing:
                        self.playback_engine.stop()
                        logger.info("⏹ Playback stopped")
                    else:
                        self.playback_engine.load_session(self.session)
                        self.playback_engine.play()
                        logger.info("▶ Playback started")
                
                elif event.key == pygame.K_a:
                    self.arpeggiator_enabled = not self.arpeggiator_enabled
                    if self.arpeggiator_enabled:
                        self.arpeggiator.enable()
                        logger.info("🎼 Arpeggiator ON")
                    else:
                        self.arpeggiator.disable()
                        logger.info("🎼 Arpeggiator OFF")
                
                elif event.key == pygame.K_n:
                    self.show_suggestions = not self.show_suggestions
                    if self.show_suggestions:
                        suggestions = self.chord_suggester.suggest_progressions(3)
                        logger.info("📋 Chord Suggestions:")
                        for i, prog in enumerate(suggestions):
                            logger.info(f"   {i+1}. {' → '.join(prog)}")
                    else:
                        logger.info("Suggestions hidden")
                
                elif event.key == pygame.K_w:
                    self.show_waveform = not self.show_waveform
                    logger.info(f"📊 Waveform: {'ON' if self.show_waveform else 'OFF'}")
                
                elif event.key == pygame.K_f:
                    self.effects_enabled = not self.effects_enabled
                    if self.effects_enabled:
                        self.effects_chain.enable_reverb(50)
                        self.effects_chain.enable_delay(30, 500)
                        logger.info("✨ Effects: ON (Reverb + Delay)")
                    else:
                        self.effects_chain.disable_all()
                        logger.info("✨ Effects: OFF")
                
                elif event.key == pygame.K_u:
                    self.quantize_strength = 100 if self.quantize_strength == 0 else 0
                    status = f"{self.quantize_strength}%" if self.quantize_strength > 0 else "OFF"
                    logger.info(f"⚙️ Quantization: {status}")
                
                elif event.key == pygame.K_x:
                    self.show_analysis = not self.show_analysis
                    logger.info(f"📈 Performance Analysis: {'ON' if self.show_analysis else 'OFF'}")
                
                elif event.key == pygame.K_q:
                    self.is_running = False
    
    def _update(self):
        """Update application state"""
        # Update piano keyboard visualization
        self.piano.update_active_notes(self.active_notes)
        
        # Update velocity meter
        self.velocity_meter.update_velocity(self.last_velocity)
        
        # Analyze current notes
        if self.active_notes:
            chord_root, chord_type, chord_confidence = MusicTheory.detect_chord(self.active_notes)
            scale_name, scale_confidence = MusicTheory.detect_scale(self.active_notes)
        else:
            chord_root, chord_type, chord_confidence = "---", "No Chord", 0
            scale_name, scale_confidence = "---", 0
        
        # Update control panel
        status = "🔴 REC" if self.session.is_recording else ("▶ PLAY" if self.playback_engine.is_playing else "⏹ IDLE")
        track_name = self.session.get_active_track().name if self.session.get_active_track() else "No Track"
        features = []
        if self.metronome_enabled: features.append("M")
        if self.arpeggiator_enabled: features.append("A")
        if self.effects_enabled: features.append("E")
        if self.quantize_strength > 0: features.append("Q")
        
        self.control_panel.update_data({
            'Status': status,
            'Track': track_name,
            'BPM': str(self.session.bpm),
            'Voice': f"P{self.current_program + 1} B{self.bank_msb}:{self.bank_lsb}",
            'Features': " ".join(features) if features else "None"
        })
        
        # Update info panel
        self.info_panel.update_data({
            'Chord': f"{chord_root} {chord_type}",
            'Confidence': f"{chord_confidence}%",
            'Scale': scale_name,
            'Active Notes': str(len(self.active_notes)),
            'Velocity': str(self.last_velocity)
        })
        
        # Update scale visualization
        self.scale_viz.update_scale(self.scale_notes)
        
        # Update FPS
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self.fps = self.clock.get_fps()
    
    def _render(self):
        """Render all UI elements"""
        # Clear screen
        self.screen.fill(COLORS['background'])

        # Draw a subtle dock lane at the bottom for fixed utility panels
        dock_height = 190
        dock_y = self.window_height - dock_height
        pygame.draw.rect(
            self.screen,
            (16, 16, 20),
            (0, dock_y, self.window_width, dock_height),
        )
        pygame.draw.line(
            self.screen,
            COLORS['grid'],
            (0, dock_y),
            (self.window_width, dock_y),
            2,
        )
        
        # Draw components
        self.piano.draw()
        self.control_panel.draw()
        self.info_panel.draw()
        self.velocity_meter.draw()
        self.scale_viz.draw()
        
        # Optional visualizations
        if self.show_waveform and self.session.get_active_track():
            self.waveform.update_messages(self.session.get_active_track().messages)
            self.waveform.draw()
            self.note_roll.update_messages(self.session.get_active_track().messages)
            self.note_roll.draw()
        
        if self.show_analysis and self.session.get_active_track():
            self.performance_analyzer.update_data(self.session.get_active_track().messages)
            self.performance_analyzer.draw()
        
        # Draw FPS and playback status
        font_small = pygame.font.Font(None, 18)
        fps_text = font_small.render(f"FPS: {self.fps:.0f}", True, COLORS['text'])
        self.screen.blit(fps_text, (self.window_width - 100, self.window_height - 30))
        
        if self.playback_engine.is_playing:
            status = self.playback_engine.get_status()
            pb_text = font_small.render(f"PB: {status['position']:.1f}s", True, COLORS['text'])
            self.screen.blit(pb_text, (self.window_width - 100, self.window_height - 50))

        midi_text = font_small.render(
            f"MIDI [I/O] In: {self._short_port_name(self.midi.input_port_name)}  Out: {self._short_port_name(self.midi.output_port_name)}",
            True,
            COLORS['text'],
        )
        self.screen.blit(midi_text, (10, self.window_height - 24))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main application loop"""
        self.midi.start_listening()
        self._update_scale_visualization()
        
        try:
            while self.is_running:
                self._handle_input()
                self._update()
                self._render()
                self.clock.tick(REFRESH_RATE)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        
        # Stop features
        self.metronome.stop()
        self.playback_engine.stop()
        self.arpeggiator.stop()
        self.effects_chain.disable_all()
        
        # Save session
        try:
            self.session.save_session(SESSIONS_DIR / "auto_save.json")
            logger.info("✓ Session auto-saved")
        except:
            pass
        
        # Cleanup MIDI
        self.midi.stop_listening()
        self.midi.disconnect()
        
        # Cleanup Pygame
        pygame.quit()
        
        logger.info(f"✓ {APP_NAME} closed")


def main():
    """Application entry point"""
    try:
        studio = MusicStudio()
        studio.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
