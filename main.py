"""
Aara - Anime Desktop Assistant
Main Application Entry Point

A warm, caring AI assistant with a Japanese-inspired personality,
voice interaction, and desktop control capabilities.
"""

import sys
import signal
import logging
from pathlib import Path
from queue import Queue
from threading import Thread, Event
from typing import Optional

# Set up paths
sys.path.insert(0, str(Path(__file__).parent))

# Initialize logging early
from utils.logger import setup_logging, get_logger
setup_logging(log_level="INFO")
logger = get_logger(__name__)

# Qt imports
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal, QObject

# Config and core
from config.settings import SETTINGS
from core.brain import create_brain, LLMBrain
from core.personality import extract_emotion_tag, get_greeting_response
from core.intent_parser import IntentParser, Intent, IntentType
from core.command_handler import CommandHandler
from core.emotion_detector import EmotionDetector
from core.memory import ShortTermMemory, LongTermMemory, UserProfile

# Voice
from voice.listener import create_listener, STTListener
from voice.speaker import create_speaker, TTSSpeaker
from voice.wake_word import create_wake_detector, WakeWordDetector

# Skills
from skills.skill_registry import SkillRegistry

# UI
from ui.main_window import MainWindow
from ui.system_tray import SystemTrayIcon


class VoiceWorker(QObject):
    """Background worker for voice processing."""

    text_received = Signal(str, str)  # (text, language)
    listening_started = Signal()
    listening_stopped = Signal()
    error_occurred = Signal(str)

    def __init__(self, listener: STTListener, wake_detector: WakeWordDetector):
        super().__init__()
        self._listener = listener
        self._wake_detector = wake_detector
        self._running = False
        self._activated = Event()

    def start_listening(self) -> None:
        """Start listening mode."""
        self._running = True
        self._run_listen_loop()

    def stop_listening(self) -> None:
        """Stop listening."""
        self._running = False
        self._wake_detector.stop()

    def activate(self) -> None:
        """Manually activate listening."""
        self._activated.set()

    def _run_listen_loop(self) -> None:
        """Main listening loop."""
        logger.info("Voice worker starting...")

        # Set up wake detector callback
        def on_activation():
            self._activated.set()

        self._wake_detector.on_activation = on_activation
        self._wake_detector.start()

        while self._running:
            try:
                # Wait for activation
                logger.debug("Waiting for activation...")
                self._activated.wait()
                self._activated.clear()

                if not self._running:
                    break

                # Emit listening started
                self.listening_started.emit()

                # Listen for speech
                text, language = self._listener.listen(timeout=10.0)

                # Emit listening stopped
                self.listening_stopped.emit()

                if text:
                    self.text_received.emit(text, language)
                else:
                    logger.debug("No speech detected")

                # Restart wake detector
                self._wake_detector.start()

            except Exception as e:
                logger.error(f"Voice worker error: {e}")
                self.error_occurred.emit(str(e))


