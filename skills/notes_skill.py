"""
Aara Notes Skill
Quick note taking and retrieval.
"""

import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from skills.base_skill import BaseSkill
from config.settings import SETTINGS

logger = logging.getLogger(__name__)


class NotesSkill(BaseSkill):
    """Manages quick notes."""

    @property
    def name(self) -> str:
        return "notes"

    @property
    def description(self) -> str:
        return "Take and retrieve quick notes"

    @property
    def keywords(self) -> List[str]:
        return ["note", "remember", "write down", "remind me", "notes"]

    def __init__(self):
        """Initialize notes skill."""
        self._notes_file = SETTINGS.data_dir / "notes.json"
        self._notes: List[dict] = []
        self._load_notes()

    def _load_notes(self) -> None:
        """Load notes from file."""
        if self._notes_file.exists():
            try:
                with open(self._notes_file, "r", encoding="utf-8") as f:
                    self._notes = json.load(f)
                logger.info(f"Loaded {len(self._notes)} notes")
            except Exception as e:
                logger.error(f"Failed to load notes: {e}")
                self._notes = []

    def _save_notes(self) -> None:
        """Save notes to file."""
        try:
            self._notes_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._notes_file, "w", encoding="utf-8") as f:
                json.dump(self._notes, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save notes: {e}")

    def execute(self, params: dict) -> str:
        """
        Execute notes command.

        Args:
            params: {"action": "add/list/clear/delete", "content": "note text"}

        Returns:
            Result message
        """
        action = params.get("action", "list")
        content = params.get("content", "")

        if action == "add":
            return self._add_note(content)
        elif action == "list":
            return self._list_notes()
        elif action == "clear":
            return self._clear_notes()
        elif action == "delete":
            return self._delete_note(params.get("index", -1))
        else:
            return self._list_notes()

    def _add_note(self, content: str) -> str:
        """Add a new note."""
        if not content.strip():
            return "What would you like me to note?"

        note = {
            "content": content.strip(),
            "created_at": datetime.now().isoformat(),
            "id": len(self._notes) + 1,
        }

        self._notes.append(note)
        self._save_notes()

        logger.info(f"Added note: {content[:50]}...")
        return f"Got it! I've noted: '{content}'"

    def _list_notes(self) -> str:
        """List all notes."""
        if not self._notes:
            return "You don't have any notes yet. Want me to take one?"

        # Get recent notes (last 5)
        recent = self._notes[-5:]

        lines = [f"You have {len(self._notes)} notes. Here are the recent ones:\n"]

        for note in recent:
            created = note.get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except Exception:
                    time_str = ""
            else:
                time_str = ""

            content = note.get("content", "")
            if len(content) > 100:
                content = content[:100] + "..."

            lines.append(f"• {content}")
            if time_str:
                lines.append(f"  ({time_str})")

        if len(self._notes) > 5:
            lines.append(f"\n...and {len(self._notes) - 5} more")

        return "\n".join(lines)

    def _clear_notes(self) -> str:
        """Clear all notes."""
        count = len(self._notes)
        self._notes = []
        self._save_notes()

        if count == 0:
            return "There were no notes to clear."
        return f"Cleared all {count} notes!"

    def _delete_note(self, index: int) -> str:
        """Delete a specific note."""
        if not self._notes:
            return "There are no notes to delete."

        # If no index, delete last note
        if index < 0 or index >= len(self._notes):
            index = len(self._notes) - 1

        deleted = self._notes.pop(index)
        self._save_notes()

        content = deleted.get("content", "")
        if len(content) > 50:
            content = content[:50] + "..."

        return f"Deleted note: '{content}'"

    def search_notes(self, query: str) -> List[dict]:
        """Search notes by content."""
        query_lower = query.lower()
        return [
            note for note in self._notes
            if query_lower in note.get("content", "").lower()
        ]

    def get_note_count(self) -> int:
        """Get total number of notes."""
        return len(self._notes)
