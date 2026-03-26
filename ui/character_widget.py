"""
Aara Character Widget
Animated character display using GIF animations.
"""

import logging
from pathlib import Path
from typing import Optional, Dict

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QMovie, QPixmap

logger = logging.getLogger(__name__)


class CharacterWidget(QWidget):
    """Displays animated character with emotion states."""

    clicked = Signal()

    # Emotion to animation mapping
    ANIMATION_MAP = {
        "happy": "happy.gif",
        "excited": "excited.gif",
        "sad": "sad.gif",
        "thinking": "thinking.gif",
        "idle": "idle.gif",
        "talking": "talking.gif",
        "shy": "shy.gif",
        "surprised": "surprised.gif",
        "playful": "playful.gif",
        "concerned": "concerned.gif",
        "worried": "worried.gif",
        "determined": "determined.gif",
        "curious": "curious.gif",
        "proud": "proud.gif",
        "relaxed": "idle.gif",
        "focused": "thinking.gif",
    }

    def __init__(self):
        """Initialize character widget."""
        super().__init__()

        self._current_emotion = "idle"
        self._is_speaking = False
        self._animations: Dict[str, QMovie] = {}
        self._current_movie: Optional[QMovie] = None

        self._setup_ui()
        self._load_animations()
        self.set_emotion("idle")

    def _setup_ui(self) -> None:
        """Set up UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)

        # Animation label
        self.animation_label = QLabel()
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setMinimumSize(200, 200)
        self.animation_label.setMaximumSize(280, 280)
        self.animation_label.setScaledContents(True)
        self.animation_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.animation_label)

        # Name label
        self.name_label = QLabel("Aara")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #a855f7;
                font-size: 16px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.name_label)

    def _load_animations(self) -> None:
        """Load animation files."""
        assets_dir = Path("assets/images/character")

        for emotion, filename in self.ANIMATION_MAP.items():
            filepath = assets_dir / filename
            if filepath.exists():
                try:
                    movie = QMovie(str(filepath))
                    movie.setScaledSize(QSize(250, 250))
                    self._animations[emotion] = movie
                    logger.debug(f"Loaded animation: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load animation {filename}: {e}")
            else:
                logger.debug(f"Animation not found: {filepath}")

        # If no animations loaded, create placeholder
        if not self._animations:
            logger.warning("No animations found, using placeholder")
            self._create_placeholder()

    def _create_placeholder(self) -> None:
        """Create a placeholder when no animations available."""
        # Create a simple colored label
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        self.animation_label.setPixmap(pixmap)
        self.animation_label.setStyleSheet("""
            QLabel {
                background-color: rgba(168, 85, 247, 100);
                border-radius: 125px;
                border: 3px solid #a855f7;
            }
        """)

    def set_emotion(self, emotion: str) -> None:
        """
        Set character emotion and update animation.

        Args:
            emotion: Emotion name
        """
        emotion = emotion.lower()
        self._current_emotion = emotion

        # If speaking, use talking animation
        if self._is_speaking and "talking" in self._animations:
            emotion = "talking"

        # Get animation (with fallback to idle)
        animation_key = emotion if emotion in self._animations else "idle"
        movie = self._animations.get(animation_key)

        if movie:
            if self._current_movie:
                self._current_movie.stop()

            self._current_movie = movie
            self.animation_label.setMovie(movie)
            movie.start()
            logger.debug(f"Set emotion: {emotion}")
        else:
            logger.warning(f"No animation for emotion: {emotion}")

    def set_speaking(self, is_speaking: bool) -> None:
        """
        Set speaking state.

        Args:
            is_speaking: Whether character is speaking
        """
        self._is_speaking = is_speaking
        if is_speaking:
            self.set_emotion("talking")
        else:
            self.set_emotion(self._current_emotion)

    def get_emotion(self) -> str:
        """Get current emotion."""
        return self._current_emotion

    def mousePressEvent(self, event) -> None:
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        """Handle mouse enter."""
        # Slight scale up effect could be added here
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        super().leaveEvent(event)
