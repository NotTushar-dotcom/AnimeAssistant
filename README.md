# Aara - Anime Desktop Assistant

> *"Your personal anime companion that lives on your desktop"*

An AI-powered anime assistant with a Japanese-accented English voice, emotional expressions, and full system control capabilities. Built with Claude Opus 4.6 for intelligence, ElevenLabs for voice, and Live2D for anime character animation.

---

## Tech Stack (Best-of-Best)

| Component | Technology | Status |
|-----------|------------|--------|
| **LLM Brain** | Claude Opus 4.6 | Pending |
| **Speech-to-Text** | OpenAI Whisper `large-v3` | Pending |
| **Text-to-Speech** | ElevenLabs (Japanese accent) | Pending |
| **Wake Word** | Picovoice Porcupine | Pending |
| **Character** | Live2D Cubism SDK | Pending |
| **GUI Framework** | PySide6 + OpenGL | Partial |
| **Memory** | SQLite + ChromaDB | Pending |
| **System Control** | PyAutoGUI + subprocess | Pending |

---

## Development Checklist

### Phase 1: Foundation (Week 1)

#### Core Brain Setup
- [ ] Create `.env` file with API keys structure
- [ ] Install Anthropic SDK (`pip install anthropic`)
- [ ] Implement `core/brain.py` - Claude Opus 4.6 integration
- [ ] Implement streaming responses for real-time output
- [ ] Test basic prompt-response flow
- [ ] Implement `core/intent_parser.py` - classify CHAT vs COMMAND vs SEARCH

#### System Prompt & Personality
- [x] Create `core/personality.py` with Aara's system prompt
- [x] Define emotion tags and Live2D mapping
- [x] Create intent classification prompt
- [ ] Test personality consistency across multiple conversations
- [ ] Fine-tune Japanese speech patterns (not too heavy, not too light)

#### Basic System Control
- [ ] Implement `core/command_handler.py` - route commands to appropriate modules
- [ ] Create `config/app_registry.yaml` - map app names to paths
- [ ] Implement `system/app_launcher.py` - open/close applications
- [ ] Implement `system/system_control.py` - volume, brightness, shutdown
- [ ] Implement `system/file_manager.py` - basic file operations
- [ ] Test system commands work reliably

---

### Phase 2: Voice System (Week 2)

#### Speech-to-Text (Whisper)
- [ ] Install Whisper dependencies (`pip install openai-whisper`)
- [ ] Implement `voice/listener.py` - microphone input capture
- [ ] Configure Whisper `large-v3` model loading
- [ ] Implement language auto-detection (English/Hindi)
- [ ] Create `voice/language_detector.py` - pass language to TTS
- [ ] Test STT accuracy with different accents
- [ ] Implement noise filtering/VAD (Voice Activity Detection)

#### Text-to-Speech (ElevenLabs)
- [ ] Install ElevenLabs SDK (`pip install elevenlabs`)
- [ ] Create/select Japanese-accented English voice on ElevenLabs
- [ ] Create/select matching Hindi voice on ElevenLabs
- [ ] Store voice IDs in `voice/voice_profiles/`
- [ ] Implement `voice/speaker.py` - text to audio playback
- [ ] Implement audio streaming (speak while generating)
- [ ] Test voice quality and accent consistency
- [ ] Add voice speed/pitch controls in settings

#### Wake Word Detection
- [ ] Sign up for Picovoice account (free tier)
- [ ] Create custom "Hey Aara" wake word model
- [ ] Download `.ppn` file for wake word
- [ ] Implement `voice/wake_word.py` - always-on listening
- [ ] Test wake word detection accuracy
- [ ] Handle false positives gracefully
- [ ] Add wake word sensitivity settings

---

### Phase 3: GUI & Character (Week 3-4)

#### Main Application Window
- [x] Create basic PySide6 frameless window
- [x] Implement transparent background
- [x] Add window dragging functionality
- [x] Position in bottom-right by default
- [ ] Implement `ui/system_tray.py` - tray icon with menu
- [ ] Add context menu (right-click on character)
- [ ] Implement `ui/hotkey_listener.py` - global Ctrl+Space trigger
- [ ] Create `ui/settings_window.py` - configuration UI

#### Chat Panel
- [ ] Implement `ui/chat_panel.py` - conversation display
- [ ] Add text input field for typed commands
- [ ] Style chat bubbles (user vs Aara)
- [ ] Implement chat history scrolling
- [ ] Add typing indicator animation
- [ ] Support markdown rendering in responses

