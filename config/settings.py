# =============================================================================
# AARA CONFIGURATION - SETTINGS
# =============================================================================
# Supports both Premium (paid) and Free alternatives for all services

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# SERVICE TIERS
# =============================================================================

class ServiceTier(Enum):
    """Choose between premium (paid) or free alternatives"""
    PREMIUM = "premium"
    FREE = "free"


# =============================================================================
# LLM CONFIGURATION
# =============================================================================

class LLMProvider(Enum):
    """
    Premium Options:
    - ANTHROPIC: Claude Opus 4.6 (Best quality, $15/1M tokens)
    - OPENAI: GPT-4o ($5/1M tokens)

    Free Options:
    - OLLAMA: Local LLMs (Llama 3.2, Mistral, Qwen) - Completely free, runs on your PC
    - GROQ: Cloud inference (Llama 3.1 70B) - Free tier: 30 req/min
    - GEMINI: Google Gemini 1.5 Flash - Free tier: 15 req/min
    - OPENROUTER: Multiple models - Some free models available
    """
    # Premium
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

    # Free
    OLLAMA = "ollama"
    GROQ = "groq"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


@dataclass
class LLMConfig:
    provider: LLMProvider = LLMProvider.OLLAMA  # Default to free

    # Premium settings
    anthropic_model: str = "claude-opus-4-6"
    openai_model: str = "gpt-4o"

    # Free settings
    ollama_model: str = "llama3.2:8b"  # or "mistral", "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"
    groq_model: str = "llama-3.1-70b-versatile"
    gemini_model: str = "gemini-1.5-flash"
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"

    # API Keys (from .env)
    @property
    def api_key(self) -> Optional[str]:
        keys = {
            LLMProvider.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY"),
            LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY"),
            LLMProvider.GROQ: os.getenv("GROQ_API_KEY"),
            LLMProvider.GEMINI: os.getenv("GOOGLE_API_KEY"),
            LLMProvider.OPENROUTER: os.getenv("OPENROUTER_API_KEY"),
            LLMProvider.OLLAMA: None,  # No key needed
        }
        return keys.get(self.provider)


# =============================================================================
# TEXT-TO-SPEECH CONFIGURATION
# =============================================================================

class TTSProvider(Enum):
    """
    Premium Options:
    - ELEVENLABS: Best quality, Japanese accent possible ($5/mo starter)

    Free Options:
    - EDGE_TTS: Microsoft Edge voices, good quality, many languages (FREE!)
    - COQUI: Open source, customizable, can clone voices (FREE, local)
    - BARK: Very expressive, can do accents, slower (FREE, local)
    - PYTTSX3: Basic offline TTS, works everywhere (FREE, local)
    """
    # Premium
    ELEVENLABS = "elevenlabs"

    # Free
    EDGE_TTS = "edge_tts"      # Best free option - Microsoft voices
    COQUI = "coqui"            # Open source, good for custom voices
    BARK = "bark"              # Most expressive free option
    PYTTSX3 = "pyttsx3"        # Basic offline fallback


@dataclass
class TTSConfig:
    provider: TTSProvider = TTSProvider.EDGE_TTS  # Default to free

    # ElevenLabs (Premium)
    elevenlabs_voice_id_en: str = ""
    elevenlabs_voice_id_hi: str = ""

    # Edge TTS (Free - RECOMMENDED)
    # Japanese-accented English approximation: use Japanese voice with English text
    # or use these natural-sounding voices:
    edge_voice_en: str = "en-US-AnaNeural"        # Young female, clear
    edge_voice_en_alt: str = "en-GB-SoniaNeural"  # British, softer
    edge_voice_hi: str = "hi-IN-SwaraNeural"      # Hindi female
    edge_voice_jp: str = "ja-JP-NanamiNeural"     # Japanese (for accent effect)

    # Coqui TTS (Free)
    coqui_model: str = "tts_models/en/ljspeech/tacotron2-DDC"

    # Bark (Free)
    bark_voice: str = "v2/en_speaker_6"  # Young female

    # Voice settings
    speed: float = 1.0
    pitch: float = 1.0


# =============================================================================
# SPEECH-TO-TEXT CONFIGURATION
# =============================================================================

class STTProvider(Enum):
    """
    Premium Options:
    - WHISPER_API: OpenAI's cloud Whisper ($0.006/min)

    Free Options:
    - WHISPER_LOCAL: Same Whisper, runs locally (FREE, needs GPU for speed)
    - VOSK: Lightweight, fast, offline (FREE)
    - GOOGLE_FREE: Google Speech Recognition (FREE, limited)
    """
    # Premium
    WHISPER_API = "whisper_api"

    # Free
    WHISPER_LOCAL = "whisper_local"  # Best accuracy, needs resources
    VOSK = "vosk"                     # Fast, lightweight
    GOOGLE_FREE = "google_free"       # Basic, no setup needed


@dataclass
class STTConfig:
    provider: STTProvider = STTProvider.WHISPER_LOCAL  # Default to free

    # Whisper settings
    whisper_model: str = "base"  # tiny, base, small, medium, large-v3
    # Recommendation: "base" for speed, "small" for accuracy, "large-v3" if you have GPU

    # Vosk settings
    vosk_model_en: str = "vosk-model-small-en-us-0.15"
    vosk_model_hi: str = "vosk-model-small-hi-0.22"

    # General
    sample_rate: int = 16000
    language: str = "auto"  # "en", "hi", or "auto"


