"""
Aara Browser Control
Web browser automation and URL handling.
"""

import logging
import webbrowser
from typing import Tuple
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class BrowserControl:
    """Controls web browser operations."""

    def __init__(self):
        """Initialize browser control."""
        self._default_browser = None
        self._detect_browser()

    def _detect_browser(self) -> None:
        """Detect the default browser."""
        try:
            self._default_browser = webbrowser.get()
            logger.info("Browser control initialized")
        except Exception as e:
            logger.warning(f"Could not detect default browser: {e}")

    def open_url(self, url: str) -> Tuple[bool, str]:
        """
        Open a URL in the default browser.

        Args:
            url: URL to open

        Returns:
            Tuple of (success, message)
        """
        # Add protocol if missing
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return True, f"Opening {url}"
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            return False, "Failed to open URL"

    def search_google(self, query: str) -> Tuple[bool, str]:
        """
        Search Google for a query.

        Args:
            query: Search query

        Returns:
            Tuple of (success, message)
        """
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        try:
            webbrowser.open(url)
            logger.info(f"Google search: {query}")
            return True, f"Searching Google for '{query}'"
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return False, "Failed to search"

    def search_youtube(self, query: str) -> Tuple[bool, str]:
        """
        Search YouTube for a query.

        Args:
            query: Search query

        Returns:
            Tuple of (success, message)
        """
        encoded_query = quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"

        try:
            webbrowser.open(url)
            logger.info(f"YouTube search: {query}")
            return True, f"Searching YouTube for '{query}'"
        except Exception as e:
            logger.error(f"Failed to search YouTube: {e}")
            return False, "Failed to search YouTube"

    def search_duckduckgo(self, query: str) -> Tuple[bool, str]:
        """
        Search DuckDuckGo for a query.

        Args:
            query: Search query

        Returns:
            Tuple of (success, message)
        """
        encoded_query = quote_plus(query)
        url = f"https://duckduckgo.com/?q={encoded_query}"

        try:
            webbrowser.open(url)
            logger.info(f"DuckDuckGo search: {query}")
            return True, f"Searching DuckDuckGo for '{query}'"
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return False, "Failed to search"

    def open_gmail(self) -> Tuple[bool, str]:
        """Open Gmail."""
        return self.open_url("https://mail.google.com")

    def open_github(self, repo: str = None) -> Tuple[bool, str]:
        """
        Open GitHub, optionally to a specific repo.

        Args:
            repo: Repository in format "owner/repo"

        Returns:
            Tuple of (success, message)
        """
        if repo:
            return self.open_url(f"https://github.com/{repo}")
        return self.open_url("https://github.com")

    def open_chatgpt(self) -> Tuple[bool, str]:
        """Open ChatGPT."""
        return self.open_url("https://chat.openai.com")

    def open_claude(self) -> Tuple[bool, str]:
        """Open Claude AI."""
        return self.open_url("https://claude.ai")

    def open_maps(self, location: str = None) -> Tuple[bool, str]:
        """
        Open Google Maps, optionally to a location.

        Args:
            location: Location to search for

        Returns:
            Tuple of (success, message)
        """
        if location:
            encoded = quote_plus(location)
            url = f"https://www.google.com/maps/search/{encoded}"
        else:
            url = "https://www.google.com/maps"

        return self.open_url(url)

    def open_weather(self, city: str = None) -> Tuple[bool, str]:
        """
        Open weather information.

        Args:
            city: City name

        Returns:
            Tuple of (success, message)
        """
        if city:
            query = f"weather {city}"
        else:
            query = "weather"

        return self.search_google(query)