#### Animation System Upgrade
- [x] Basic GIF animation working
- [ ] Research Live2D Cubism SDK for Python
- [ ] Implement `ui/character/live2d_widget.py` - OpenGL renderer
- [ ] Load Live2D model files (`.moc3`, `.model3.json`)
- [ ] Create `ui/character/emotion_controller.py` - map emotions to expressions
- [ ] Implement smooth expression transitions
- [ ] Add idle animations (breathing, blinking)
- [ ] Add lip-sync during speech (advanced)

---

### Phase 4: Memory System (Week 5)

#### Short-Term Memory
- [ ] Implement `core/memory/short_term.py` - conversation buffer
- [ ] Store last 20 conversation turns
- [ ] Implement context window management
- [ ] Pass conversation history to Claude

#### Long-Term Memory (ChromaDB)
- [ ] Install ChromaDB (`pip install chromadb`)
- [ ] Implement `core/memory/long_term.py` - semantic memory
- [ ] Create embedding function for memories
- [ ] Store user preferences and facts
- [ ] Implement memory retrieval based on relevance
- [ ] Add memory decay/importance scoring

#### User Profile
- [ ] Implement `core/memory/user_profile.py` - persistent user data
- [ ] Store: name, preferences, frequently used apps
- [ ] Track user patterns (work schedule, habits)
- [ ] Allow user to view/edit stored information

---

### Phase 5: Skills & Integrations (Week 6)

#### Skill Framework
- [ ] Create `skills/base_skill.py` - standard skill interface
- [ ] Implement skill registration system
- [ ] Add skill discovery/loading mechanism

#### Media Control
- [ ] Implement `skills/spotify_skill.py` - Spotify control
- [ ] Implement `skills/youtube_skill.py` - YouTube playback
- [ ] Implement `system/media_control.py` - play/pause/skip
- [ ] Add volume control for media

#### Utility Skills
- [ ] Implement `skills/weather_skill.py` - OpenWeatherMap API
- [ ] Implement `skills/web_search_skill.py` - Tavily/Serper API
- [ ] Implement `skills/notes_skill.py` - quick note taking
- [ ] Implement `skills/reminder_skill.py` - scheduled reminders
- [ ] Implement `system/clipboard_manager.py` - read/write clipboard

#### Browser Control
- [ ] Implement `system/browser_control.py` - Selenium integration
- [ ] Add website opening capability
- [ ] Add search query execution
- [ ] Add tab management

---

### Phase 6: Polish & Quality (Week 7)

#### Performance Optimization
- [ ] Profile application startup time
- [ ] Optimize Whisper model loading (lazy load)
- [ ] Implement response caching where appropriate
- [ ] Reduce memory footprint
- [ ] Test CPU/GPU usage during operation

#### User Experience
- [ ] Add startup animation/greeting
- [ ] Implement "Focus Mode" - reduced interruptions
- [ ] Add notification sounds (`assets/sounds/`)
- [ ] Create dark/light/ themes (`assets/themes/`)
- [ ] Add first-time setup wizard
- [ ] Implement error recovery and graceful fallbacks

#### Testing & Stability
- [ ] Write unit tests for core modules
- [ ] Test on different Windows versions
- [ ] Test with various microphone setups
- [ ] Handle network disconnection gracefully
- [ ] Add comprehensive logging (`utils/logger.py`)
- [ ] Create error reporting mechanism

#### Documentation
- [ ] Write API key setup guide
- [ ] Document all available commands
- [ ] Create troubleshooting guide
- [ ] Add contribution guidelines

---

## Required API Keys

Create a `.env` file in the project root:

