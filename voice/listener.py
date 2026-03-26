"""
Aara Speech-to-Text Listener
Multi-provider STT with Whisper and fallbacks.
"""

import logging
import tempfile
import wave
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from config.settings import SETTINGS, STTProvider
from voice.audio_utils import record_audio

logger = logging.getLogger(__name__)


class STTListener(ABC):
    """Abstract base class for speech-to-text listeners."""

    @abstractmethod
    def listen(self, timeout: float = 10.0) -> Tuple[str, str]:
        """
        Listen and transcribe speech.

        Args:
            timeout: Maximum recording duration in seconds

        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this listener is available."""
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        return self.__class__.__name__


class WhisperListener(STTListener):
    """Whisper-based speech-to-text listener."""

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper listener.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large-v3)
        """
        self.model_name = model_name
        self._model = None
        self._available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Whisper is available."""
        try:
            import whisper
            self._whisper = whisper
            self._available = True
            logger.info(f"Whisper available (model: {self.model_name})")
        except ImportError:
            logger.warning("Whisper not installed. Run: pip install openai-whisper")
            self._available = False

    def _load_model(self) -> None:
        """Lazy load the Whisper model."""
        if self._model is None and self._available:
            logger.info(f"Loading Whisper model: {self.model_name}")
            try:
                self._model = self._whisper.load_model(self.model_name)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self._available = False

    def is_available(self) -> bool:
        return self._available

    def listen(self, timeout: float = 10.0) -> Tuple[str, str]:
        """Listen and transcribe speech using Whisper."""
        if not self._available:
            return "", "en"

        self._load_model()
        if self._model is None:
            return "", "en"

        try:
            # Record audio
            logger.debug(f"Recording audio for {timeout} seconds...")
            audio_data = record_audio(duration=timeout)

            if audio_data is None or len(audio_data) == 0:
                logger.warning("No audio recorded")
                return "", "en"

            # Save to temporary file (Whisper requires a file)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                self._save_audio(audio_data, temp_path)

            # Transcribe
            logger.debug("Transcribing audio...")
            result = self._model.transcribe(
                temp_path,
                language=None,  # Auto-detect
                task="transcribe",
            )

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            text = result.get("text", "").strip()
            language = result.get("language", "en")

            # Map to our supported languages
            if language == "hi":
                detected_lang = "hi"
            else:
                detected_lang = "en"

            logger.info(f"Transcribed: '{text[:50]}...' (lang: {detected_lang})")
            return text, detected_lang

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return "", "en"

    def _save_audio(self, audio_data: np.ndarray, path: str) -> None:
        """Save audio data to WAV file."""
        audio_int16 = (audio_data * 32767).astype(np.int16)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_int16.tobytes())


class VoskListener(STTListener):
    """Vosk-based speech-to-text listener (lightweight offline)."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Vosk listener.

        Args:
            model_path: Path to Vosk model directory
        """
        self.model_path = model_path
        self._model = None
        self._available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Vosk is available."""
        try:
            import vosk
            self._vosk = vosk
            self._available = True
            logger.info("Vosk available")
        except ImportError:
            logger.warning("Vosk not installed. Run: pip install vosk")
            self._available = False

    def _load_model(self) -> None:
        """Lazy load the Vosk model."""
        if self._model is None and self._available:
            try:
                # Download model if not specified
                if self.model_path and Path(self.model_path).exists():
                    self._model = self._vosk.Model(self.model_path)
                else:
                    # Use SetLogLevel to reduce output
                    self._vosk.SetLogLevel(-1)
                    # This will download a small model automatically
                    self._model = self._vosk.Model(lang="en-us")
                logger.info("Vosk model loaded")
            except Exception as e:
                logger.error(f"Failed to load Vosk model: {e}")
                self._available = False

    def is_available(self) -> bool:
        return self._available

    def listen(self, timeout: float = 10.0) -> Tuple[str, str]:
        """Listen and transcribe speech using Vosk."""
        if not self._available:
            return "", "en"

        self._load_model()
        if self._model is None:
            return "", "en"

        try:
            import json

            # Record audio
            audio_data = record_audio(duration=timeout)
            if audio_data is None or len(audio_data) == 0:
                return "", "en"

            # Convert to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Create recognizer
            rec = self._vosk.KaldiRecognizer(self._model, 16000)

            # Process audio
            rec.AcceptWaveform(audio_int16.tobytes())
            result = json.loads(rec.FinalResult())

            text = result.get("text", "").strip()
            logger.info(f"Vosk transcribed: '{text[:50]}...'")

            # Vosk doesn't detect language, assume English
            return text, "en"

        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")
            return "", "en"


class DummyListener(STTListener):
    """Dummy listener for when no STT is available."""

    def is_available(self) -> bool:
        return True

    def listen(self, timeout: float = 10.0) -> Tuple[str, str]:
        """Return empty string (for keyboard input fallback)."""
        logger.warning("No STT available, use keyboard input")
        return "", "en"


def create_listener() -> STTListener:
    """Factory function to create the best available STT listener."""
    provider = SETTINGS.stt.provider
    logger.info(f"Creating STT listener with provider: {provider.value}")

    # Try providers based on settings
    if provider in (STTProvider.WHISPER_LARGE, STTProvider.WHISPER_BASE, STTProvider.WHISPER_TINY):
        model_map = {
            STTProvider.WHISPER_LARGE: "large-v3",
            STTProvider.WHISPER_BASE: "base",
            STTProvider.WHISPER_TINY: "tiny",
        }
        listener = WhisperListener(model_name=model_map.get(provider, SETTINGS.stt.whisper_model))
        if listener.is_available():
            return listener
        logger.warning("Whisper not available, trying Vosk")

    if provider == STTProvider.VOSK:
        listener = VoskListener()
        if listener.is_available():
            return listener
        logger.warning("Vosk not available")

    # Try fallbacks
    for ListenerClass in [WhisperListener, VoskListener]:
        try:
            listener = ListenerClass()
            if listener.is_available():
                logger.info(f"Using fallback listener: {listener.get_provider_name()}")
                return listener
        except Exception:
            continue

    logger.warning("No STT available, using dummy listener")
    return DummyListener()
