"""
Aara Skill Registry
Manages skill discovery and registration.
"""

import logging
from typing import Optional, List, Dict, Type

from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for managing skills."""

    def __init__(self):
        """Initialize skill registry."""
        self._skills: Dict[str, BaseSkill] = {}
        self._auto_register()

    def _auto_register(self) -> None:
        """Auto-register built-in skills."""
        try:
            from skills.weather_skill import WeatherSkill
            from skills.search_skill import SearchSkill
            from skills.timer_skill import TimerSkill
            from skills.notes_skill import NotesSkill

            self.register(WeatherSkill())
            self.register(SearchSkill())
            self.register(TimerSkill())
            self.register(NotesSkill())

            logger.info(f"Registered {len(self._skills)} skills")
        except Exception as e:
            logger.error(f"Failed to auto-register skills: {e}")

    def register(self, skill: BaseSkill) -> None:
        """
        Register a skill.

        Args:
            skill: Skill instance to register
        """
        self._skills[skill.name.lower()] = skill
        logger.debug(f"Registered skill: {skill.name}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a skill.

        Args:
            name: Skill name

        Returns:
            True if skill was removed
        """
        name_lower = name.lower()
        if name_lower in self._skills:
            del self._skills[name_lower]
            return True
        return False

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """
        Get a skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance or None
        """
        return self._skills.get(name.lower())

    def find_skill(self, text: str) -> Optional[BaseSkill]:
        """
        Find a skill that can handle the given text.

        Args:
            text: User input text

        Returns:
            Matching skill or None
        """
        text_lower = text.lower()

        # Check each skill's keywords
        for skill in self._skills.values():
            if skill.can_handle(text_lower):
                logger.debug(f"Found skill for '{text[:30]}...': {skill.name}")
                return skill

        return None

    def get_all_skills(self) -> List[BaseSkill]:
        """Get all registered skills."""
        return list(self._skills.values())

    def get_skill_names(self) -> List[str]:
        """Get names of all registered skills."""
        return list(self._skills.keys())

    def execute_skill(self, name: str, params: dict) -> Optional[str]:
        """
        Execute a skill by name.

        Args:
            name: Skill name
            params: Parameters for the skill

        Returns:
            Result message or None if skill not found
        """
        skill = self.get_skill(name)
        if skill:
            try:
                return skill.execute(params)
            except Exception as e:
                logger.error(f"Skill execution error: {e}")
                return f"Error executing {name}: {str(e)}"
        return None

    def get_help(self) -> str:
        """Get help text for all skills."""
        lines = ["Available skills:"]
        for skill in self._skills.values():
            lines.append(f"  - {skill.get_help()}")
        return "\n".join(lines)