# =============================================================================
# WAKE WORD CONFIGURATION
# =============================================================================

class WakeWordProvider(Enum):
    """
    Premium Options:
    - PICOVOICE: Custom wake words, very accurate (Free tier: 3 custom words)

    Free Options:
    - OPENWAKEWORD: Open source, good accuracy (FREE)
    - HOTKEY_ONLY: No wake word, use Ctrl+Space only (FREE)
    - VOSK_KEYWORD: Use Vosk for keyword spotting (FREE)
    """
    # Premium
    PICOVOICE = "picovoice"

    # Free
    OPENWAKEWORD = "openwakeword"
    HOTKEY_ONLY = "hotkey_only"
    VOSK_KEYWORD = "vosk_keyword"


@dataclass
class WakeWordConfig:
    provider: WakeWordProvider = WakeWordProvider.HOTKEY_ONLY  # Default to free

    # Picovoice
    picovoice_keyword_path: str = "assets/hey_aara.ppn"

    # OpenWakeWord
    openwakeword_model: str = "hey_jarvis"  # closest free alternative

    # Hotkey
    activation_hotkey: str = "ctrl+space"

    # Sensitivity
    sensitivity: float = 0.5


# =============================================================================
# WEB SEARCH CONFIGURATION
# =============================================================================

class SearchProvider(Enum):
    """
    Premium Options:
    - SERPER: Google results ($50/5000 searches)
    - TAVILY: AI-optimized search ($0.01/search)

    Free Options:
    - DUCKDUCKGO: DuckDuckGo instant answers (FREE, unlimited)
    - SEARXNG: Self-hosted meta search (FREE)
    - WIKIPEDIA: For factual queries (FREE)
    """
    # Premium
    SERPER = "serper"
    TAVILY = "tavily"

    # Free
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"
    WIKIPEDIA = "wikipedia"


@dataclass
class SearchConfig:
    provider: SearchProvider = SearchProvider.DUCKDUCKGO  # Default to free
    searxng_url: str = "https://searx.be"  # Public instance, or self-host


# =============================================================================
# WEATHER CONFIGURATION
# =============================================================================

class WeatherProvider(Enum):
    """
    Both free options work great:
    - OPENWEATHERMAP: Needs API key, free tier (FREE)
    - OPEN_METEO: No API key needed at all! (FREE)
    """
    OPENWEATHERMAP = "openweathermap"
    OPEN_METEO = "open_meteo"  # Recommended - no key needed!


@dataclass
class WeatherConfig:
    provider: WeatherProvider = WeatherProvider.OPEN_METEO
    default_city: str = "New Delhi"
    units: str = "metric"  # metric or imperial


# =============================================================================
# MAIN APPLICATION SETTINGS
# =============================================================================

@dataclass
class AppSettings:
    """Main application configuration"""

    # Service configurations
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    wake_word: WakeWordConfig = field(default_factory=WakeWordConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)

    # UI Settings
    start_minimized: bool = False
    always_on_top: bool = True
    character_position: str = "bottom_right"
    theme: str = "dark"  # dark, light, sakura

    # Voice settings
    auto_listen_after_response: bool = True
    voice_feedback_sounds: bool = True

    # Memory settings
    conversation_history_limit: int = 20
    enable_long_term_memory: bool = True

    # Debug
    debug_mode: bool = False
    log_level: str = "INFO"


# =============================================================================
# QUICK PRESETS
# =============================================================================

def get_free_preset() -> AppSettings:
    """All free services - no API keys needed except optional Groq"""
    settings = AppSettings()
    settings.llm.provider = LLMProvider.OLLAMA
    settings.tts.provider = TTSProvider.EDGE_TTS
    settings.stt.provider = STTProvider.WHISPER_LOCAL
    settings.wake_word.provider = WakeWordProvider.HOTKEY_ONLY
    settings.search.provider = SearchProvider.DUCKDUCKGO
    settings.weather.provider = WeatherProvider.OPEN_METEO
    return settings


def get_premium_preset() -> AppSettings:
    """Premium services for best quality"""
    settings = AppSettings()
    settings.llm.provider = LLMProvider.ANTHROPIC
    settings.tts.provider = TTSProvider.ELEVENLABS
    settings.stt.provider = STTProvider.WHISPER_LOCAL  # Local is actually better
    settings.wake_word.provider = WakeWordProvider.PICOVOICE
    settings.search.provider = SearchProvider.SERPER
    settings.weather.provider = WeatherProvider.OPEN_METEO  # Free is fine
    return settings


def get_balanced_preset() -> AppSettings:
    """Mix of free local + some cloud services"""
    settings = AppSettings()
    settings.llm.provider = LLMProvider.GROQ  # Free tier, cloud quality
    settings.tts.provider = TTSProvider.EDGE_TTS  # Free, good quality
    settings.stt.provider = STTProvider.WHISPER_LOCAL
    settings.wake_word.provider = WakeWordProvider.HOTKEY_ONLY
    settings.search.provider = SearchProvider.DUCKDUCKGO
    settings.weather.provider = WeatherProvider.OPEN_METEO
    return settings


# =============================================================================
# LOAD SETTINGS
# =============================================================================

# Default to free preset
SETTINGS = get_free_preset()

# Override with environment variables if set
if os.getenv("AARA_PRESET") == "premium":
    SETTINGS = get_premium_preset()
elif os.getenv("AARA_PRESET") == "balanced":
    SETTINGS = get_balanced_preset()