class AaraApplication:
    """Main Aara application."""

    def __init__(self):
        """Initialize application."""
        logger.info("=" * 60)
        logger.info("   AARA - Anime Desktop Assistant")
        logger.info("=" * 60)

        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Aara")

        # Initialize components
        self._init_components()
        self._init_ui()
        self._connect_signals()

        logger.info("Application initialized successfully")

    def _init_components(self) -> None:
        """Initialize core components."""
        logger.info("Initializing components...")

        # Brain (LLM)
        logger.info("Creating brain...")
        self.brain = create_brain()
        logger.info(f"Brain ready: {self.brain.get_provider_name()}")

        # Memory systems
        logger.info("Initializing memory...")
        self.short_term_memory = ShortTermMemory(max_turns=20)
        self.long_term_memory = LongTermMemory()
        self.user_profile = UserProfile()

        # Intent parser and command handler
        self.intent_parser = IntentParser(brain=self.brain)
        self.command_handler = CommandHandler()
        self.emotion_detector = EmotionDetector()

        # Skills
        logger.info("Loading skills...")
        self.skill_registry = SkillRegistry()

        # Voice components
        logger.info("Initializing voice...")
        self.listener = create_listener()
        self.speaker = create_speaker()
        self.wake_detector = create_wake_detector()
        logger.info(f"STT: {self.listener.get_provider_name()}")
        logger.info(f"TTS: {self.speaker.get_provider_name()}")

        # Message queue for thread-safe communication
        self.message_queue = Queue()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        logger.info("Initializing UI...")

        # Main window
        self.window = MainWindow()

        # System tray
        self.tray_icon = SystemTrayIcon()

        # Voice worker thread
        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker(self.listener, self.wake_detector)
        self.voice_worker.moveToThread(self.voice_thread)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Window signals
        self.window.message_submitted.connect(self._on_user_message)
        self.window.activation_requested.connect(self._on_activation)

        # Tray icon signals
        self.tray_icon.show_requested.connect(self.window.show)
        self.tray_icon.hide_requested.connect(self.window.hide)
        self.tray_icon.settings_requested.connect(self._open_settings)
        self.tray_icon.quit_requested.connect(self._quit)

        # Voice worker signals
        self.voice_worker.text_received.connect(self._on_voice_input)
        self.voice_worker.listening_started.connect(
            lambda: self.window.set_listening(True)
        )
        self.voice_worker.listening_stopped.connect(
            lambda: self.window.set_listening(False)
        )

        # Thread signals
        self.voice_thread.started.connect(self.voice_worker.start_listening)

    def run(self) -> int:
        """Run the application."""
        logger.info("Starting Aara...")

        # Show window
        if not SETTINGS.ui.start_minimized:
            self.window.show()

        # Greet user
        self._greet_user()

        # Start voice thread
        self.voice_thread.start()

        # Set up signal handlers
        signal.signal(signal.SIGINT, lambda *args: self._quit())
        signal.signal(signal.SIGTERM, lambda *args: self._quit())

        logger.info("Aara is ready!")

        # Run event loop
        return self.app.exec()

    def _greet_user(self) -> None:
        """Send initial greeting."""
        user_name = self.user_profile.get_name() or SETTINGS.user_name
        greeting = get_greeting_response(user_name)

        clean_text, emotion = extract_emotion_tag(greeting)

        self.window.add_message("aara", clean_text, emotion)
        self.speaker.speak_async(clean_text)

    def _on_user_message(self, text: str) -> None:
        """Handle user text input."""
        logger.info(f"User message: {text}")
        self._process_input(text, "en")

    def _on_voice_input(self, text: str, language: str) -> None:
        """Handle voice input."""
        logger.info(f"Voice input: {text} (lang: {language})")
        self._process_input(text, language)

    def _on_activation(self) -> None:
        """Handle activation request."""
        logger.debug("Activation requested")
        self.voice_worker.activate()

    def _process_input(self, text: str, language: str) -> None:
        """Process user input."""
        # Add to chat
        self.window.add_message("user", text)

        # Show thinking state
        self.window.set_thinking(True)

        # Process in background thread
        Thread(
            target=self._process_input_async,
            args=(text, language),
            daemon=True
        ).start()

    def _process_input_async(self, text: str, language: str) -> None:
        """Process input asynchronously."""
        try:
            # Parse intent
            intent = self.intent_parser.parse(text)
            logger.debug(f"Intent: {intent.type.value}")

            response = ""

            if intent.type == IntentType.COMMAND and intent.command_type:
                # Execute command
                result = self.command_handler.execute(intent)
                if result.requires_confirmation:
                    response = result.message
                else:
                    # Generate conversational response about the command
                    self.short_term_memory.add_user_message(text)
                    messages = self.short_term_memory.get_for_llm()
                    messages.append({
                        "role": "user",
                        "content": f"I just asked you to: {text}\nThe command result was: {result.message}\nPlease respond naturally and include an emotion tag."
                    })
                    response = self.brain.chat(messages)

            else:
                # Chat with brain
                self.short_term_memory.add_user_message(text)

                # Add context from long-term memory
                context = self.long_term_memory.get_relevant_context(text)
                if context:
                    messages = [{
                        "role": "user",
                        "content": f"Context from memory:\n{context}"
                    }]
                    messages.extend(self.short_term_memory.get_for_llm())
                else:
                    messages = self.short_term_memory.get_for_llm()

                response = self.brain.chat(messages)

            # Extract emotion and clean text
            clean_text, emotion = extract_emotion_tag(response)

            # Store response in memory
            self.short_term_memory.add_assistant_message(clean_text, emotion)

            # Update UI (thread-safe via signal)
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                self.window,
                "set_thinking",
                Qt.QueuedConnection,
                Q_ARG(bool, False)
            )
            QMetaObject.invokeMethod(
                self.window,
                "add_message",
                Qt.QueuedConnection,
                Q_ARG(str, "aara"),
                Q_ARG(str, clean_text),
            )
            QMetaObject.invokeMethod(
                self.window,
                "set_emotion",
                Qt.QueuedConnection,
                Q_ARG(str, emotion)
            )

            # Speak response
            from utils.helpers import sanitize_for_speech
            speech_text = sanitize_for_speech(clean_text)
            self.speaker.speak(speech_text, language)

            # Record stats
            self.user_profile.increment_stat("messages_sent")

        except Exception as e:
            logger.error(f"Error processing input: {e}", exc_info=True)
            # Show error to user
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                self.window,
                "set_thinking",
                Qt.QueuedConnection,
                Q_ARG(bool, False)
            )
            QMetaObject.invokeMethod(
                self.window,
                "add_message",
                Qt.QueuedConnection,
                Q_ARG(str, "aara"),
                Q_ARG(str, f"Gomen! I had a problem: {str(e)[:100]}"),
            )

    def _open_settings(self) -> None:
        """Open settings dialog."""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.window)
        dialog.exec()

    def _quit(self) -> None:
        """Quit the application."""
        logger.info("Shutting down...")

        # Stop voice worker
        self.voice_worker.stop_listening()
        self.voice_thread.quit()
        self.voice_thread.wait(2000)

        # Clean up
        from utils.async_utils import cleanup_executor
        cleanup_executor()

        # Quit app
        self.app.quit()


def main():
    """Main entry point."""
    try:
        # Ensure data directories exist
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        Path("data/chromadb").mkdir(parents=True, exist_ok=True)
        Path("assets/images/character").mkdir(parents=True, exist_ok=True)
        Path("assets/sounds").mkdir(parents=True, exist_ok=True)
        Path("assets/themes").mkdir(parents=True, exist_ok=True)

        # Run application
        app = AaraApplication()
        sys.exit(app.run())

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
