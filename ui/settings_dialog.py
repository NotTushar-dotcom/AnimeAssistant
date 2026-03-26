"""
Aara Settings Dialog
Configuration UI for application settings.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QFormLayout, QGroupBox, QSlider,
)
from PySide6.QtCore import Qt

from config.settings import SETTINGS, LLMProvider, TTSProvider, STTProvider

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Settings dialog."""

    def __init__(self, parent=None):
        """Initialize settings dialog."""
        super().__init__(parent)

        self.setWindowTitle("Aara Settings")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up UI."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self._create_general_tab()
        self._create_voice_tab()
        self._create_api_tab()
        self._create_about_tab()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_settings)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self._apply_style()

    def _apply_style(self) -> None:
        """Apply styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e4e;
                border-radius: 4px;
                background-color: #2e2e3e;
            }
            QTabBar::tab {
                background-color: #2e2e3e;
                color: #aaa;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3e3e4e;
                color: white;
            }
            QGroupBox {
                border: 1px solid #3e3e4e;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ddd;
            }
            QLineEdit, QComboBox {
                background-color: #3e3e4e;
                border: 1px solid #4e4e5e;
                border-radius: 4px;
                padding: 6px;
                color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #a855f7;
            }
            QCheckBox {
                color: #ddd;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QPushButton {
                background-color: #4e4e5e;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5e5e6e;
            }
            QPushButton#save_button {
                background-color: #a855f7;
            }
            QPushButton#save_button:hover {
                background-color: #9333ea;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background-color: #3e3e4e;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                margin: -5px 0;
                background-color: #a855f7;
                border-radius: 8px;
            }
        """)
        self.save_button.setObjectName("save_button")

    def _create_general_tab(self) -> None:
        """Create general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        appearance_layout.addRow("Theme:", self.theme_combo)

        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Bottom Right", "Bottom Left", "Top Right", "Top Left"
        ])
        appearance_layout.addRow("Window Position:", self.position_combo)

        layout.addWidget(appearance_group)

        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)

        self.start_minimized_check = QCheckBox("Start minimized to tray")
        behavior_layout.addRow(self.start_minimized_check)

        self.always_on_top_check = QCheckBox("Always on top")
        self.always_on_top_check.setChecked(True)
        behavior_layout.addRow(self.always_on_top_check)

        layout.addWidget(behavior_group)

        # User group
        user_group = QGroupBox("User")
        user_layout = QFormLayout(user_group)

        self.user_name_edit = QLineEdit()
        self.user_name_edit.setPlaceholderText("Your name")
        user_layout.addRow("Name:", self.user_name_edit)

        layout.addWidget(user_group)

        layout.addStretch()
        self.tabs.addTab(tab, "General")

    def _create_voice_tab(self) -> None:
        """Create voice settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # TTS group
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QFormLayout(tts_group)

        self.tts_provider_combo = QComboBox()
        self.tts_provider_combo.addItems(["ElevenLabs", "Edge TTS", "Pyttsx3"])
        tts_layout.addRow("Provider:", self.tts_provider_combo)

        self.tts_voice_combo = QComboBox()
        self.tts_voice_combo.addItems(["Ana (US)", "Sonia (UK)", "Aria (US)"])
        tts_layout.addRow("Voice:", self.tts_voice_combo)

        layout.addWidget(tts_group)

        # STT group
        stt_group = QGroupBox("Speech-to-Text")
        stt_layout = QFormLayout(stt_group)

        self.stt_provider_combo = QComboBox()
        self.stt_provider_combo.addItems(["Whisper Large", "Whisper Base", "Vosk"])
        stt_layout.addRow("Provider:", self.stt_provider_combo)

        layout.addWidget(stt_group)

        # Wake word group
        wake_group = QGroupBox("Activation")
        wake_layout = QFormLayout(wake_group)

        self.wake_combo = QComboBox()
        self.wake_combo.addItems(["Hotkey (Ctrl+Space)", "Picovoice Wake Word"])
        wake_layout.addRow("Method:", self.wake_combo)

        self.hotkey_edit = QLineEdit("ctrl+space")
        wake_layout.addRow("Hotkey:", self.hotkey_edit)

        layout.addWidget(wake_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Voice")

    def _create_api_tab(self) -> None:
        """Create API keys tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # LLM group
        llm_group = QGroupBox("LLM Provider")
        llm_layout = QFormLayout(llm_group)

        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems([
            "Anthropic Claude", "Groq (Free)", "Gemini (Free)", "Ollama (Local)"
        ])
        llm_layout.addRow("Provider:", self.llm_provider_combo)

        self.anthropic_key_edit = QLineEdit()
        self.anthropic_key_edit.setEchoMode(QLineEdit.Password)
        self.anthropic_key_edit.setPlaceholderText("sk-...")
        llm_layout.addRow("Anthropic API Key:", self.anthropic_key_edit)

        self.groq_key_edit = QLineEdit()
        self.groq_key_edit.setEchoMode(QLineEdit.Password)
        self.groq_key_edit.setPlaceholderText("gsk_...")
        llm_layout.addRow("Groq API Key:", self.groq_key_edit)

        layout.addWidget(llm_group)

        # Other APIs group
        other_group = QGroupBox("Other Services")
        other_layout = QFormLayout(other_group)

        self.elevenlabs_key_edit = QLineEdit()
        self.elevenlabs_key_edit.setEchoMode(QLineEdit.Password)
        other_layout.addRow("ElevenLabs Key:", self.elevenlabs_key_edit)

        self.serper_key_edit = QLineEdit()
        self.serper_key_edit.setEchoMode(QLineEdit.Password)
        other_layout.addRow("Serper Key:", self.serper_key_edit)

        layout.addWidget(other_group)

        layout.addStretch()
        self.tabs.addTab(tab, "API Keys")

    def _create_about_tab(self) -> None:
        """Create about tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Logo/title
        title_label = QLabel("Aara")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #a855f7;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Your Anime Desktop Assistant")
        subtitle_label.setStyleSheet("color: #888; font-size: 14px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Version
        version_label = QLabel("Version 0.1.0")
        version_label.setStyleSheet("color: #666; font-size: 12px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        layout.addStretch()

        # Credits
        credits_label = QLabel("Built with love for anime culture")
        credits_label.setStyleSheet("color: #555; font-size: 11px;")
        credits_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits_label)

        self.tabs.addTab(tab, "About")

    def _load_settings(self) -> None:
        """Load current settings into UI."""
        # General
        self.theme_combo.setCurrentText(SETTINGS.ui.theme.capitalize())
        position_map = {
            "bottom-right": "Bottom Right",
            "bottom-left": "Bottom Left",
            "top-right": "Top Right",
            "top-left": "Top Left",
        }
        self.position_combo.setCurrentText(
            position_map.get(SETTINGS.ui.window_position, "Bottom Right")
        )
        self.start_minimized_check.setChecked(SETTINGS.ui.start_minimized)
        self.user_name_edit.setText(SETTINGS.user_name)

        # Load API keys from env (masked)
        if SETTINGS.llm.anthropic_key:
            self.anthropic_key_edit.setText("*" * 20)
        if SETTINGS.llm.groq_key:
            self.groq_key_edit.setText("*" * 20)

    def _save_settings(self) -> None:
        """Save settings."""
        # Note: In a full implementation, this would write to .env or a config file
        logger.info("Settings saved (not persisted in this demo)")
        self.accept()
