"""
Aara Search Skill
Web search using DuckDuckGo (free) or Serper (premium).
"""

import logging
from typing import List

from skills.base_skill import BaseSkill
from config.settings import SETTINGS, SearchProvider

logger = logging.getLogger(__name__)


class SearchSkill(BaseSkill):
    """Provides web search functionality."""

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Search the web for information"

    @property
    def keywords(self) -> List[str]:
        return ["search", "google", "find", "look up", "what is", "who is", "how to"]

    def __init__(self):
        """Initialize search skill."""
        self._provider = SETTINGS.search.provider
        self._serper_key = SETTINGS.search.serper_key
        self._max_results = SETTINGS.search.max_results

    def execute(self, params: dict) -> str:
        """
        Search the web.

        Args:
            params: {"query": "search query"}

        Returns:
            Search results summary
        """
        query = params.get("query", "")
        if not query:
            return "What would you like me to search for?"

        if self._provider == SearchProvider.SERPER and self._serper_key:
            return self._search_serper(query)
        else:
            return self._search_duckduckgo(query)

    def _search_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo (free)."""
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self._max_results))

            if not results:
                return f"I couldn't find any results for '{query}'."

            # Format results
            response_parts = [f"Here's what I found for '{query}':\n"]

            for i, result in enumerate(results[:3], 1):
                title = result.get("title", "No title")
                body = result.get("body", "")
                href = result.get("href", "")

                # Truncate body
                if len(body) > 150:
                    body = body[:150] + "..."

                response_parts.append(f"{i}. **{title}**")
                response_parts.append(f"   {body}")

            return "\n".join(response_parts)

        except ImportError:
            logger.error("DuckDuckGo search not available. Run: pip install duckduckgo-search")
            return "Web search is not available right now."
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return f"I had trouble searching for '{query}'. Try again?"

    def _search_serper(self, query: str) -> str:
        """Search using Serper API (Google results)."""
        try:
            import requests

            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self._serper_key,
                "Content-Type": "application/json",
            }
            payload = {"q": query, "num": self._max_results}

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()

            organic = data.get("organic", [])
            if not organic:
                return f"I couldn't find any results for '{query}'."

            # Format results
            response_parts = [f"Here's what I found for '{query}':\n"]

            for i, result in enumerate(organic[:3], 1):
                title = result.get("title", "No title")
                snippet = result.get("snippet", "")

                if len(snippet) > 150:
                    snippet = snippet[:150] + "..."

                response_parts.append(f"{i}. **{title}**")
                response_parts.append(f"   {snippet}")

            # Include answer box if available
            if data.get("answerBox"):
                answer = data["answerBox"].get("answer") or data["answerBox"].get("snippet")
                if answer:
                    response_parts.insert(1, f"\n**Quick Answer:** {answer}\n")

            return "\n".join(response_parts)

        except Exception as e:
            logger.error(f"Serper search error: {e}")
            # Fall back to DuckDuckGo
            return self._search_duckduckgo(query)
