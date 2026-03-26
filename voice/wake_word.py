"""
Aara Wake Word Detection
Supports Picovoice and keyboard hotkey activation.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional

from config.settings import SETTINGS, WakeWordProvider

logger = logging.getLogger(__name__)


class WakeWordDetector(ABC):
    """Abstract base class for wake word detection."""

    def __init__(self):
        """Initialize detector."""
        self._running = False
        self._on_activation: Optional[Callable] = None

    @property
    def on_activation(self) -> Optional[Callable]:
        """Get activation callback."""
        return self._on_activation

    @on_activation.setter
    def on_activation(self, callback: Callable) -> None:
        """Set activation callback."""
        self._on_activation = callback

    @abstractmethod
    def start(self) -> None:
        """Start listening for wake word."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop listening."""
        pass

    def wait_for_activation(self) -> bool:
        """
        Block until activation is detected.

        Returns:
            True if activated, False if stopped
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this detector is available."""
        pass


class PicovoiceDetector(WakeWordDetector):
    """Picovoice Porcupine wake word detector (premium)."""

    def __init__(self, access_key: str, keyword_path: Optional[str] = None):
        """
        Initialize Picovoice detector.

        Args:
            access_key: Picovoice access key
            keyword_path: Optional path to custom wake word .ppn file
        """
        super().__init__()
        self.access_key = access_key
        self.keyword_path = keyword_path
        self._porcupine = None
        self._pa = None
        self._audio_stream = None
        self._available = False
        self._activation_event = threading.Event()
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Picovoice is available."""
        if not self.access_key:
            logger.warning("Picovoice access key not provided")
            return

        try:
            import pvporcupine
            self._pvporcupine = pvporcupine
            self._available = True
            logger.info("Picovoice detector available")
        except ImportError:
            logger.warning("Picovoice not installed. Run: pip install pvporcupine")

    def is_available(self) -> bool:
        return self._available

    def start(self) -> None:
        """Start listening for wake word."""
        if not self._available or self._running:
            return

        try:
            import pyaudio

            # Create Porcupine instance
            if self.keyword_path:
                self._porcupine = self._pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.keyword_path],
                )
            else:
                # Use built-in keyword
                self._porcupine = self._pvporcupine.create(
                    access_key=self.access_key,
                    keywords=["picovoice"],  # Default, replace with custom
                )

            # Set up audio stream
            self._pa = pyaudio.PyAudio()
            self._audio_stream = self._pa.open(
                rate=self._porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self._porcupine.frame_length,
            )

            self._running = True
            self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._listen_thread.start()

            logger.info("Picovoice wake word detection started")

        except Exception as e:
            logger.error(f"Failed to start Picovoice: {e}")
            self._running = False

    def _listen_loop(self) -> None:
        """Listen for wake word."""
        try:
            while self._running:
                pcm = self._audio_stream.read(
                    self._porcupine.frame_length,
                    exception_on_overflow=False,
                )
                pcm = [int.from_bytes(pcm[i:i+2], byteorder="little", signed=True)
                       for i in range(0, len(pcm), 2)]

                keyword_index = self._porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    self._activation_event.set()
                    if self._on_activation:
                        self._on_activation()

        except Exception as e:
            logger.error(f"Picovoice listen error: {e}")
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop listening."""
        self._running = False
        self._activation_event.set()  # Unblock wait_for_activation

        if self._audio_stream:
            try:
                self._audio_stream.close()
            except Exception:
                pass
            self._audio_stream = None

        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None

        if self._porcupine:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None

    def wait_for_activation(self) -> bool:
        """Wait for wake word detection."""
        self._activation_event.clear()
        self._activation_event.wait()
        return self._running


