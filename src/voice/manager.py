"""
Voice Manager - Handles wake word detection, STT, TTS, and voice pipeline
"""

import asyncio
import logging
import numpy as np
import pyaudio
import queue
import threading
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    logging.warning("Porcupine not available - using mock wake word detection")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available - using mock STT")

try:
    import piper
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logging.warning("Piper not available - using mock TTS")


class VoiceState(Enum):
    """Voice system states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceCommand:
    """Represents a processed voice command."""
    text: str
    confidence: float
    timestamp: float
    wake_word: str
    processing_time: float


@dataclass
class AudioConfig:
    """Audio configuration parameters."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: int = pyaudio.paInt16
    input_device_index: Optional[int] = None


class WakeWordDetector:
    """Wake word detection using Porcupine or mock implementation."""
    
    def __init__(self, keywords: list, sensitivity: float = 0.7):
        self.keywords = keywords
        self.sensitivity = sensitivity
        self.logger = logging.getLogger(__name__)
        
        if PORCUPINE_AVAILABLE:
            try:
                self.porcupine = pvporcupine.create(
                    keywords=keywords,
                    sensitivities=[sensitivity] * len(keywords)
                )
                self.frame_length = self.porcupine.frame_length
                self.sample_rate = self.porcupine.sample_rate
                self.mock_mode = False
                self.logger.info(f"✅ Porcupine initialized with keywords: {keywords}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Porcupine: {e}")
                self._init_mock_mode()
        else:
            self._init_mock_mode()
    
    def _init_mock_mode(self):
        """Initialize mock wake word detection for development."""
        self.mock_mode = True
        self.frame_length = 512
        self.sample_rate = 16000
        self.mock_counter = 0
        self.logger.warning("🔧 Using mock wake word detection")
    
    def process_audio(self, audio_frame: np.ndarray) -> Optional[str]:
        """Process audio frame and return detected wake word if any."""
        if self.mock_mode:
            # Mock detection every 5 seconds for testing
            self.mock_counter += 1
            if self.mock_counter % (5 * self.sample_rate // self.frame_length) == 0:
                return self.keywords[0] if self.keywords else "hey-car"
            return None
        
        try:
            keyword_index = self.porcupine.process(audio_frame)
            if keyword_index >= 0:
                detected_keyword = self.keywords[keyword_index]
                self.logger.info(f"🎤 Wake word detected: {detected_keyword}")
                return detected_keyword
        except Exception as e:
            self.logger.error(f"Wake word processing error: {e}")
        
        return None
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'porcupine') and not self.mock_mode:
            self.porcupine.delete()


class SpeechToText:
    """Speech-to-text processing using Whisper or mock implementation."""
    
    def __init__(self, model_name: str = "base"):
        self.logger = logging.getLogger(__name__)
        
        if WHISPER_AVAILABLE:
            try:
                self.model = whisper.load_model(model_name)
                self.mock_mode = False
                self.logger.info(f"✅ Whisper model '{model_name}' loaded")
            except Exception as e:
                self.logger.error(f"Failed to load Whisper model: {e}")
                self._init_mock_mode()
        else:
            self._init_mock_mode()
    
    def _init_mock_mode(self):
        """Initialize mock STT for development."""
        self.mock_mode = True
        self.mock_responses = [
            "turn on air conditioning",
            "set temperature to 72 degrees",
            "what is my engine temperature",
            "turn up the volume",
            "dim the lights"
        ]
        self.mock_index = 0
        self.logger.warning("🔧 Using mock speech-to-text")
    
    async def transcribe(self, audio_data: np.ndarray) -> tuple[str, float]:
        """Transcribe audio data to text with confidence score."""
        if self.mock_mode:
            # Simulate processing time
            await asyncio.sleep(0.2)
            text = self.mock_responses[self.mock_index % len(self.mock_responses)]
            self.mock_index += 1
            return text, 0.95
        
        try:
            # Run Whisper in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.model.transcribe(audio_data, language="en")
            )
            
            text = result["text"].strip()
            confidence = 0.9  # Whisper doesn't provide confidence, use default
            
            self.logger.info(f"🗣️ Transcribed: '{text}' (confidence: {confidence:.2f})")
            return text, confidence
            
        except Exception as e:
            self.logger.error(f"Speech transcription error: {e}")
            return "", 0.0


class TextToSpeech:
    """Text-to-speech synthesis using Piper or mock implementation."""
    
    def __init__(self, voice_model: str = "en_US-lessac-medium"):
        self.logger = logging.getLogger(__name__)
        
        if PIPER_AVAILABLE:
            try:
                # Initialize Piper TTS
                self.mock_mode = False
                self.logger.info(f"✅ Piper TTS initialized with voice: {voice_model}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Piper: {e}")
                self._init_mock_mode()
        else:
            self._init_mock_mode()
    
    def _init_mock_mode(self):
        """Initialize mock TTS for development."""
        self.mock_mode = True
        self.logger.warning("🔧 Using mock text-to-speech")
    
    async def synthesize(self, text: str) -> Optional[np.ndarray]:
        """Synthesize text to speech audio."""
        if self.mock_mode:
            # Simulate TTS processing time
            await asyncio.sleep(0.3)
            self.logger.info(f"🔊 Mock TTS: '{text}'")
            return None
        
        try:
            # Run TTS in thread pool
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                None,
                lambda: self._generate_speech(text)
            )
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
            return None
    
    def _generate_speech(self, text: str) -> np.ndarray:
        """Generate speech audio from text."""
        # Placeholder for actual Piper TTS implementation
        return np.array([])


