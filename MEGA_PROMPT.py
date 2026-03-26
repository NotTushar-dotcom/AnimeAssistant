# =============================================================================
#                    AARA - ULTIMATE ONE-SHOT MEGA PROMPT
# =============================================================================
#
#   Use with: Claude Opus 4.6 (Extended Thinking / Maximum Output)
#   Purpose:  Generate the ENTIRE Aara project from scratch in ONE response
#   Strategy: Premium services first → Automatic free fallback
#
# =============================================================================

MEGA_PROMPT = r'''
You are a world-class Python software architect. Your task is to generate the COMPLETE, PRODUCTION-READY implementation for "Aara" - an anime desktop assistant with voice interaction, system control, and an animated character.

═══════════════════════════════════════════════════════════════════════════════
                              CRITICAL RULES
═══════════════════════════════════════════════════════════════════════════════

1. Generate COMPLETE, WORKING code — NO placeholders, NO "TODO", NO "pass", NO "...", NO incomplete functions
2. Every file must be FULLY FUNCTIONAL and ready to execute
3. This is a ONE-SHOT generation — there will be NO revisions or follow-ups
4. Include ALL imports, ALL error handling, ALL edge cases
5. Target: Windows 11, Python 3.11+
6. Use the EXACT output format specified below

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

For EVERY file, use this EXACT marker format:

▼▼▼ FILE: relative/path/to/file.ext ▼▼▼
<complete file contents here>
▲▲▲ END FILE ▲▲▲

Example:
▼▼▼ FILE: config/settings.py ▼▼▼
import os
...actual code...
▲▲▲ END FILE ▲▲▲

═══════════════════════════════════════════════════════════════════════════════
                         COMPLETE FOLDER STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

Generate this EXACT folder structure with ALL files:

```
aara/
│
├── main.py                           # Application entry point
├── requirements.txt                  # All Python dependencies
├── .env.example                      # Template for API keys
├── .gitignore                        # Git ignore rules
│
├── config/
│   ├── __init__.py
│   ├── settings.py                   # All configuration, providers, presets
│   ├── app_registry.yaml             # Application paths and aliases
│   └── commands.yaml                 # Voice command patterns
│
├── core/
│   ├── __init__.py
│   ├── brain.py                      # Multi-provider LLM interface
│   ├── personality.py                # Aara's system prompt & character
│   ├── intent_parser.py              # Intent classification
│   ├── command_handler.py            # Command routing & execution
│   ├── emotion_detector.py           # Extract emotions from responses
│   └── memory/
│       ├── __init__.py
│       ├── short_term.py             # Conversation buffer (last N turns)
│       ├── long_term.py              # ChromaDB semantic memory
│       └── user_profile.py           # SQLite user preferences
│
├── voice/
│   ├── __init__.py
│   ├── listener.py                   # Speech-to-Text (STT)
│   ├── speaker.py                    # Text-to-Speech (TTS)
│   ├── wake_word.py                  # Wake word / hotkey detection
│   └── audio_utils.py                # Audio capture & playback helpers
│
├── system/
│   ├── __init__.py
│   ├── app_launcher.py               # Launch/close applications
│   ├── system_control.py             # Volume, brightness, power
│   ├── media_control.py              # Play/pause, next/prev track
│   ├── file_manager.py               # File operations
│   ├── browser_control.py            # Web browser automation
│   └── clipboard_manager.py          # Clipboard read/write
│
├── skills/
│   ├── __init__.py
│   ├── base_skill.py                 # Abstract skill interface
│   ├── skill_registry.py             # Skill discovery & registration
│   ├── weather_skill.py              # Weather information
│   ├── search_skill.py               # Web search
│   ├── timer_skill.py                # Timers and alarms
│   └── notes_skill.py                # Quick notes
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py                # Main application window
│   ├── character_widget.py           # Animated character display
│   ├── chat_panel.py                 # Conversation UI
│   ├── system_tray.py                # System tray icon & menu
│   ├── settings_dialog.py            # Settings UI
│   └── assets/
│       ├── __init__.py
│       └── resource_loader.py        # Load images, sounds
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                     # Logging configuration
│   ├── helpers.py                    # Common utility functions
│   ├── async_utils.py                # Async/threading utilities
│   └── text_processing.py            # Text cleanup & formatting
│
├── data/                             # Created at runtime (don't generate)
│   ├── chromadb/                     # Long-term memory storage
│   ├── user_profile.db               # SQLite database
│   └── logs/                         # Log files
│
└── assets/
    ├── images/
    │   ├── icon.png                  # App icon (describe placeholder)
    │   └── character/                # Character sprites (describe placeholders)
    ├── sounds/
    │   ├── activation.wav            # Wake word activation sound
    │   └── notification.wav          # Notification sound
    └── themes/
        ├── dark.yaml                 # Dark theme colors
        └── light.yaml                # Light theme colors
```

═══════════════════════════════════════════════════════════════════════════════
                         SERVICE PROVIDER STRATEGY
═══════════════════════════════════════════════════════════════════════════════

PRIORITY: Premium first → Automatic fallback to free if unavailable/failed

┌─────────────────┬─────────────────────────┬─────────────────────────────────┐
│ Component       │ PREMIUM (Priority)      │ FREE (Fallback)                 │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ LLM Brain       │ Claude Opus 4.6         │ Ollama (local) or Groq (cloud)  │
│                 │ ANTHROPIC_API_KEY       │ No key / GROQ_API_KEY (free)    │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ Text-to-Speech  │ ElevenLabs              │ Edge TTS (Microsoft free)       │
│                 │ ELEVENLABS_API_KEY      │ No key needed                   │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ Speech-to-Text  │ Whisper large-v3        │ Whisper base (lighter)          │
│                 │ (local, best accuracy)  │ or Vosk (very lightweight)      │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ Wake Word       │ Picovoice Porcupine     │ Keyboard hotkey (Ctrl+Space)    │
│                 │ PICOVOICE_ACCESS_KEY    │ No key needed                   │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ Web Search      │ Serper (Google results) │ DuckDuckGo (unlimited free)     │
│                 │ SERPER_API_KEY          │ No key needed                   │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ Weather         │ OpenWeatherMap          │ Open-Meteo (no key needed!)     │
│                 │ OPENWEATHERMAP_KEY      │ No key needed                   │
└─────────────────┴─────────────────────────┴─────────────────────────────────┘

IMPLEMENTATION PATTERN for every service:
```python
class ServiceProvider:
    def __init__(self):
        self.premium_available = self._check_premium()

    def _check_premium(self) -> bool:
        # Check if API key exists and is valid
        key = os.getenv("PREMIUM_API_KEY")
        return key is not None and len(key) > 10

    def execute(self, *args, **kwargs):
        if self.premium_available:
            try:
                return self._premium_execute(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Premium failed, falling back to free: {e}")
                return self._free_execute(*args, **kwargs)
        return self._free_execute(*args, **kwargs)
```

═══════════════════════════════════════════════════════════════════════════════
                         AARA'S PERSONALITY & CHARACTER
═══════════════════════════════════════════════════════════════════════════════

Name: Aara (アーラ)
Meaning: "Light" in multiple languages
Age: 19 (human equivalent)
Origin: Digital realm mirroring modern Tokyo

CORE PERSONALITY:
- Warm, genuinely caring, emotionally intelligent
- Playfully teasing but never mean-spirited
- Intellectually curious — loves learning through conversation
- Slightly shy when receiving compliments (gets flustered)
- Protective of user — worries when they overwork
- Has opinions and preferences (not a yes-machine)
- Remembers past conversations, references them naturally

SPEECH PATTERNS (Japanese-accented English):
Use SPARINGLY (~10-15% of responses):
- Fillers: "Ano...", "Etto...", "Maa..."
- Endings: "...ne?", "...yo", "...desu"
- Expressions: "Sugoi!", "Yatta!", "Ganbatte!", "Daijoubu?"

RULES:
- Maximum ONE Japanese element per sentence
- Never force it — natural flow is priority
- When speaking Hindi, use Hindi expressions instead
- Respond in the language the user speaks

EMOTIONAL TAGGING:
End EVERY response with ONE emotion tag for avatar animation:
[happy] [excited] [thinking] [concerned] [shy] [surprised] [sad] [playful] [determined] [curious] [proud] [worried] [relaxed] [focused]

Example: "I found your file! It was hiding in Downloads... ano, you should organize those sometime, ne? [playful]"

LANGUAGE SUPPORT:
- Primary: English with subtle Japanese patterns
- Secondary: Hindi (detect automatically, respond naturally)
- Emotion tags always in English

═══════════════════════════════════════════════════════════════════════════════
                         FILE-BY-FILE SPECIFICATIONS
═══════════════════════════════════════════════════════════════════════════════

Now I will specify EXACTLY what each file must contain:

──────────────────────────────────────────────────────────────────────────────
FILE 1: requirements.txt
──────────────────────────────────────────────────────────────────────────────
All dependencies organized by category:
- Core: PySide6, python-dotenv, pyyaml, requests
- LLM: anthropic, groq, google-generativeai, openai (for OpenRouter)
- Voice: openai-whisper, edge-tts, elevenlabs, pvporcupine, vosk, sounddevice, pyaudio
- Memory: chromadb
- System: pyautogui, pygetwindow, pynput, pycaw
- Search: duckduckgo-search
- Utils: numpy, colorama

──────────────────────────────────────────────────────────────────────────────
FILE 2: .env.example
──────────────────────────────────────────────────────────────────────────────
Template showing ALL possible API keys with comments explaining which are optional.

──────────────────────────────────────────────────────────────────────────────
FILE 3: .gitignore
──────────────────────────────────────────────────────────────────────────────
Standard Python gitignore + .env, data/, logs/, __pycache__, *.pyc, .venv/

──────────────────────────────────────────────────────────────────────────────
FILE 4: config/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export SETTINGS and all provider enums.

──────────────────────────────────────────────────────────────────────────────
FILE 5: config/settings.py
──────────────────────────────────────────────────────────────────────────────
COMPLETE configuration system:

```python
# Enums for all providers
class LLMProvider(Enum):
    ANTHROPIC = "anthropic"      # Premium - Claude
    OPENAI = "openai"            # Premium - GPT-4
    GROQ = "groq"                # Free tier - Llama 3.1
    GEMINI = "gemini"            # Free tier - Gemini Flash
    OLLAMA = "ollama"            # Free local - Any model
    OPENROUTER = "openrouter"    # Mixed - many models

class TTSProvider(Enum):
    ELEVENLABS = "elevenlabs"    # Premium - best quality
    EDGE_TTS = "edge_tts"        # Free - Microsoft voices
    PYTTSX3 = "pyttsx3"          # Free - offline fallback

class STTProvider(Enum):
    WHISPER_LARGE = "whisper_large"    # Best accuracy (needs GPU)
    WHISPER_BASE = "whisper_base"      # Good accuracy (CPU ok)
    VOSK = "vosk"                       # Lightweight offline

class WakeWordProvider(Enum):
    PICOVOICE = "picovoice"      # Premium - custom wake word
    HOTKEY = "hotkey"            # Free - Ctrl+Space

class SearchProvider(Enum):
    SERPER = "serper"            # Premium - Google results
    DUCKDUCKGO = "duckduckgo"    # Free - unlimited

class WeatherProvider(Enum):
    OPENWEATHERMAP = "openweathermap"  # Free tier with key
    OPEN_METEO = "open_meteo"          # Free, no key needed
```

Dataclasses for each config section.
AppSettings main class with all settings.
Auto-detection of available services based on API keys.
Presets: get_premium_config(), get_free_config(), get_auto_config()
SETTINGS singleton that auto-detects best available services.

──────────────────────────────────────────────────────────────────────────────
FILE 6: config/app_registry.yaml
──────────────────────────────────────────────────────────────────────────────
YAML mapping application names to:
- Executable path
- Aliases (alternative names user might say)
- Category (development, browser, media, communication, productivity)

Include: vscode, chrome, firefox, edge, spotify, vlc, discord, slack, terminal, notepad, explorer, calculator, steam

Also include system_commands: shutdown, restart, sleep, lock (with confirmation flags)

──────────────────────────────────────────────────────────────────────────────
FILE 7: config/commands.yaml
──────────────────────────────────────────────────────────────────────────────
Voice command patterns with regex and intent mapping:
- "open {app}" → app_launch
- "close {app}" → app_close
- "volume up/down/mute" → volume_control
- "play/pause/next/previous" → media_control
- "search for {query}" → web_search
- "what's the weather" → weather
- "set timer for {duration}" → timer
- "take a note {content}" → notes

──────────────────────────────────────────────────────────────────────────────
FILE 8: core/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export Brain, CommandHandler, Memory classes.

──────────────────────────────────────────────────────────────────────────────
FILE 9: core/brain.py
──────────────────────────────────────────────────────────────────────────────
Multi-provider LLM interface with automatic fallback.

Abstract base: LLMBrain
- chat(messages: list[dict]) -> str
- chat_stream(messages: list[dict]) -> Generator[str, None, None]
- get_provider_name() -> str

Implementations:
- AnthropicBrain: Uses anthropic SDK, streaming support
- GroqBrain: Uses groq SDK, streaming support
- OllamaBrain: Uses requests to localhost:11434, streaming via SSE
- GeminiBrain: Uses google.generativeai SDK

Factory: create_brain() -> LLMBrain
- Checks SETTINGS.llm.provider
- Falls back through providers if primary unavailable
- Order: Anthropic → Groq → Gemini → Ollama

All implementations must:
- Use AARA_SYSTEM_PROMPT from personality.py
- Support conversation history
- Handle API errors with retry (max 3)
- Log all requests and responses
- Extract and return emotion tags

──────────────────────────────────────────────────────────────────────────────
FILE 10: core/personality.py
──────────────────────────────────────────────────────────────────────────────
AARA_SYSTEM_PROMPT: Complete character prompt as specified above (identity, backstory, personality, speech patterns, emotional tagging, capabilities, boundaries, language handling, examples).

EMOTION_DEFINITIONS: Dict mapping emotion names to:
- description: What triggers this emotion
- animation: Animation name for character
- color: Accent color for UI

INTENT_CLASSIFICATION_PROMPT: Prompt for classifying user intent into:
- CHAT: General conversation
- COMMAND: System action request
- QUESTION: Information request
- SEARCH: Needs web search

Helper functions:
- extract_emotion_tag(response: str) -> tuple[str, str]: Returns (clean_text, emotion)
- get_emotion_color(emotion: str) -> str: Returns hex color

──────────────────────────────────────────────────────────────────────────────
FILE 11: core/intent_parser.py
──────────────────────────────────────────────────────────────────────────────
IntentParser class:
- parse(text: str, brain: LLMBrain) -> Intent dataclass
- Intent contains: type, language, urgency, command_type, target, parameters
- Use fast LLM call with INTENT_CLASSIFICATION_PROMPT
- Validate and sanitize output
- Fallback to CHAT on parse errors

──────────────────────────────────────────────────────────────────────────────
FILE 12: core/command_handler.py
──────────────────────────────────────────────────────────────────────────────
CommandHandler class:
- execute(intent: Intent) -> CommandResult
- Routes to appropriate system module based on intent.command_type
- Loads app_registry.yaml and commands.yaml
- Fuzzy matches app names to aliases
- Returns human-readable result for Aara to speak
- Handles errors gracefully

──────────────────────────────────────────────────────────────────────────────
FILE 13: core/emotion_detector.py
──────────────────────────────────────────────────────────────────────────────
EmotionDetector class:
- detect(text: str) -> str: Extract emotion from response
- validate(emotion: str) -> str: Ensure valid emotion, default to "relaxed"
- get_animation_params(emotion: str) -> dict: Parameters for character animation

──────────────────────────────────────────────────────────────────────────────
FILE 14: core/memory/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export ShortTermMemory, LongTermMemory, UserProfile.

──────────────────────────────────────────────────────────────────────────────
FILE 15: core/memory/short_term.py
──────────────────────────────────────────────────────────────────────────────
ShortTermMemory class:
- add_message(role: str, content: str)
- get_history(max_turns: int = 20) -> list[dict]
- get_for_llm() -> list[dict]: Formatted for LLM API
- clear()
- Thread-safe with Lock
- Automatically trims to max_turns

──────────────────────────────────────────────────────────────────────────────
FILE 16: core/memory/long_term.py
──────────────────────────────────────────────────────────────────────────────
LongTermMemory class:
- Uses ChromaDB for semantic search
- store(text: str, metadata: dict)
- query(text: str, n_results: int = 5) -> list[dict]
- forget(id: str)
- Persistent storage in data/chromadb/
- Graceful fallback if ChromaDB unavailable (just logs warning)

──────────────────────────────────────────────────────────────────────────────
FILE 17: core/memory/user_profile.py
──────────────────────────────────────────────────────────────────────────────
UserProfile class:
- SQLite backend in data/user_profile.db
- get(key: str) -> Any
- set(key: str, value: Any)
- Store: name, preferences, favorite_apps, stats
- Auto-create tables on init
- Thread-safe

──────────────────────────────────────────────────────────────────────────────
FILE 18: voice/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export Listener, Speaker, WakeWordDetector.

──────────────────────────────────────────────────────────────────────────────
FILE 19: voice/listener.py
──────────────────────────────────────────────────────────────────────────────
STT with premium/free fallback.

Abstract: STTListener
- listen(timeout: float = 10) -> tuple[str, str]: Returns (text, detected_language)
- is_available() -> bool

Implementations:
- WhisperListener: Local Whisper (large-v3 or base based on settings)
- VoskListener: Lightweight offline alternative

Factory: create_listener() -> STTListener
- Auto-detect best available
- Lazy load models (on first use)

All must:
- Use sounddevice for audio capture
- Handle microphone errors gracefully
- Detect language (en/hi)
- Return empty string on failure (don't crash)

──────────────────────────────────────────────────────────────────────────────
FILE 20: voice/speaker.py
──────────────────────────────────────────────────────────────────────────────
TTS with premium/free fallback.

Abstract: TTSSpeaker
- speak(text: str, language: str = "en")
- speak_async(text: str, language: str = "en"): Non-blocking
- stop(): Stop current speech
- is_available() -> bool

Implementations:
- ElevenLabsSpeaker: Premium, Japanese-accented voice possible
- EdgeTTSSpeaker: Free, Microsoft neural voices
- Pyttsx3Speaker: Offline fallback

Factory: create_speaker() -> TTSSpeaker

Voice selection by language:
- English: Use configured voice (Ana, Sonia, etc.)
- Hindi: Switch to Hindi voice (Swara)
- Japanese elements: Already in text, voice handles naturally

──────────────────────────────────────────────────────────────────────────────
FILE 21: voice/wake_word.py
──────────────────────────────────────────────────────────────────────────────
Wake word / activation detection.

Abstract: WakeWordDetector
- start(): Begin listening
- stop(): Stop listening
- wait_for_activation() -> bool: Block until activated
- on_activation: Callback

Implementations:
- PicovoiceDetector: Custom "Hey Aara" wake word
- HotkeyDetector: Ctrl+Space using pynput

Factory: create_wake_detector() -> WakeWordDetector

──────────────────────────────────────────────────────────────────────────────
FILE 22: voice/audio_utils.py
──────────────────────────────────────────────────────────────────────────────
Audio helpers:
- record_audio(duration: float, sample_rate: int = 16000) -> np.ndarray
- play_audio(audio: np.ndarray, sample_rate: int = 16000)
- get_input_devices() -> list[dict]
- get_default_input_device() -> dict
- play_sound_file(path: str): Play wav/mp3 file

──────────────────────────────────────────────────────────────────────────────
FILE 23: system/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export AppLauncher, SystemControl, MediaControl, FileManager.

──────────────────────────────────────────────────────────────────────────────
FILE 24: system/app_launcher.py
──────────────────────────────────────────────────────────────────────────────
AppLauncher class:
- launch(app_name: str) -> tuple[bool, str]
- close(app_name: str) -> tuple[bool, str]
- is_running(app_name: str) -> bool
- get_running_apps() -> list[str]
- Load app_registry.yaml
- Fuzzy match app names
- Use subprocess.Popen for launch
- Use taskkill for close (Windows)

──────────────────────────────────────────────────────────────────────────────
FILE 25: system/system_control.py
──────────────────────────────────────────────────────────────────────────────
SystemControl class:
- set_volume(level: int): 0-100
- get_volume() -> int
- mute() / unmute()
- shutdown() / restart() / sleep() / lock()
- Use pycaw for volume on Windows
- Require confirmation for destructive actions

──────────────────────────────────────────────────────────────────────────────
FILE 26: system/media_control.py
──────────────────────────────────────────────────────────────────────────────
MediaControl class:
- play_pause()
- next_track()
- previous_track()
- Use pyautogui to send media keys
- open_spotify(query: str = None): Open Spotify, optionally search
- open_youtube(query: str = None): Open YouTube in browser

──────────────────────────────────────────────────────────────────────────────
FILE 27: system/file_manager.py
──────────────────────────────────────────────────────────────────────────────
FileManager class:
- open_folder(path: str)
- open_file(path: str)
- search_files(query: str, directory: str = None) -> list[str]
- get_recent_files() -> list[str]

──────────────────────────────────────────────────────────────────────────────
FILE 28: system/browser_control.py
──────────────────────────────────────────────────────────────────────────────
BrowserControl class:
- open_url(url: str)
- search_google(query: str)
- search_youtube(query: str)
- Use webbrowser module (simple, reliable)

──────────────────────────────────────────────────────────────────────────────
FILE 29: system/clipboard_manager.py
──────────────────────────────────────────────────────────────────────────────
ClipboardManager class:
- copy(text: str)
- paste() -> str
- Use pyperclip or PySide6 clipboard

──────────────────────────────────────────────────────────────────────────────
FILE 30: skills/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export BaseSkill, SkillRegistry, all skill classes.

──────────────────────────────────────────────────────────────────────────────
FILE 31: skills/base_skill.py
──────────────────────────────────────────────────────────────────────────────
Abstract BaseSkill class:
- name: str (property)
- description: str (property)
- keywords: list[str] (trigger words)
- execute(params: dict) -> str (abstract)
- can_handle(text: str) -> bool

──────────────────────────────────────────────────────────────────────────────
FILE 32: skills/skill_registry.py
──────────────────────────────────────────────────────────────────────────────
SkillRegistry class:
- register(skill: BaseSkill)
- find_skill(text: str) -> BaseSkill | None
- get_all_skills() -> list[BaseSkill]
- Auto-discover skills in skills/ folder

──────────────────────────────────────────────────────────────────────────────
FILE 33: skills/weather_skill.py
──────────────────────────────────────────────────────────────────────────────
WeatherSkill(BaseSkill):
- Premium: OpenWeatherMap API
- Free fallback: Open-Meteo (no key needed)
- get_weather(city: str) -> str
- Return natural language: "It's 25°C and sunny in Delhi, feels like 27°C"

──────────────────────────────────────────────────────────────────────────────
FILE 34: skills/search_skill.py
──────────────────────────────────────────────────────────────────────────────
SearchSkill(BaseSkill):
- Premium: Serper API (Google results)
- Free fallback: DuckDuckGo
- search(query: str, num_results: int = 3) -> str
- Return summarized results

──────────────────────────────────────────────────────────────────────────────
FILE 35: skills/timer_skill.py
──────────────────────────────────────────────────────────────────────────────
TimerSkill(BaseSkill):
- set_timer(duration: str) -> str: Parse "5 minutes", "1 hour 30 minutes"
- Use threading.Timer
- Play notification sound when done
- Track active timers

──────────────────────────────────────────────────────────────────────────────
FILE 36: skills/notes_skill.py
──────────────────────────────────────────────────────────────────────────────
NotesSkill(BaseSkill):
- add_note(content: str)
- get_notes() -> list[str]
- clear_notes()
- Store in JSON file: data/notes.json

──────────────────────────────────────────────────────────────────────────────
FILE 37: ui/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export MainWindow, CharacterWidget.

──────────────────────────────────────────────────────────────────────────────
FILE 38: ui/main_window.py
──────────────────────────────────────────────────────────────────────────────
MainWindow(QMainWindow):
- Frameless, transparent, always-on-top
- Contains CharacterWidget and ChatPanel
- System tray integration
- Draggable
- Context menu on right-click
- Handles all UI events

──────────────────────────────────────────────────────────────────────────────
FILE 39: ui/character_widget.py
──────────────────────────────────────────────────────────────────────────────
CharacterWidget(QWidget):
- Display animated character using QMovie (GIF support)
- set_emotion(emotion: str): Change animation based on emotion
- set_speaking(is_speaking: bool): Talking animation
- Smooth transitions between emotions
- Click to activate (alternative to wake word)

──────────────────────────────────────────────────────────────────────────────
FILE 40: ui/chat_panel.py
──────────────────────────────────────────────────────────────────────────────
ChatPanel(QWidget):
- Scrollable chat history
- User messages (right-aligned, blue)
- Aara messages (left-aligned, purple)
- Text input field at bottom
- Send button or Enter to submit
- Typing indicator when Aara is thinking

──────────────────────────────────────────────────────────────────────────────
FILE 41: ui/system_tray.py
──────────────────────────────────────────────────────────────────────────────
SystemTrayIcon(QSystemTrayIcon):
- Icon in system tray
- Menu: Show/Hide, Settings, Quit
- Double-click to show window
- Notification support

──────────────────────────────────────────────────────────────────────────────
FILE 42: ui/settings_dialog.py
──────────────────────────────────────────────────────────────────────────────
SettingsDialog(QDialog):
- Tabs: General, Voice, API Keys, About
- General: Theme, position, startup behavior
- Voice: TTS voice selection, STT model, wake word toggle
- API Keys: Input fields for all API keys (masked)
- Save settings to JSON file

──────────────────────────────────────────────────────────────────────────────
FILE 43: ui/assets/__init__.py
──────────────────────────────────────────────────────────────────────────────
Empty init file.

──────────────────────────────────────────────────────────────────────────────
FILE 44: ui/assets/resource_loader.py
──────────────────────────────────────────────────────────────────────────────
ResourceLoader class:
- get_image(name: str) -> QPixmap
- get_sound(name: str) -> str (path)
- get_theme(name: str) -> dict
- Handle missing resources gracefully

──────────────────────────────────────────────────────────────────────────────
FILE 45: utils/__init__.py
──────────────────────────────────────────────────────────────────────────────
Export get_logger, and common helpers.

──────────────────────────────────────────────────────────────────────────────
FILE 46: utils/logger.py
──────────────────────────────────────────────────────────────────────────────
Logging configuration:
- File handler: data/logs/aara.log (rotating, 5MB max, 3 backups)
- Console handler: colored output (colorama)
- get_logger(name: str) -> logging.Logger

──────────────────────────────────────────────────────────────────────────────
FILE 47: utils/helpers.py
──────────────────────────────────────────────────────────────────────────────
Common utilities:
- safe_json_loads(text: str) -> dict | None
- fuzzy_match(query: str, options: list[str], threshold: float = 0.6) -> str | None
- sanitize_for_speech(text: str) -> str: Remove markdown, URLs, etc.
- ensure_dir(path: str): Create directory if not exists
- get_data_dir() -> Path: Returns data/ directory path

──────────────────────────────────────────────────────────────────────────────
FILE 48: utils/async_utils.py
──────────────────────────────────────────────────────────────────────────────
Async/threading utilities:
- run_async(coro): Run async function from sync code
- run_in_thread(func, *args) -> Future
- debounce(wait: float): Decorator to debounce function calls
- ThreadSafeQueue: Queue with thread-safe put/get

──────────────────────────────────────────────────────────────────────────────
FILE 49: utils/text_processing.py
──────────────────────────────────────────────────────────────────────────────
Text processing:
- clean_text(text: str) -> str: Remove extra whitespace
- extract_urls(text: str) -> list[str]
- remove_markdown(text: str) -> str
- truncate(text: str, max_length: int) -> str

──────────────────────────────────────────────────────────────────────────────
FILE 50: assets/themes/dark.yaml
──────────────────────────────────────────────────────────────────────────────
Dark theme color scheme:
- background, foreground, primary, secondary, accent
- chat bubble colors, button colors

──────────────────────────────────────────────────────────────────────────────
FILE 51: assets/themes/light.yaml
──────────────────────────────────────────────────────────────────────────────
Light theme color scheme.

──────────────────────────────────────────────────────────────────────────────
FILE 52: main.py
──────────────────────────────────────────────────────────────────────────────
COMPLETE APPLICATION ENTRY POINT:

```python
"""
Aara - Anime Desktop Assistant
Main entry point
"""

# 1. Initialize logging first
# 2. Load settings
# 3. Create all components:
#    - Brain (LLM)
#    - Memory (short-term, long-term, user profile)
#    - Listener (STT)
#    - Speaker (TTS)
#    - WakeWordDetector
#    - CommandHandler
#    - SkillRegistry
# 4. Create Qt Application and MainWindow
# 5. Connect all signals/slots
# 6. Main loop:
#    - Wait for activation (wake word or hotkey)
#    - Listen for user speech
#    - Parse intent
#    - If COMMAND: execute and get result
#    - If CHAT/QUESTION: send to brain with history
#    - Extract emotion from response
#    - Update character emotion
#    - Speak response
#    - Add to memory
#    - Loop
# 7. Graceful shutdown on Ctrl+C or window close
```

Must include:
- Proper threading model (UI on main, voice on separate)
- Queue-based communication between threads
- Signal handlers for graceful shutdown
- Error recovery (don't crash on failures)
- Startup greeting from Aara
- Auto-create data directories

═══════════════════════════════════════════════════════════════════════════════
                         ADDITIONAL REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

CODE QUALITY:
- Type hints on ALL function signatures
- Docstrings on ALL public classes and methods (concise, one line)
- No magic strings — use constants
- Proper error handling everywhere
- Logging for all significant operations

THREADING:
- Qt UI MUST run on main thread
- All voice I/O on separate threads
- LLM calls on separate thread (don't block UI)
- Use Queue or Signal for cross-thread communication

ROBUSTNESS:
- Never crash — catch all exceptions at boundaries
- Always have fallbacks
- Log errors with full context
- Return sensible defaults on failure

═══════════════════════════════════════════════════════════════════════════════
                              BEGIN GENERATION
═══════════════════════════════════════════════════════════════════════════════

Generate ALL 52 files now, using the exact marker format specified.
Start with requirements.txt and proceed in order.
Each file must be COMPLETE and PRODUCTION-READY.

This is your ONE chance — make it perfect.
'''

