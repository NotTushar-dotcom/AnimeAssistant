"""
Aara Resource Loader
Loads images, sounds, and themes.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from PySide6.QtGui import QPixmap, QIcon

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Loads and caches resources."""

    _instance = None
    _images: Dict[str, QPixmap] = {}
    _sounds: Dict[str, str] = {}
    _themes: Dict[str, dict] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize resource loader."""
        if self._initialized:
            return

        self.assets_dir = Path("assets")
        self.images_dir = self.assets_dir / "images"
        self.sounds_dir = self.assets_dir / "sounds"
        self.themes_dir = self.assets_dir / "themes"

        self._initialized = True
        logger.info("Resource loader initialized")

    def get_image(self, name: str) -> Optional[QPixmap]:
        """
        Get an image by name.

        Args:
            name: Image name (with or without extension)

        Returns:
            QPixmap or None
        """
        if name in self._images:
            return self._images[name]

        # Try to find the image
        for ext in [".png", ".jpg", ".gif", ""]:
            path = self.images_dir / f"{name}{ext}"
            if path.exists():
                try:
                    pixmap = QPixmap(str(path))
                    self._images[name] = pixmap
                    logger.debug(f"Loaded image: {name}")
                    return pixmap
                except Exception as e:
                    logger.error(f"Failed to load image {name}: {e}")
                    break

        logger.warning(f"Image not found: {name}")
        return None

    def get_icon(self, name: str) -> Optional[QIcon]:
        """
        Get an icon by name.

        Args:
            name: Icon name

        Returns:
            QIcon or None
        """
        pixmap = self.get_image(name)
        if pixmap:
            return QIcon(pixmap)
        return None

    def get_sound(self, name: str) -> Optional[str]:
        """
        Get a sound file path by name.

        Args:
            name: Sound name (with or without extension)

        Returns:
            Path string or None
        """
        if name in self._sounds:
            return self._sounds[name]

        for ext in [".wav", ".mp3", ""]:
            path = self.sounds_dir / f"{name}{ext}"
            if path.exists():
                path_str = str(path)
                self._sounds[name] = path_str
                logger.debug(f"Found sound: {name}")
                return path_str

        logger.warning(f"Sound not found: {name}")
        return None

    def get_theme(self, name: str) -> dict:
        """
        Get a theme by name.

        Args:
            name: Theme name ("dark" or "light")

        Returns:
            Theme dict
        """
        if name in self._themes:
            return self._themes[name]

        path = self.themes_dir / f"{name}.yaml"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    theme = yaml.safe_load(f) or {}
                    self._themes[name] = theme
                    logger.debug(f"Loaded theme: {name}")
                    return theme
            except Exception as e:
                logger.error(f"Failed to load theme {name}: {e}")

        # Return default theme
        return self._get_default_theme()

    def _get_default_theme(self) -> dict:
        """Get default theme."""
        return {
            "background": "#1e1e2e",
            "foreground": "#ffffff",
            "primary": "#a855f7",
            "secondary": "#6366f1",
            "accent": "#ec4899",
            "surface": "#2e2e3e",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "chat": {
                "user_bubble": "#3b82f6",
                "assistant_bubble": "#a855f7",
            }
        }

    def get_character_animation(self, emotion: str) -> Optional[str]:
        """
        Get character animation path for emotion.

        Args:
            emotion: Emotion name

        Returns:
            Path string or None
        """
        character_dir = self.images_dir / "character"

        for ext in [".gif", ".png"]:
            path = character_dir / f"{emotion}{ext}"
            if path.exists():
                return str(path)

        # Fallback to idle
        idle_path = character_dir / "idle.gif"
        if idle_path.exists():
            return str(idle_path)

        return None

    def ensure_directories(self) -> None:
        """Create asset directories if they don't exist."""
        directories = [
            self.assets_dir,
            self.images_dir,
            self.images_dir / "character",
            self.sounds_dir,
            self.themes_dir,
        ]

        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info("Asset directories ensured")


# Global instance
resources = ResourceLoader()
