"""
Aara Media Control
Play/pause, next/previous, and media app integration.
"""

import logging
import webbrowser
from typing import Tuple

logger = logging.getLogger(__name__)


class MediaControl:
    """Controls media playback using system media keys."""

    def __init__(self):
        """Initialize media control."""
        self._pyautogui_available = False
        self._init_pyautogui()

    def _init_pyautogui(self) -> None:
        """Initialize PyAutoGUI."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            self._pyautogui = pyautogui
            self._pyautogui_available = True
            logger.info("Media control initialized (pyautogui)")
        except ImportError:
            logger.warning("PyAutoGUI not installed. Run: pip install pyautogui")

    def play_pause(self) -> Tuple[bool, str]:
        """Toggle play/pause."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("playpause")
                logger.info("Play/Pause toggled")
                return True, "Toggled play/pause"
            except Exception as e:
                logger.error(f"Failed to toggle play/pause: {e}")
                return False, "Failed to control media"
        return False, "Media control not available"

    def next_track(self) -> Tuple[bool, str]:
        """Skip to next track."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("nexttrack")
                logger.info("Skipped to next track")
                return True, "Skipping to next track"
            except Exception as e:
                logger.error(f"Failed to skip track: {e}")
                return False, "Failed to skip track"
        return False, "Media control not available"

    def previous_track(self) -> Tuple[bool, str]:
        """Go to previous track."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("prevtrack")
                logger.info("Went to previous track")
                return True, "Going to previous track"
            except Exception as e:
                logger.error(f"Failed to go to previous track: {e}")
                return False, "Failed to go to previous track"
        return False, "Media control not available"

    def stop(self) -> Tuple[bool, str]:
        """Stop playback."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("stop")
                logger.info("Playback stopped")
                return True, "Stopped playback"
            except Exception as e:
                logger.error(f"Failed to stop: {e}")
                return False, "Failed to stop playback"
        return False, "Media control not available"

    def volume_up(self) -> Tuple[bool, str]:
        """Increase media volume."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("volumeup")
                return True, "Volume increased"
            except Exception as e:
                logger.error(f"Failed to increase volume: {e}")
        return False, "Failed to increase volume"

    def volume_down(self) -> Tuple[bool, str]:
        """Decrease media volume."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("volumedown")
                return True, "Volume decreased"
            except Exception as e:
                logger.error(f"Failed to decrease volume: {e}")
        return False, "Failed to decrease volume"

    def mute(self) -> Tuple[bool, str]:
        """Toggle mute."""
        if self._pyautogui_available:
            try:
                self._pyautogui.press("volumemute")
                return True, "Toggled mute"
            except Exception as e:
                logger.error(f"Failed to mute: {e}")
        return False, "Failed to mute"

    def open_spotify(self, query: str = None) -> Tuple[bool, str]:
        """
        Open Spotify, optionally with a search query.

        Args:
            query: Optional search query

        Returns:
            Tuple of (success, message)
        """
        try:
            if query:
                # Open Spotify search
                url = f"spotify:search:{query.replace(' ', '%20')}"
                webbrowser.open(url)
                return True, f"Opening Spotify search for '{query}'"
            else:
                # Just open Spotify
                webbrowser.open("spotify:")
                return True, "Opening Spotify"
        except Exception as e:
            logger.error(f"Failed to open Spotify: {e}")
            return False, "Failed to open Spotify"

    def open_youtube(self, query: str = None) -> Tuple[bool, str]:
        """
        Open YouTube, optionally with a search query.

        Args:
            query: Optional search query

        Returns:
            Tuple of (success, message)
        """
        try:
            if query:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(url)
                return True, f"Opening YouTube search for '{query}'"
            else:
                webbrowser.open("https://www.youtube.com")
                return True, "Opening YouTube"
        except Exception as e:
            logger.error(f"Failed to open YouTube: {e}")
            return False, "Failed to open YouTube"

    def play_on_youtube(self, query: str) -> Tuple[bool, str]:
        """
        Search and play first result on YouTube.

        Args:
            query: Search query

        Returns:
            Tuple of (success, message)
        """
        # For now, just open search results
        # Could use yt-dlp or selenium for more advanced control
        return self.open_youtube(query)
