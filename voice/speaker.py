"""
Aara Text-to-Speech Speaker
Multi-provider TTS with ElevenLabs, Edge TTS, and fallbacks.
"""

import asyncio
import logging
import tempfile
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from config.settings import SETTINGS, TTSProvider
from voice.audio_utils import play_sound_file

logger = logging.getLogger(__name__)


class TTSSpeaker(ABC):
    """Abstract base class for text-to-speech speakers."""

    @abstractmethod
    def speak(self, text: str, language: str = "en") -> None:
        """
        Speak text synchronously.

        Args:
            text: Text to speak
            language: Language code ("en" or "hi")
        """
        pass

    def speak_async(self, text: str, language: str = "en") -> None:
        """
        Speak text asynchronously (non-blocking).

        Args:
            text: Text to speak
            language: Language code
        """
        thread = threading.Thread(target=self.speak, args=(text, language), daemon=True)
        thread.start()

    @abstractmethod
    def stop(self) -> None:
        """Stop current speech."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this speaker is available."""
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        return self.__class__.__name__


class ElevenLabsSpeaker(TTSSpeaker):
    """ElevenLabs TTS speaker (premium)."""

    def __init__(self, api_key: str, voice_id_en: str = "", voice_id_hi: str = ""):
        """
        Initialize ElevenLabs speaker.

        Args:
            api_key: ElevenLabs API key
            voice_id_en: English voice ID
            voice_id_hi: Hindi voice ID
        """
        self.api_key = api_key
        self.voice_id_en = voice_id_en or "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
        self.voice_id_hi = voice_id_hi or self.voice_id_en
        self._available = False
        self._client = None
        self._is_speaking = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if ElevenLabs is available."""
        if not self.api_key:
            logger.warning("ElevenLabs API key not provided")
            return

        try:
            from elevenlabs import ElevenLabs
            self._client = ElevenLabs(api_key=self.api_key)
            self._available = True
            logger.info("ElevenLabs speaker available")
        except ImportError:
            logger.warning("ElevenLabs not installed. Run: pip install elevenlabs")
        except Exception as e:
            logger.warning(f"ElevenLabs initialization failed: {e}")

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str, language: str = "en") -> None:
        """Speak using ElevenLabs."""
        if not self._available or not text.strip():
            return

        try:
            self._is_speaking = True
            voice_id = self.voice_id_hi if language == "hi" else self.voice_id_en

            # Generate audio
            audio = self._client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
            )

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                for chunk in audio:
                    f.write(chunk)
                temp_path = f.name

            play_sound_file(temp_path)
            Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"ElevenLabs speak error: {e}")
        finally:
            self._is_speaking = False

    def stop(self) -> None:
        """Stop current speech."""
        self._is_speaking = False


class EdgeTTSSpeaker(TTSSpeaker):
    """Microsoft Edge TTS speaker (free)."""

    def __init__(self, voice_en: str = "en-US-AnaNeural", voice_hi: str = "hi-IN-SwaraNeural"):
        """
        Initialize Edge TTS speaker.

        Args:
            voice_en: English voice name
            voice_hi: Hindi voice name
        """
        self.voice_en = voice_en
        self.voice_hi = voice_hi
        self._available = False
        self._is_speaking = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Edge TTS is available."""
        try:
            import edge_tts
            self._edge_tts = edge_tts
            self._available = True
            logger.info("Edge TTS speaker available")
        except ImportError:
            logger.warning("Edge TTS not installed. Run: pip install edge-tts")

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str, language: str = "en") -> None:
        """Speak using Edge TTS."""
        if not self._available or not text.strip():
            return

        try:
            self._is_speaking = True
            voice = self.voice_hi if language == "hi" else self.voice_en

            # Create temp file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            # Run async synthesis
            async def synthesize():
                communicate = self._edge_tts.Communicate(text, voice)
                await communicate.save(temp_path)

            # Run in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(synthesize())
            finally:
                loop.close()

            # Play audio
            if self._is_speaking:
                play_sound_file(temp_path)

            # Clean up
            Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Edge TTS speak error: {e}")
        finally:
            self._is_speaking = False

    def stop(self) -> None:
        """Stop current speech."""
        self._is_speaking = False


