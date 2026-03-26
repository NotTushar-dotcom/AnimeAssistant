"""
Aara System Tray Icon
System tray icon with menu.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtCore import Signal

logger = logging.getLogger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for Aara."""

    show_requested = Signal()
    hide_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        """Initialize system tray icon."""
        super().__init__(parent)

        self._setup_icon()
        self._setup_menu()
        self._setup_signals()

        self.show()
        logger.info("System tray icon initialized")

    def _setup_icon(self) -> None:
        """Set up tray icon."""
        # Try to load custom icon
        icon_path = Path("assets/images/icon.png")
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            # Create a simple colored icon
            pixmap = QPixmap(32, 32)
            pixmap.fill()  # Will be a default color

            # Try to draw a purple circle
            from PySide6.QtGui import QPainter, QColor, QBrush
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(168, 85, 247)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(2, 2, 28, 28)
            painter.end()

            self.setIcon(QIcon(pixmap))

        self.setToolTip("Aara - Desktop Assistant")

    def _setup_menu(self) -> None:
        """Set up context menu."""
        menu = QMenu()

        # Show/Hide
        self.show_action = QAction("Show Aara", self)
        self.show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(self.show_action)

        self.hide_action = QAction("Hide Aara", self)
        self.hide_action.triggered.connect(self.hide_requested.emit)
        menu.addAction(self.hide_action)

        menu.addSeparator()

        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _setup_signals(self) -> None:
        """Set up signal connections."""
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_requested.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - toggle
            self.show_requested.emit()

    def show_notification(
        self,
        title: str,
        message: str,
        duration: int = 3000
    ) -> None:
        """
        Show a system notification.

        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        if self.supportsMessages():
            self.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                duration
            )

    def update_window_visible(self, visible: bool) -> None:
        """Update menu items based on window visibility."""
        self.show_action.setVisible(not visible)
        self.hide_action.setVisible(visible)


# Need to import Qt for the pixmap drawing
from PySide6.QtCore import Qt
