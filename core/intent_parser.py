"""
Aara Intent Parser
Classifies user input into intents for routing.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

from core.personality import INTENT_CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents."""
    CHAT = "chat"
    COMMAND = "command"
    QUESTION = "question"
    SEARCH = "search"


class CommandType(Enum):
    """Types of commands."""
    APP_LAUNCH = "app_launch"
    APP_CLOSE = "app_close"
    VOLUME = "volume"
    MEDIA = "media"
    SYSTEM = "system"
    FILE = "file"
    TIMER = "timer"
    NOTES = "notes"
    WEATHER = "weather"
    SEARCH = "search"
    CLIPBOARD = "clipboard"


@dataclass
class Intent:
    """Parsed intent from user input."""
    type: IntentType = IntentType.CHAT
    language: str = "en"
    command_type: Optional[CommandType] = None
    target: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    raw_text: str = ""
    confidence: float = 1.0


class IntentParser:
    """Parses user input to determine intent."""

    # Pattern-based quick detection for common commands
    QUICK_PATTERNS = {
        # App commands
        r"^(open|launch|start|run)\s+(.+)$": (IntentType.COMMAND, CommandType.APP_LAUNCH),
        r"^(close|quit|exit|kill)\s+(.+)$": (IntentType.COMMAND, CommandType.APP_CLOSE),
        # Volume commands
        r"^(volume\s+up|increase\s+volume|louder)": (IntentType.COMMAND, CommandType.VOLUME),
        r"^(volume\s+down|decrease\s+volume|quieter)": (IntentType.COMMAND, CommandType.VOLUME),
        r"^(mute|unmute)": (IntentType.COMMAND, CommandType.VOLUME),
        r"^(set\s+)?volume\s+(to\s+)?(\d+)": (IntentType.COMMAND, CommandType.VOLUME),
        # Media commands
        r"^(play|pause|resume|stop\s+playing)$": (IntentType.COMMAND, CommandType.MEDIA),
        r"^(next|skip|next\s+track)$": (IntentType.COMMAND, CommandType.MEDIA),
        r"^(previous|prev|back|previous\s+track)$": (IntentType.COMMAND, CommandType.MEDIA),
        # System commands
        r"^(shutdown|shut\s+down|turn\s+off)": (IntentType.COMMAND, CommandType.SYSTEM),
        r"^(restart|reboot)": (IntentType.COMMAND, CommandType.SYSTEM),
        r"^(sleep|hibernate)": (IntentType.COMMAND, CommandType.SYSTEM),
        r"^(lock|lock\s+screen)": (IntentType.COMMAND, CommandType.SYSTEM),
        # Weather
        r"(weather|temperature|forecast)": (IntentType.COMMAND, CommandType.WEATHER),
        # Timer
        r"^(set\s+(a\s+)?timer|timer\s+for)": (IntentType.COMMAND, CommandType.TIMER),
        # Notes
        r"^(take\s+a\s+note|note\s+|remember\s+)": (IntentType.COMMAND, CommandType.NOTES),
        r"^(read|show|list)\s+(my\s+)?notes": (IntentType.COMMAND, CommandType.NOTES),
        # Search
        r"^(search|google|look\s+up|find)\s+(for\s+)?(.+)$": (IntentType.SEARCH, CommandType.SEARCH),
    }

    def __init__(self, brain=None):
        """
        Initialize parser.

        Args:
            brain: Optional LLM brain for complex parsing
        """
        self.brain = brain

    def parse(self, text: str, use_llm: bool = False) -> Intent:
        """
        Parse user input to determine intent.

        Args:
            text: User input text
            use_llm: Whether to use LLM for complex parsing

        Returns:
            Parsed Intent object
        """
        text = text.strip()
        if not text:
            return Intent(type=IntentType.CHAT, raw_text=text)

        # Try quick pattern matching first
        intent = self._quick_parse(text)
        if intent.type != IntentType.CHAT or intent.command_type is not None:
            return intent

        # Use LLM for complex parsing if available
        if use_llm and self.brain:
            try:
                return self._llm_parse(text)
            except Exception as e:
                logger.warning(f"LLM parsing failed: {e}, falling back to pattern matching")

        # Default to chat
        return Intent(
            type=IntentType.CHAT,
            language=self._detect_language(text),
            raw_text=text,
        )

    def _quick_parse(self, text: str) -> Intent:
        """Quick pattern-based parsing."""
        text_lower = text.lower()

        for pattern, (intent_type, command_type) in self.QUICK_PATTERNS.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                target = None
                params = {}

                # Extract target/parameters based on command type
                if command_type == CommandType.APP_LAUNCH:
                    target = match.group(2).strip()
                elif command_type == CommandType.APP_CLOSE:
                    target = match.group(2).strip()
                elif command_type == CommandType.VOLUME:
                    vol_match = re.search(r"(\d+)", text_lower)
                    if vol_match:
                        params["level"] = int(vol_match.group(1))
                    elif "up" in text_lower or "increase" in text_lower or "louder" in text_lower:
                        params["action"] = "up"
                    elif "down" in text_lower or "decrease" in text_lower or "quieter" in text_lower:
                        params["action"] = "down"
                    elif "mute" in text_lower:
                        params["action"] = "unmute" if "unmute" in text_lower else "mute"
                elif command_type == CommandType.MEDIA:
                    if any(w in text_lower for w in ["play", "resume"]):
                        params["action"] = "play"
                    elif "pause" in text_lower or "stop" in text_lower:
                        params["action"] = "pause"
                    elif any(w in text_lower for w in ["next", "skip"]):
                        params["action"] = "next"
                    elif any(w in text_lower for w in ["previous", "prev", "back"]):
                        params["action"] = "previous"
                elif command_type == CommandType.SYSTEM:
                    if "shutdown" in text_lower or "turn off" in text_lower:
                        params["action"] = "shutdown"
                    elif "restart" in text_lower or "reboot" in text_lower:
                        params["action"] = "restart"
                    elif "sleep" in text_lower or "hibernate" in text_lower:
                        params["action"] = "sleep"
                    elif "lock" in text_lower:
                        params["action"] = "lock"
                elif command_type == CommandType.SEARCH:
                    target = match.group(3).strip() if match.lastindex >= 3 else text
                elif command_type == CommandType.WEATHER:
                    city_match = re.search(r"(?:in|at|for)\s+(\w+(?:\s+\w+)?)", text_lower)
                    if city_match:
                        target = city_match.group(1)
                elif command_type == CommandType.TIMER:
                    duration_match = re.search(
                        r"(\d+)\s*(second|minute|hour|min|sec|hr)s?",
                        text_lower
                    )
                    if duration_match:
                        params["duration"] = duration_match.group(0)
                elif command_type == CommandType.NOTES:
                    note_match = re.search(r"(?:note|remember)\s+(.+)$", text_lower)
                    if note_match:
                        params["content"] = note_match.group(1)
                        params["action"] = "add"
                    elif "read" in text_lower or "show" in text_lower or "list" in text_lower:
                        params["action"] = "list"

                return Intent(
                    type=intent_type,
                    language=self._detect_language(text),
                    command_type=command_type,
                    target=target,
                    parameters=params,
                    raw_text=text,
                )

        return Intent(type=IntentType.CHAT, raw_text=text, language=self._detect_language(text))

    def _llm_parse(self, text: str) -> Intent:
        """Use LLM for complex intent parsing."""
        prompt = INTENT_CLASSIFICATION_PROMPT.format(message=text)
        response = self.brain.chat([{"role": "user", "content": prompt}])

        # Extract JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")

            intent_type = IntentType(data.get("intent", "chat").lower())
            command_type = None
            if data.get("command_type"):
                try:
                    command_type = CommandType(data["command_type"])
                except ValueError:
                    pass

            return Intent(
                type=intent_type,
                language=data.get("language", "en"),
                command_type=command_type,
                target=data.get("target"),
                parameters=data.get("parameters", {}),
                raw_text=text,
            )
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise

    def _detect_language(self, text: str) -> str:
        """Simple language detection (English vs Hindi)."""
        # Hindi Unicode block range
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.replace(" ", ""))

        if total_chars > 0 and hindi_chars / total_chars > 0.3:
            return "hi"
        return "en"