class Pyttsx3Speaker(TTSSpeaker):
    """Pyttsx3 TTS speaker (offline fallback)."""

    def __init__(self):
        """Initialize pyttsx3 speaker."""
        self._engine = None
        self._available = False
        self._is_speaking = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if pyttsx3 is available."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            # Set properties
            self._engine.setProperty("rate", 175)  # Speed
            self._engine.setProperty("volume", 0.9)
            self._available = True
            logger.info("Pyttsx3 speaker available")
        except ImportError:
            logger.warning("Pyttsx3 not installed. Run: pip install pyttsx3")
        except Exception as e:
            logger.warning(f"Pyttsx3 initialization failed: {e}")

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str, language: str = "en") -> None:
        """Speak using pyttsx3."""
        if not self._available or not text.strip():
            return

        try:
            self._is_speaking = True

            # Try to set voice based on language
            voices = self._engine.getProperty("voices")
            for voice in voices:
                if language == "hi" and "hindi" in voice.name.lower():
                    self._engine.setProperty("voice", voice.id)
                    break
                elif language == "en" and "english" in voice.name.lower():
                    self._engine.setProperty("voice", voice.id)
                    break

            self._engine.say(text)
            self._engine.runAndWait()

        except Exception as e:
            logger.error(f"Pyttsx3 speak error: {e}")
        finally:
            self._is_speaking = False

    def stop(self) -> None:
        """Stop current speech."""
        self._is_speaking = False
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass


class DummySpeaker(TTSSpeaker):
    """Dummy speaker when no TTS is available."""

    def is_available(self) -> bool:
        return True

    def speak(self, text: str, language: str = "en") -> None:
        """Just log the text (for debugging)."""
        logger.info(f"[TTS would say]: {text}")
        print(f"[Aara]: {text}")

    def stop(self) -> None:
        pass


def create_speaker() -> TTSSpeaker:
    """Factory function to create the best available TTS speaker."""
    provider = SETTINGS.tts.provider
    logger.info(f"Creating TTS speaker with provider: {provider.value}")

    # Try provider based on settings
    if provider == TTSProvider.ELEVENLABS:
        speaker = ElevenLabsSpeaker(
            api_key=SETTINGS.tts.elevenlabs_key or "",
            voice_id_en=SETTINGS.tts.elevenlabs_voice_english,
            voice_id_hi=SETTINGS.tts.elevenlabs_voice_hindi,
        )
        if speaker.is_available():
            return speaker
        logger.warning("ElevenLabs not available, trying Edge TTS")

    if provider == TTSProvider.EDGE_TTS:
        speaker = EdgeTTSSpeaker(
            voice_en=SETTINGS.tts.edge_voice_english,
            voice_hi=SETTINGS.tts.edge_voice_hindi,
        )
        if speaker.is_available():
            return speaker
        logger.warning("Edge TTS not available, trying pyttsx3")

    if provider == TTSProvider.PYTTSX3:
        speaker = Pyttsx3Speaker()
        if speaker.is_available():
            return speaker

    # Try fallbacks
    for SpeakerClass in [EdgeTTSSpeaker, Pyttsx3Speaker, ElevenLabsSpeaker]:
        try:
            if SpeakerClass == ElevenLabsSpeaker:
                speaker = SpeakerClass(api_key=SETTINGS.tts.elevenlabs_key or "")
            else:
                speaker = SpeakerClass()
            if speaker.is_available():
                logger.info(f"Using fallback speaker: {speaker.get_provider_name()}")
                return speaker
        except Exception:
            continue

    logger.warning("No TTS available, using dummy speaker")
    return DummySpeaker()
