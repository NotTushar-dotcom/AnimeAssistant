"""
Aara Base Skill
Abstract base class for all skills.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseSkill(ABC):
    """Abstract base class for skills."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Skill description."""
        pass

    @property
    @abstractmethod
    def keywords(self) -> List[str]:
        """Trigger keywords for this skill."""
        pass

    @abstractmethod
    def execute(self, params: dict) -> str:
        """
        Execute the skill.

        Args:
            params: Parameters for the skill

        Returns:
            Result message
        """
        pass

    def can_handle(self, text: str) -> bool:
        """
        Check if this skill can handle the given text.

        Args:
            text: User input text

        Returns:
            True if skill can handle
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def get_help(self) -> str:
        """Get help text for this skill."""
        return f"{self.name}: {self.description}"
