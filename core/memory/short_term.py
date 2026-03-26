"""
Aara Short-Term Memory
Manages conversation buffer for context window.
"""

import logging
from threading import Lock
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    emotion: Optional[str] = None


class ShortTermMemory:
    """Manages short-term conversation memory with thread-safe operations."""

    def __init__(self, max_turns: int = 20):
        """
        Initialize short-term memory.

        Args:
            max_turns: Maximum number of conversation turns to keep
        """
        self.max_turns = max_turns
        self._messages: list[Message] = []
        self._lock = Lock()
        logger.info(f"Initialized short-term memory with max_turns={max_turns}")

    def add_message(self, role: str, content: str, emotion: Optional[str] = None) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            emotion: Optional emotion tag for assistant messages
        """
        with self._lock:
            message = Message(
                role=role,
                content=content,
                timestamp=datetime.now(),
                emotion=emotion,
            )
            self._messages.append(message)
            self._trim()
            logger.debug(f"Added message from {role}: {content[:50]}...")

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.add_message("user", content)

    def add_assistant_message(self, content: str, emotion: Optional[str] = None) -> None:
        """Add an assistant message."""
        self.add_message("assistant", content, emotion)

    def get_history(self, max_turns: Optional[int] = None) -> list[Message]:
        """
        Get conversation history.

        Args:
            max_turns: Optional limit on turns to return

        Returns:
            List of Message objects
        """
        with self._lock:
            if max_turns is None:
                return self._messages.copy()
            # Calculate how many messages to return (2 per turn: user + assistant)
            num_messages = max_turns * 2
            return self._messages[-num_messages:].copy()

    def get_for_llm(self, max_turns: Optional[int] = None) -> list[dict]:
        """
        Get history formatted for LLM API calls.

        Args:
            max_turns: Optional limit on turns to return

        Returns:
            List of dicts with "role" and "content" keys
        """
        messages = self.get_history(max_turns)
        return [{"role": m.role, "content": m.content} for m in messages]

    def get_last_message(self, role: Optional[str] = None) -> Optional[Message]:
        """
        Get the last message, optionally filtered by role.

        Args:
            role: Optional role filter ("user" or "assistant")

        Returns:
            Last Message or None
        """
        with self._lock:
            if not self._messages:
                return None
            if role is None:
                return self._messages[-1]
            for msg in reversed(self._messages):
                if msg.role == role:
                    return msg
            return None

    def get_last_user_message(self) -> Optional[str]:
        """Get the content of the last user message."""
        msg = self.get_last_message("user")
        return msg.content if msg else None

    def get_last_assistant_message(self) -> Optional[str]:
        """Get the content of the last assistant message."""
        msg = self.get_last_message("assistant")
        return msg.content if msg else None

    def clear(self) -> None:
        """Clear all messages from memory."""
        with self._lock:
            self._messages.clear()
            logger.info("Short-term memory cleared")

    def _trim(self) -> None:
        """Trim messages to max_turns (called within lock)."""
        max_messages = self.max_turns * 2
        if len(self._messages) > max_messages:
            excess = len(self._messages) - max_messages
            self._messages = self._messages[excess:]
            logger.debug(f"Trimmed {excess} messages from memory")

    def get_summary(self) -> dict:
        """Get memory statistics."""
        with self._lock:
            return {
                "total_messages": len(self._messages),
                "max_turns": self.max_turns,
                "user_messages": sum(1 for m in self._messages if m.role == "user"),
                "assistant_messages": sum(1 for m in self._messages if m.role == "assistant"),
            }

    def __len__(self) -> int:
        """Return number of messages."""
        with self._lock:
            return len(self._messages)

    def __bool__(self) -> bool:
        """Return True if there are any messages."""
        with self._lock:
            return len(self._messages) > 0
