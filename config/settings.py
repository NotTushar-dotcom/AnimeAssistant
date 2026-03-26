"""
Aara Configuration Settings
Complete configuration system with provider enums, presets, and auto-detection.
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# PROVIDER ENUMS
# =============================================================================

class LLMProvider(Enum):
    """LLM service providers."""
    ANTHROPIC = "anthropic"      # Premium - Claude
    OPENAI = "openai"            # Premium - GPT-4
    GROQ = "groq"                # Free tier - Llama 3.1
    GEMINI = "gemini"            # Free tier - Gemini
    OLLAMA = "ollama"            # Free local
    OPENROUTER = "openrouter"    # Mixed


class TTSProvider(Enum):
    """Text-to-Speech providers."""
    ELEVENLABS = "elevenlabs"    # Premium
    EDGE_TTS = "edge_tts"        # Free - Microsoft
    PYTTSX3 = "pyttsx3"          # Free - Offline


class STTProvider(Enum):
    """Speech-to-Text providers."""
    WHISPER_LARGE = "whisper_large"  # Best, needs GPU
    WHISPER_BASE = "whisper_base"    # Good, CPU ok
    WHISPER_TINY = "whisper_tiny"    # Fast, lower quality
    VOSK = "vosk"                     # Lightweight offline


class WakeWordProvider(Enum):
    """Wake word detection providers."""
    PICOVOICE = "picovoice"      # Premium
    HOTKEY = "hotkey"            # Free - Ctrl+Space


class SearchProvider(Enum):
    """Web search providers."""
    SERPER = "serper"            # Premium - Google
    DUCKDUCKGO = "duckduckgo"    # Free


class WeatherProvider(Enum):
    """Weather data providers."""
    OPENWEATHERMAP = "openweathermap"  # Free tier
    OPEN_METEO = "open_meteo"          # Free, no key


# =============================================================================
# CONFIGURATION DATACLASSES
# =============================================================================

@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = "llama3.2:8b"
    temperature: float = 0.7
    max_tokens: int = 2048
    anthropic_key: Optional[str] = None
    groq_key: Optional[str] = None
    google_key: Optional[str] = None
    openrouter_key: Optional[str] = None
    ollama_host: str = "http://localhost:11434"


@dataclass
class TTSConfig:
    """Text-to-Speech configuration."""
    provider: TTSProvider = TTSProvider.EDGE_TTS
    elevenlabs_key: Optional[str] = None
    elevenlabs_voice_english: str = ""
    elevenlabs_voice_hindi: str = ""
    edge_voice_english: str = "en-US-AnaNeural"
    edge_voice_hindi: str = "hi-IN-SwaraNeural"
    speed: float = 1.0
    pitch: float = 1.0


@dataclass
class STTConfig:
    """Speech-to-Text configuration."""
    provider: STTProvider = STTProvider.WHISPER_BASE
    whisper_model: str = "base"
    language: str = "en"
    sample_rate: int = 16000


@dataclass
class WakeWordConfig:
    """Wake word detection configuration."""
    provider: WakeWordProvider = WakeWordProvider.HOTKEY
    picovoice_key: Optional[str] = None
    hotkey: str = "ctrl+space"
    sensitivity: float = 0.5


@dataclass
class SearchConfig:
    """Web search configuration."""
    provider: SearchProvider = SearchProvider.DUCKDUCKGO
    serper_key: Optional[str] = None
    max_results: int = 5


@dataclass
class WeatherConfig:
    """Weather service configuration."""
    provider: WeatherProvider = WeatherProvider.OPEN_METEO
    openweathermap_key: Optional[str] = None
    default_city: str = "Delhi"
    units: str = "metric"


@dataclass
class UIConfig:
    """UI configuration."""
    theme: str = "dark"
    window_position: str = "bottom-right"
    start_minimized: bool = False
    always_on_top: bool = True
    opacity: float = 1.0


@dataclass
class AppSettings:
    """Main application settings container."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    wake_word: WakeWordConfig = field(default_factory=WakeWordConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    user_name: str = ""
    debug_mode: bool = False
    log_level: str = "INFO"
    data_dir: Path = field(default_factory=lambda: Path("data"))

    def __post_init__(self):
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "logs").mkdir(exist_ok=True)
        (self.data_dir / "chromadb").mkdir(exist_ok=True)


# =============================================================================
# AUTO-DETECTION FUNCTIONS
# =============================================================================

def _check_api_key(key_name: str, min_length: int = 10) -> bool:
    """Check if an API key exists and is valid."""
    key = os.getenv(key_name, "")
    return len(key) >= min_length


