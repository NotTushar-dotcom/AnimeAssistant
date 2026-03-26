"""
Aara Clipboard Manager
Read and write to system clipboard.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ClipboardManager:
    """Manages clipboard operations."""

    def __init__(self):
        """Initialize clipboard manager."""
        self._backend = None
        self._init_backend()

    def _init_backend(self) -> None:
        """Initialize clipboard backend."""
        # Try pyperclip first
        try:
            import pyperclip
            self._backend = "pyperclip"
            self._pyperclip = pyperclip
            logger.info("Clipboard initialized (pyperclip)")
            return
        except ImportError:
            pass

        # Try PySide6/Qt clipboard
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QClipboard
            self._backend = "qt"
            logger.info("Clipboard initialized (Qt)")
            return
        except ImportError:
            pass

        # Fallback to win32clipboard
        try:
            import win32clipboard
            self._backend = "win32"
            self._win32 = win32clipboard
            logger.info("Clipboard initialized (win32)")
            return
        except ImportError:
            pass

        logger.warning("No clipboard backend available")

    def copy(self, text: str) -> bool:
        """
        Copy text to clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful
        """
        try:
            if self._backend == "pyperclip":
                self._pyperclip.copy(text)
                logger.debug(f"Copied to clipboard: {text[:50]}...")
                return True

            elif self._backend == "qt":
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.clipboard().setText(text)
                    return True
                return False

            elif self._backend == "win32":
                self._win32.OpenClipboard()
                try:
                    self._win32.EmptyClipboard()
                    self._win32.SetClipboardText(text)
                finally:
                    self._win32.CloseClipboard()
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False

    def paste(self) -> Optional[str]:
        """
        Get text from clipboard.

        Returns:
            Clipboard text or None
        """
        try:
            if self._backend == "pyperclip":
                return self._pyperclip.paste()

            elif self._backend == "qt":
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    return app.clipboard().text()
                return None

            elif self._backend == "win32":
                self._win32.OpenClipboard()
                try:
                    data = self._win32.GetClipboardData()
                    return data
                finally:
                    self._win32.CloseClipboard()

            return None

        except Exception as e:
            logger.error(f"Failed to read clipboard: {e}")
            return None

    def clear(self) -> bool:
        """
        Clear the clipboard.

        Returns:
            True if successful
        """
        try:
            return self.copy("")
        except Exception:
            return False

    def has_text(self) -> bool:
        """
        Check if clipboard has text.

        Returns:
            True if clipboard contains text
        """
        text = self.paste()
        return text is not None and len(text) > 0

    def get_length(self) -> int:
        """
        Get length of clipboard text.

        Returns:
            Length of clipboard content
        """
        text = self.paste()
        return len(text) if text else 0