class VoiceManager:
    """Main voice processing manager."""
    
    def __init__(self, 
                 config: AudioConfig,
                 command_callback: Callable[[VoiceCommand], None],
                 keywords: list = None):
        
        self.config = config
        self.command_callback = command_callback
        self.keywords = keywords or ["hey-car", "vehicle-assistant", "emergency-override"]
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.wake_word_detector = WakeWordDetector(self.keywords)
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        
        # Audio processing
        self.audio = pyaudio.PyAudio()
        self.audio_queue = queue.Queue()
        self.recording = False
        
        # State management
        self.state = VoiceState.IDLE
        self.listening_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.stats = {
            "wake_words_detected": 0,
            "commands_processed": 0,
            "average_processing_time": 0.0
        }
    
    async def initialize(self) -> bool:
        """Initialize voice manager components."""
        try:
            self.logger.info("🎤 Initializing Voice Manager...")
            
            # Test audio input
            if not self._test_audio_input():
                return False
            
            self.state = VoiceState.IDLE
            self.logger.info("✅ Voice Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Voice Manager initialization failed: {e}")
            return False
    
    def _test_audio_input(self) -> bool:
        """Test audio input device."""
        try:
            stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.input_device_index,
                frames_per_buffer=self.config.chunk_size
            )
            
            # Test recording a small chunk
            data = stream.read(self.config.chunk_size, exception_on_overflow=False)
            stream.stop_stream()
            stream.close()
            
            self.logger.info("✅ Audio input test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Audio input test failed: {e}")
            return False
    
    async def start_listening(self) -> None:
        """Start continuous listening for wake words."""
        if self.state != VoiceState.IDLE:
            self.logger.warning("Voice manager already active")
            return
        
        self.state = VoiceState.LISTENING
        self.recording = True
        
        # Start audio capture in separate thread
        audio_thread = threading.Thread(target=self._audio_capture_thread)
        audio_thread.daemon = True
        audio_thread.start()
        
        # Start processing loop
        self.listening_task = asyncio.create_task(self._processing_loop())
        
        self.logger.info("🎤 Started listening for wake words...")
    
    def _audio_capture_thread(self) -> None:
        """Audio capture thread."""
        try:
            stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.input_device_index,
                frames_per_buffer=self.config.chunk_size
            )
            
            while self.recording:
                try:
                    data = stream.read(
                        self.config.chunk_size, 
                        exception_on_overflow=False
                    )
                    
                    # Convert to numpy array
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    self.audio_queue.put(audio_array)
                    
                except Exception as e:
                    self.logger.error(f"Audio capture error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.logger.error(f"Audio capture thread error: {e}")
    
    async def _processing_loop(self) -> None:
        """Main audio processing loop."""
        while self.recording and self.state != VoiceState.ERROR:
            try:
                # Get audio data (non-blocking)
                try:
                    audio_data = self.audio_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue
                
                # Process for wake words
                if self.state == VoiceState.LISTENING:
                    wake_word = self.wake_word_detector.process_audio(audio_data)
                    
                    if wake_word:
                        await self._handle_wake_word(wake_word)
                
            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                self.state = VoiceState.ERROR
                break
    
    async def _handle_wake_word(self, wake_word: str) -> None:
        """Handle detected wake word."""
        self.stats["wake_words_detected"] += 1
        self.state = VoiceState.PROCESSING
        
        start_time = time.time()
        
        try:
            # Collect audio for command (simulate 3 seconds)
            self.logger.info(f"🔊 Wake word '{wake_word}' detected, listening for command...")
            
            # In real implementation, would collect audio until silence
            await asyncio.sleep(3.0)  # Simulate command collection
            
            # Mock audio data for STT
            command_audio = np.array([])  # Would be actual audio data
            
            # Transcribe command
            text, confidence = await self.stt.transcribe(command_audio)
            
            if text and confidence > 0.7:
                processing_time = time.time() - start_time
                
                # Create voice command object
                voice_command = VoiceCommand(
                    text=text,
                    confidence=confidence,
                    timestamp=time.time(),
                    wake_word=wake_word,
                    processing_time=processing_time
                )
                
                # Update stats
                self.stats["commands_processed"] += 1
                avg_time = self.stats["average_processing_time"]
                self.stats["average_processing_time"] = (
                    (avg_time * (self.stats["commands_processed"] - 1) + processing_time) /
                    self.stats["commands_processed"]
                )
                
                # Send to command callback
                self.command_callback(voice_command)
                
            else:
                self.logger.warning(f"Command not understood (confidence: {confidence:.2f})")
                await self.speak("Sorry, I didn't understand that command.")
            
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            await self.speak("Sorry, there was an error processing your command.")
        
        finally:
            self.state = VoiceState.LISTENING
    
    async def speak(self, text: str) -> None:
        """Synthesize and play speech."""
        if self.state == VoiceState.ERROR:
            return
        
        prev_state = self.state
        self.state = VoiceState.SPEAKING
        
        try:
            self.logger.info(f"🔊 Speaking: '{text}'")
            audio_data = await self.tts.synthesize(text)
            
            if audio_data is not None:
                # In real implementation, would play audio
                pass
            
        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
        
        finally:
            self.state = prev_state
    
    async def stop_listening(self) -> None:
        """Stop listening and clean up."""
        self.logger.info("🛑 Stopping voice manager...")
        
        self.recording = False
        self.state = VoiceState.IDLE
        
        if self.listening_task:
            self.listening_task.cancel()
            try:
                await self.listening_task
            except asyncio.CancelledError:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get voice processing statistics."""
        return self.stats.copy()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.wake_word_detector.cleanup()
        self.audio.terminate()