def _detect_llm_provider() -> tuple[LLMProvider, str]:
    """Detect the best available LLM provider."""
    if _check_api_key("ANTHROPIC_API_KEY"):
        return LLMProvider.ANTHROPIC, "claude-sonnet-4-20250514"
    if _check_api_key("GROQ_API_KEY"):
        return LLMProvider.GROQ, "llama-3.1-70b-versatile"
    if _check_api_key("GOOGLE_API_KEY"):
        return LLMProvider.GEMINI, "gemini-1.5-flash"
    if _check_api_key("OPENROUTER_API_KEY"):
        return LLMProvider.OPENROUTER, "meta-llama/llama-3.1-8b-instruct:free"
    # Default to Ollama (local)
    return LLMProvider.OLLAMA, os.getenv("OLLAMA_MODEL", "llama3.2:8b")


def _detect_tts_provider() -> TTSProvider:
    """Detect the best available TTS provider."""
    if _check_api_key("ELEVENLABS_API_KEY"):
        return TTSProvider.ELEVENLABS
    return TTSProvider.EDGE_TTS


def _detect_wake_provider() -> WakeWordProvider:
    """Detect the best available wake word provider."""
    if _check_api_key("PICOVOICE_ACCESS_KEY"):
        return WakeWordProvider.PICOVOICE
    return WakeWordProvider.HOTKEY


def _detect_search_provider() -> SearchProvider:
    """Detect the best available search provider."""
    if _check_api_key("SERPER_API_KEY"):
        return SearchProvider.SERPER
    return SearchProvider.DUCKDUCKGO


def _detect_weather_provider() -> WeatherProvider:
    """Detect the best available weather provider."""
    if _check_api_key("OPENWEATHERMAP_API_KEY"):
        return WeatherProvider.OPENWEATHERMAP
    return WeatherProvider.OPEN_METEO


# =============================================================================
# PRESET CONFIGURATIONS
# =============================================================================

def get_free_preset() -> AppSettings:
    """Get configuration using only free services."""
    settings = AppSettings()

    # LLM: Ollama (local)
    settings.llm = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model=os.getenv("OLLAMA_MODEL", "llama3.2:8b"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    )

    # TTS: Edge TTS (free)
    settings.tts = TTSConfig(
        provider=TTSProvider.EDGE_TTS,
        edge_voice_english=os.getenv("EDGE_TTS_VOICE_ENGLISH", "en-US-AnaNeural"),
        edge_voice_hindi=os.getenv("EDGE_TTS_VOICE_HINDI", "hi-IN-SwaraNeural"),
    )

    # STT: Whisper base (local)
    settings.stt = STTConfig(
        provider=STTProvider.WHISPER_BASE,
        whisper_model="base",
    )

    # Wake word: Hotkey
    settings.wake_word = WakeWordConfig(
        provider=WakeWordProvider.HOTKEY,
        hotkey=os.getenv("ACTIVATION_HOTKEY", "ctrl+space"),
    )

    # Search: DuckDuckGo
    settings.search = SearchConfig(provider=SearchProvider.DUCKDUCKGO)

    # Weather: Open-Meteo
    settings.weather = WeatherConfig(
        provider=WeatherProvider.OPEN_METEO,
        default_city=os.getenv("DEFAULT_CITY", "Delhi"),
    )

    return settings


def get_balanced_preset() -> AppSettings:
    """Get balanced configuration (free cloud LLM + free TTS)."""
    settings = get_free_preset()

    # Upgrade LLM to Groq if available
    if _check_api_key("GROQ_API_KEY"):
        settings.llm = LLMConfig(
            provider=LLMProvider.GROQ,
            model="llama-3.1-70b-versatile",
            groq_key=os.getenv("GROQ_API_KEY"),
        )
    elif _check_api_key("GOOGLE_API_KEY"):
        settings.llm = LLMConfig(
            provider=LLMProvider.GEMINI,
            model="gemini-1.5-flash",
            google_key=os.getenv("GOOGLE_API_KEY"),
        )

    return settings


