"""
Aara Main Window
Main application window with frameless, transparent design.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QApplication, QMenu,
)
from PySide6.QtCore import Qt, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction

from config.settings import SETTINGS
from ui.character_widget import CharacterWidget
from ui.chat_panel import ChatPanel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    message_submitted = Signal(str)
    activation_requested = Signal()

    def __init__(self):
        """Initialize main window."""
        super().__init__()

        self._dragging = False
        self._drag_position = QPoint()
        self._chat_visible = False

        self._setup_window()
        self._setup_ui()
        self._setup_context_menu()
        self._position_window()

        logger.info("Main window initialized")

    def _setup_window(self) -> None:
        """Configure window properties."""
        # Frameless, transparent, always on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # Don't show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Size
        self.setFixedSize(300, 400)

    def _setup_ui(self) -> None:
        """Set up UI components."""
        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Character widget
        self.character_widget = CharacterWidget()
        self.character_widget.clicked.connect(self._on_character_clicked)
        layout.addWidget(self.character_widget, 1)

        # Chat panel (hidden by default)
        self.chat_panel = ChatPanel()
        self.chat_panel.message_submitted.connect(self.message_submitted.emit)
        self.chat_panel.setVisible(False)
        layout.addWidget(self.chat_panel, 2)

        # Status indicator
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                padding: 4px 8px;
                border-radius: 10px;
                font-size: 11px;
            }
        """)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

    def _setup_context_menu(self) -> None:
        """Set up right-click context menu."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _position_window(self) -> None:
        """Position window based on settings."""
        screen = QApplication.primaryScreen()
        if not screen:
            return

        screen_geo = screen.availableGeometry()
        position = SETTINGS.ui.window_position

        if position == "bottom-right":
            x = screen_geo.right() - self.width() - 20
            y = screen_geo.bottom() - self.height() - 20
        elif position == "bottom-left":
            x = screen_geo.left() + 20
            y = screen_geo.bottom() - self.height() - 20
        elif position == "top-right":
            x = screen_geo.right() - self.width() - 20
            y = screen_geo.top() + 20
        elif position == "top-left":
            x = screen_geo.left() + 20
            y = screen_geo.top() + 20
        else:  # center
            x = screen_geo.center().x() - self.width() // 2
            y = screen_geo.center().y() - self.height() // 2

        self.move(x, y)

    def _show_context_menu(self, pos: QPoint) -> None:
        """Show context menu."""
        menu = QMenu(self)

        # Toggle chat
        chat_action = QAction(
            "Hide Chat" if self._chat_visible else "Show Chat",
            self
        )
        chat_action.triggered.connect(self.toggle_chat)
        menu.addAction(chat_action)

        menu.addSeparator()

        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec_(self.mapToGlobal(pos))

    def _on_character_clicked(self) -> None:
        """Handle character click."""
        self.activation_requested.emit()

    def _open_settings(self) -> None:
        """Open settings dialog."""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()

    # Public methods

    def toggle_chat(self) -> None:
        """Toggle chat panel visibility."""
        self._chat_visible = not self._chat_visible
        self.chat_panel.setVisible(self._chat_visible)

        # Resize window
        if self._chat_visible:
            self.setFixedSize(350, 600)
        else:
            self.setFixedSize(300, 400)

        # Reposition
        self._position_window()

    def show_chat(self) -> None:
        """Show chat panel."""
        if not self._chat_visible:
            self.toggle_chat()

    def hide_chat(self) -> None:
        """Hide chat panel."""
        if self._chat_visible:
            self.toggle_chat()

    def set_emotion(self, emotion: str) -> None:
        """Set character emotion."""
        self.character_widget.set_emotion(emotion)

    def set_speaking(self, is_speaking: bool) -> None:
        """Set speaking state."""
        self.character_widget.set_speaking(is_speaking)

    def add_message(self, sender: str, text: str, emotion: Optional[str] = None) -> None:
        """Add message to chat panel."""
        self.chat_panel.add_message(sender, text)
        if emotion:
            self.set_emotion(emotion)

    def set_status(self, text: str) -> None:
        """Show status message."""
        if text:
            self.status_label.setText(text)
            self.status_label.setVisible(True)
        else:
            self.status_label.setVisible(False)

    def set_listening(self, is_listening: bool) -> None:
        """Set listening state."""
        if is_listening:
            self.set_status("Listening...")
            self.character_widget.set_emotion("curious")
        else:
            self.set_status("")

    def set_thinking(self, is_thinking: bool) -> None:
        """Set thinking state."""
        if is_thinking:
            self.set_status("Thinking...")
            self.character_widget.set_emotion("thinking")
        else:
            self.set_status("")

    # Mouse events for dragging

    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move."""
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release."""
        self._dragging = False