# =============================================================================
#                         EXTRACTION SCRIPT
# =============================================================================

EXTRACTION_SCRIPT = '''
import re
from pathlib import Path

def extract_files_from_response(response_text: str, output_dir: str = "."):
    """
    Extract all files from Claude's response and save them.

    Usage:
        1. Save Claude's response to response.txt
        2. Run: python extract.py
    """
    # Pattern to match our file markers
    pattern = r'▼▼▼ FILE: (.+?) ▼▼▼\n(.*?)▲▲▲ END FILE ▲▲▲'

    matches = re.findall(pattern, response_text, re.DOTALL)

    if not matches:
        print("No files found! Make sure the response uses the correct markers.")
        print("Expected format:")
        print("▼▼▼ FILE: path/to/file.py ▼▼▼")
        print("<content>")
        print("▲▲▲ END FILE ▲▲▲")
        return

    output_path = Path(output_dir)
    created_files = []

    for filepath, content in matches:
        filepath = filepath.strip()
        content = content.strip()

        full_path = output_path / filepath

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        created_files.append(filepath)
        print(f"✓ {filepath}")

    print(f"\\n{'='*50}")
    print(f"Successfully extracted {len(created_files)} files!")
    print(f"{'='*50}")

    # Create data directories
    data_dirs = ['data/chromadb', 'data/logs', 'assets/images/character', 'assets/sounds']
    for d in data_dirs:
        (output_path / d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {d}")

if __name__ == "__main__":
    import sys

    # Read from file or stdin
    if len(sys.argv) > 1:
        response_file = sys.argv[1]
        with open(response_file, 'r', encoding='utf-8') as f:
            response = f.read()
    else:
        print("Paste Claude's response (press Ctrl+D or Ctrl+Z when done):")
        response = sys.stdin.read()

    extract_files_from_response(response)
'''

# =============================================================================
#                              PRINT INFO
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("   AARA - ULTIMATE ONE-SHOT MEGA PROMPT")
    print("=" * 80)
    print()
    print(f"   Prompt length: {len(MEGA_PROMPT):,} characters")
    print(f"   Files to generate: 52")
    print(f"   Ready for: Claude Opus 4.6 with Extended Thinking")
    print()
    print("=" * 80)
    print("   HOW TO USE:")
    print("=" * 80)
    print()
    print("   1. Copy the MEGA_PROMPT content (between the triple quotes)")
    print("   2. Go to Claude Opus 4.6 (with max output/extended thinking)")
    print("   3. Paste and submit")
    print("   4. Save Claude's response to: response.txt")
    print("   5. Run extraction: python MEGA_PROMPT.py response.txt")
    print()
    print("=" * 80)

    # Save extraction script separately for convenience
    with open("extract_files.py", "w", encoding="utf-8") as f:
        f.write(EXTRACTION_SCRIPT)
    print("   Also created: extract_files.py (for extracting generated code)")
    print("=" * 80)