def get_premium_preset() -> AppSettings:
    """Get premium configuration (best quality, costs money)."""
    settings = AppSettings()

    # LLM: Claude
    settings.llm = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model="claude-sonnet-4-20250514",
        anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
    )

    # TTS: ElevenLabs
    settings.tts = TTSConfig(
        provider=TTSProvider.ELEVENLABS,
        elevenlabs_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_english=os.getenv("ELEVENLABS_VOICE_ID_ENGLISH", ""),
        elevenlabs_voice_hindi=os.getenv("ELEVENLABS_VOICE_ID_HINDI", ""),
    )

    # STT: Whisper large
    settings.stt = STTConfig(
        provider=STTProvider.WHISPER_LARGE,
        whisper_model="large-v3",
    )

    # Wake word: Picovoice
    settings.wake_word = WakeWordConfig(
        provider=WakeWordProvider.PICOVOICE,
        picovoice_key=os.getenv("PICOVOICE_ACCESS_KEY"),
    )

    # Search: Serper
    settings.search = SearchConfig(
        provider=SearchProvider.SERPER,
        serper_key=os.getenv("SERPER_API_KEY"),
    )

    # Weather: OpenWeatherMap
    settings.weather = WeatherConfig(
        provider=WeatherProvider.OPENWEATHERMAP,
        openweathermap_key=os.getenv("OPENWEATHERMAP_API_KEY"),
        default_city=os.getenv("DEFAULT_CITY", "Delhi"),
    )

    return settings


def get_auto_preset() -> AppSettings:
    """Auto-detect best available services."""
    settings = AppSettings()

    # Auto-detect LLM
    llm_provider, llm_model = _detect_llm_provider()
    settings.llm = LLMConfig(
        provider=llm_provider,
        model=llm_model,
        anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
        groq_key=os.getenv("GROQ_API_KEY"),
        google_key=os.getenv("GOOGLE_API_KEY"),
        openrouter_key=os.getenv("OPENROUTER_API_KEY"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    )

    # Auto-detect TTS
    tts_provider = _detect_tts_provider()
    settings.tts = TTSConfig(
        provider=tts_provider,
        elevenlabs_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_english=os.getenv("ELEVENLABS_VOICE_ID_ENGLISH", ""),
        elevenlabs_voice_hindi=os.getenv("ELEVENLABS_VOICE_ID_HINDI", ""),
        edge_voice_english=os.getenv("EDGE_TTS_VOICE_ENGLISH", "en-US-AnaNeural"),
        edge_voice_hindi=os.getenv("EDGE_TTS_VOICE_HINDI", "hi-IN-SwaraNeural"),
    )

    # STT: Use configured Whisper model
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    stt_provider = {
        "large-v3": STTProvider.WHISPER_LARGE,
        "large": STTProvider.WHISPER_LARGE,
        "base": STTProvider.WHISPER_BASE,
        "tiny": STTProvider.WHISPER_TINY,
    }.get(whisper_model, STTProvider.WHISPER_BASE)
    settings.stt = STTConfig(
        provider=stt_provider,
        whisper_model=whisper_model,
    )

    # Auto-detect wake word
    wake_provider = _detect_wake_provider()
    settings.wake_word = WakeWordConfig(
        provider=wake_provider,
        picovoice_key=os.getenv("PICOVOICE_ACCESS_KEY"),
        hotkey=os.getenv("ACTIVATION_HOTKEY", "ctrl+space"),
    )

    # Auto-detect search
    search_provider = _detect_search_provider()
    settings.search = SearchConfig(
        provider=search_provider,
        serper_key=os.getenv("SERPER_API_KEY"),
    )

    # Auto-detect weather
    weather_provider = _detect_weather_provider()
    settings.weather = WeatherConfig(
        provider=weather_provider,
        openweathermap_key=os.getenv("OPENWEATHERMAP_API_KEY"),
        default_city=os.getenv("DEFAULT_CITY", "Delhi"),
    )

    return settings


def load_settings() -> AppSettings:
    """Load settings based on preset or auto-detection."""
    preset = os.getenv("AARA_PRESET", "auto").lower()

    presets = {
        "free": get_free_preset,
        "balanced": get_balanced_preset,
        "premium": get_premium_preset,
        "auto": get_auto_preset,
    }

    settings = presets.get(preset, get_auto_preset)()

    # Apply common settings from env
    settings.user_name = os.getenv("USER_NAME", "")
    settings.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    settings.log_level = os.getenv("LOG_LEVEL", "INFO")
    settings.ui.theme = os.getenv("THEME", "dark")
    settings.ui.window_position = os.getenv("WINDOW_POSITION", "bottom-right")
    settings.ui.start_minimized = os.getenv("START_MINIMIZED", "false").lower() == "true"

    return settings


# =============================================================================
# GLOBAL SETTINGS SINGLETON
# =============================================================================

SETTINGS = load_settings()
