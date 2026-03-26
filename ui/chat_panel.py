"""
Aara Chat Panel
Conversation display with message bubbles.
"""

import logging
from typing import Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, Signal

logger = logging.getLogger(__name__)


class MessageBubble(QFrame):
    """A single message bubble."""

    def __init__(self, sender: str, text: str, is_user: bool = False):
        """Initialize message bubble."""
        super().__init__()

        self._setup_ui(sender, text, is_user)

    def _setup_ui(self, sender: str, text: str, is_user: bool) -> None:
        """Set up UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        # Message text
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(message_label)

        # Time label
        time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        time_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 10px;")
        layout.addWidget(time_label)

        # Style based on sender
        if is_user:
            self.setStyleSheet("""
                MessageBubble {
                    background-color: rgba(59, 130, 246, 200);
                    border-radius: 12px;
                    border-bottom-right-radius: 4px;
                }
                QLabel {
                    color: white;
                    font-size: 13px;
                }
            """)
        else:
            self.setStyleSheet("""
                MessageBubble {
                    background-color: rgba(168, 85, 247, 200);
                    border-radius: 12px;
                    border-bottom-left-radius: 4px;
                }
                QLabel {
                    color: white;
                    font-size: 13px;
                }
            """)


class ChatPanel(QWidget):
    """Chat conversation panel."""

    message_submitted = Signal(str)

    def __init__(self):
        """Initialize chat panel."""
        super().__init__()

        self._setup_ui()
        self._setup_style()

    def _setup_ui(self) -> None:
        """Set up UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Messages scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Messages container
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(4, 4, 4, 4)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area, 1)

        # Typing indicator
        self.typing_indicator = QLabel("Aara is typing...")
        self.typing_indicator.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 11px;
                font-style: italic;
                padding-left: 8px;
            }
        """)
        self.typing_indicator.setVisible(False)
        layout.addWidget(self.typing_indicator)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self._submit_message)
        input_layout.addWidget(self.input_field, 1)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._submit_message)
        self.send_button.setCursor(Qt.PointingHandCursor)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def _setup_style(self) -> None:
        """Set up styles."""
        self.setStyleSheet("""
            ChatPanel {
                background-color: rgba(30, 30, 40, 220);
                border-radius: 12px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                padding: 8px 16px;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #a855f7;
            }
            QPushButton {
                background-color: #a855f7;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9333ea;
            }
            QPushButton:pressed {
                background-color: #7c3aed;
            }
        """)

    def _submit_message(self) -> None:
        """Submit the current message."""
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.message_submitted.emit(text)

    def add_message(self, sender: str, text: str) -> None:
        """
        Add a message to the chat.

        Args:
            sender: Message sender ("user" or "aara")
            text: Message text
        """
        is_user = sender.lower() == "user"

        # Create bubble
        bubble = MessageBubble(sender, text, is_user)

        # Wrap in alignment container
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()

        # Add to messages layout (before the stretch)
        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1,
            container
        )

        # Scroll to bottom
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        """Scroll chat to bottom."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_typing(self, show: bool = True) -> None:
        """Show/hide typing indicator."""
        self.typing_indicator.setVisible(show)

    def clear_messages(self) -> None:
        """Clear all messages."""
        # Remove all widgets except the stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_input_enabled(self, enabled: bool) -> None:
        """Enable/disable input."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    def focus_input(self) -> None:
        """Focus the input field."""
        self.input_field.setFocus()
