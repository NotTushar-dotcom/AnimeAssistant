"""
Aara Audio Utilities
Audio capture, playback, and device management.
"""

import logging
from pathlib import Path
from typing import Optional, List

import numpy as np

logger = logging.getLogger(__name__)

# Audio settings
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1


def record_audio(
    duration: float = 5.0,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    device: Optional[int] = None,
) -> Optional[np.ndarray]:
    """
    Record audio from microphone.

    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
        device: Optional audio device index

    Returns:
        NumPy array of audio samples (float32, normalized to [-1, 1])
    """
    try:
        import sounddevice as sd

        logger.debug(f"Recording {duration}s of audio at {sample_rate}Hz...")

        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            device=device,
        )
        sd.wait()

        # Flatten to 1D if needed
        if audio.ndim > 1:
            audio = audio.flatten()

        # Check if we got meaningful audio
        if np.max(np.abs(audio)) < 0.001:
            logger.warning("Recorded audio appears to be silent")

        logger.debug(f"Recorded {len(audio)} samples")
        return audio

    except ImportError:
        logger.error("sounddevice not installed. Run: pip install sounddevice")
        return None
    except Exception as e:
        logger.error(f"Audio recording error: {e}")
        return None


def play_audio(
    audio: np.ndarray,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    device: Optional[int] = None,
    blocking: bool = True,
) -> None:
    """
    Play audio array through speakers.

    Args:
        audio: NumPy array of audio samples
        sample_rate: Sample rate in Hz
        device: Optional output device index
        blocking: Whether to block until playback completes
    """
    try:
        import sounddevice as sd

        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize if needed
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val

        sd.play(audio, samplerate=sample_rate, device=device)
        if blocking:
            sd.wait()

    except ImportError:
        logger.error("sounddevice not installed. Run: pip install sounddevice")
    except Exception as e:
        logger.error(f"Audio playback error: {e}")


def play_sound_file(path: str, blocking: bool = True) -> None:
    """
    Play an audio file (WAV, MP3, etc.).

    Args:
        path: Path to audio file
        blocking: Whether to block until playback completes
    """
    file_path = Path(path)
    if not file_path.exists():
        logger.error(f"Audio file not found: {path}")
        return

    try:
        import soundfile as sf
        import sounddevice as sd

        # Read audio file
        audio, sample_rate = sf.read(str(file_path))

        # Play
        sd.play(audio, samplerate=sample_rate)
        if blocking:
            sd.wait()

    except ImportError:
        # Try fallback with simpleaudio or playsound
        try:
            from playsound import playsound
            playsound(str(file_path), block=blocking)
        except ImportError:
            logger.error("No audio playback library available. Install soundfile or playsound.")
    except Exception as e:
        logger.error(f"Audio file playback error: {e}")


def get_input_devices() -> List[dict]:
    """
    Get list of available audio input devices.

    Returns:
        List of device info dicts with 'index', 'name', 'channels'
    """
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        input_devices = []

        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                input_devices.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "sample_rate": dev["default_samplerate"],
                })

        return input_devices

    except ImportError:
        logger.error("sounddevice not installed")
        return []
    except Exception as e:
        logger.error(f"Error getting input devices: {e}")
        return []


def get_output_devices() -> List[dict]:
    """
    Get list of available audio output devices.

    Returns:
        List of device info dicts
    """
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        output_devices = []

        for i, dev in enumerate(devices):
            if dev["max_output_channels"] > 0:
                output_devices.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_output_channels"],
                    "sample_rate": dev["default_samplerate"],
                })

        return output_devices

    except ImportError:
        return []
    except Exception as e:
        logger.error(f"Error getting output devices: {e}")
        return []


def get_default_input_device() -> Optional[dict]:
    """
    Get the default audio input device.

    Returns:
        Device info dict or None
    """
    try:
        import sounddevice as sd

        dev_index = sd.default.device[0]
        if dev_index is not None:
            dev = sd.query_devices(dev_index)
            return {
                "index": dev_index,
                "name": dev["name"],
                "channels": dev["max_input_channels"],
                "sample_rate": dev["default_samplerate"],
            }
        return None

    except ImportError:
        return None
    except Exception as e:
        logger.error(f"Error getting default device: {e}")
        return None


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = DEFAULT_SAMPLE_RATE) -> bytes:
    """
    Convert audio array to WAV file bytes.

    Args:
        audio: NumPy array of audio samples
        sample_rate: Sample rate

    Returns:
        WAV file content as bytes
    """
    import io
    import wave

    # Convert to int16
    if audio.dtype == np.float32 or audio.dtype == np.float64:
        audio_int16 = (audio * 32767).astype(np.int16)
    else:
        audio_int16 = audio.astype(np.int16)

    # Create WAV in memory
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    buffer.seek(0)
    return buffer.read()


def normalize_audio(audio: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
    """
    Normalize audio to a target peak level.

    Args:
        audio: Input audio array
        target_peak: Target peak value (0-1)

    Returns:
        Normalized audio array
    """
    current_peak = np.max(np.abs(audio))
    if current_peak > 0:
        return audio * (target_peak / current_peak)
    return audio


def detect_silence(
    audio: np.ndarray,
    threshold: float = 0.01,
    min_silence_duration: float = 0.5,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> bool:
    """
    Detect if audio is mostly silence.

    Args:
        audio: Audio array
        threshold: Amplitude threshold for silence
        min_silence_duration: Minimum silence duration to consider
        sample_rate: Audio sample rate

    Returns:
        True if audio is considered silent
    """
    # Calculate RMS energy in windows
    window_size = int(sample_rate * min_silence_duration)
    if len(audio) < window_size:
        return np.max(np.abs(audio)) < threshold

    # Check if any window has audio above threshold
    for i in range(0, len(audio) - window_size, window_size // 2):
        window = audio[i:i + window_size]
        if np.max(np.abs(window)) > threshold:
            return False

    return True