class HotkeyDetector(WakeWordDetector):
    """Keyboard hotkey detector (free alternative)."""

    def __init__(self, hotkey: str = "ctrl+space"):
        """
        Initialize hotkey detector.

        Args:
            hotkey: Hotkey combination (e.g., "ctrl+space", "ctrl+shift+a")
        """
        super().__init__()
        self.hotkey = hotkey
        self._listener = None
        self._available = False
        self._activation_event = threading.Event()
        self._pressed_keys = set()
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if pynput is available."""
        try:
            from pynput import keyboard
            self._keyboard = keyboard
            self._available = True
            logger.info(f"Hotkey detector available (hotkey: {self.hotkey})")
        except ImportError:
            logger.warning("Pynput not installed. Run: pip install pynput")

    def is_available(self) -> bool:
        return self._available

    def _parse_hotkey(self) -> set:
        """Parse hotkey string to key set."""
        keys = set()
        parts = self.hotkey.lower().split("+")

        for part in parts:
            part = part.strip()
            if part == "ctrl":
                keys.add(self._keyboard.Key.ctrl_l)
            elif part == "shift":
                keys.add(self._keyboard.Key.shift)
            elif part == "alt":
                keys.add(self._keyboard.Key.alt_l)
            elif part == "space":
                keys.add(self._keyboard.Key.space)
            elif part == "enter":
                keys.add(self._keyboard.Key.enter)
            elif len(part) == 1:
                keys.add(self._keyboard.KeyCode.from_char(part))

        return keys

    def start(self) -> None:
        """Start listening for hotkey."""
        if not self._available or self._running:
            return

        try:
            self._target_keys = self._parse_hotkey()
            self._pressed_keys = set()

            def on_press(key):
                self._pressed_keys.add(key)
                # Also check for _l and _r variants
                if hasattr(key, "name"):
                    if key.name.endswith("_l") or key.name.endswith("_r"):
                        base_key = getattr(self._keyboard.Key, key.name[:-2], None)
                        if base_key:
                            self._pressed_keys.add(base_key)

                if self._target_keys.issubset(self._pressed_keys):
                    logger.info(f"Hotkey {self.hotkey} detected!")
                    self._activation_event.set()
                    if self._on_activation:
                        self._on_activation()
                    return False  # Stop listener

            def on_release(key):
                self._pressed_keys.discard(key)
                if hasattr(key, "name"):
                    if key.name.endswith("_l") or key.name.endswith("_r"):
                        base_key = getattr(self._keyboard.Key, key.name[:-2], None)
                        if base_key:
                            self._pressed_keys.discard(base_key)

            self._listener = self._keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
            )
            self._listener.start()
            self._running = True

            logger.info(f"Hotkey detection started (press {self.hotkey})")

        except Exception as e:
            logger.error(f"Failed to start hotkey detector: {e}")

    def stop(self) -> None:
        """Stop listening."""
        self._running = False
        self._activation_event.set()

        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def wait_for_activation(self) -> bool:
        """Wait for hotkey activation."""
        self._activation_event.clear()

        # Re-start listener if needed
        if not self._running:
            self.start()

        self._activation_event.wait()
        return self._running


class DummyDetector(WakeWordDetector):
    """Dummy detector (for testing/keyboard only mode)."""

    def __init__(self):
        super().__init__()
        self._activation_event = threading.Event()

    def is_available(self) -> bool:
        return True

    def start(self) -> None:
        self._running = True
        logger.info("Dummy detector started (call trigger() to activate)")

    def stop(self) -> None:
        self._running = False
        self._activation_event.set()

    def trigger(self) -> None:
        """Manually trigger activation."""
        logger.info("Manual activation triggered")
        self._activation_event.set()
        if self._on_activation:
            self._on_activation()

    def wait_for_activation(self) -> bool:
        self._activation_event.clear()
        self._activation_event.wait()
        return self._running


def create_wake_detector() -> WakeWordDetector:
    """Factory function to create the best available wake word detector."""
    provider = SETTINGS.wake_word.provider
    logger.info(f"Creating wake word detector with provider: {provider.value}")

    if provider == WakeWordProvider.PICOVOICE:
        detector = PicovoiceDetector(
            access_key=SETTINGS.wake_word.picovoice_key or "",
        )
        if detector.is_available():
            return detector
        logger.warning("Picovoice not available, falling back to hotkey")

    # Default to hotkey
    detector = HotkeyDetector(hotkey=SETTINGS.wake_word.hotkey)
    if detector.is_available():
        return detector

    logger.warning("No wake word detector available, using dummy")
    return DummyDetector()