```env
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
PICOVOICE_ACCESS_KEY=your_picovoice_key_here

# Optional (for extra features)
OPENWEATHERMAP_API_KEY=your_weather_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

### Where to get API keys:
1. **Anthropic (Claude)**: [console.anthropic.com](https://console.anthropic.com)
2. **ElevenLabs**: [elevenlabs.io](https://elevenlabs.io)
3. **Picovoice**: [picovoice.ai](https://picovoice.ai) (free tier available)
4. **OpenWeatherMap**: [openweathermap.org/api](https://openweathermap.org/api)
5. **Serper**: [serper.dev](https://serper.dev)

---

## Project Structure

```
AnimeAssistant/
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env                           # API keys (DO NOT COMMIT)
├── README.md                      # This file
│
├── core/                          # Core intelligence
│   ├── __init__.py
│   ├── brain.py                   # Claude Opus 4.6 integration
│   ├── personality.py             # Aara's system prompt & emotions [DONE]
│   ├── intent_parser.py           # Intent classification
│   ├── command_handler.py         # Command routing
│   ├── emotion_detector.py        # Emotion extraction from responses
│   └── memory/
│       ├── short_term.py          # Conversation buffer
│       ├── long_term.py           # ChromaDB semantic memory
│       └── user_profile.py        # Persistent user data
│
├── voice/                         # Voice I/O
│   ├── listener.py                # Whisper STT
│   ├── speaker.py                 # ElevenLabs TTS
│   ├── wake_word.py               # Porcupine "Hey Aara"
│   ├── language_detector.py       # English/Hindi detection
│   └── voice_profiles/            # ElevenLabs voice IDs
│       ├── english_voice_id.txt
│       └── hindi_voice_id.txt
│
├── system/                        # System control
│   ├── app_launcher.py            # Open/close applications
│   ├── system_control.py          # Volume, brightness, power
│   ├── file_manager.py            # File operations
│   ├── browser_control.py         # Web browser automation
│   ├── media_control.py           # Spotify, YouTube, etc.
│   └── clipboard_manager.py       # Clipboard read/write
│
├── ui/                            # User interface
│   ├── __init__.py
│   ├── display.py                 # Main window [PARTIAL]
│   ├── animation_manager.py       # Animation control
│   ├── chat_panel.py              # Conversation display
│   ├── system_tray.py             # Tray icon
│   ├── settings_window.py         # Settings UI
│   ├── hotkey_listener.py         # Global hotkeys
│   └── character/
│       ├── live2d_widget.py       # Live2D OpenGL renderer
│       ├── emotion_controller.py  # Emotion → expression mapping
│       └── models/                # Live2D model files
│           └── aara/
│               ├── aara.moc3
│               ├── aara.model3.json
│               └── textures/
│
├── skills/                        # Plugin skills
│   ├── base_skill.py              # Skill interface
│   ├── spotify_skill.py
│   ├── youtube_skill.py
│   ├── weather_skill.py
│   ├── web_search_skill.py
│   ├── notes_skill.py
│   └── reminder_skill.py
│
├── config/                        # Configuration
│   ├── __init__.py
│   ├── settings.py                # Application settings
│   ├── commands.py                # Command definitions
│   └── app_registry.yaml          # App name → path mapping
│
├── assets/                        # Media files
│   ├── videos/                    # GIF animations
│   ├── audio/                     # Sound effects
│   ├── images/                    # Static images
│   ├── sounds/                    # UI sounds
│   └── themes/                    # Color themes
│
├── logs/                          # Application logs
│   └── app.log
│
└── utils/                         # Utilities
    ├── logger.py                  # Logging configuration
    └── helpers.py                 # Helper functions
```

---

## Quick Start

```bash
# 1. Clone the repository
cd AnimeAssistant

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your .env file with API keys

# 5. Run the application
python main.py
```

---

## Current Status

**Phase**: Early Development (Phase 1 in progress)

**What works now:**
- Basic desktop window with animated character
- Character can be dragged around the screen
- Stays on top of other windows
- Transparent background

**Next milestone:**
- Claude Opus 4.6 integration for conversation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
│              (Voice via Mic OR Hotkey + Type)                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Wake Word Detection                         │
│                      (Picovoice Porcupine)                       │
│                        "Hey Aara" → Activate                     │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Speech-to-Text (Whisper)                     │
│                    Audio → Text + Language Tag                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Intent Classification                       │
│                  (Claude) CHAT | COMMAND | SEARCH                │
└─────────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Chat Handler   │  │Command Router│  │  Search/Skills   │
│ (Claude + Memory)│  │(System Ctrl) │  │  (Web + APIs)    │
└──────────────────┘  └──────────────┘  └──────────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Response + Emotion Tag [happy]                      │
│                    (From Claude)                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────┐            ┌────────────────────────────┐
│    Text-to-Speech     │            │    Emotion Controller      │
│     (ElevenLabs)      │            │   emotion → Live2D param   │
│ Japanese accent voice │            │   Update avatar expression │
└───────────────────────┘            └────────────────────────────┘
            │                                     │
            ▼                                     ▼
┌───────────────────────┐            ┌────────────────────────────┐
│    Audio Output       │            │    Live2D Animation        │
│     (Speakers)        │            │   (Character reacts)       │
└───────────────────────┘            └────────────────────────────┘
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built with love for anime culture and productivity*
