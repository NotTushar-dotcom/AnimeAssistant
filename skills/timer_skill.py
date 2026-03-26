"""
Aara Timer Skill
Set timers and get notifications.
"""

import re
import logging
import threading
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class TimerSkill(BaseSkill):
    """Manages timers and alarms."""

    @property
    def name(self) -> str:
        return "timer"

    @property
    def description(self) -> str:
        return "Set timers and get notifications"

    @property
    def keywords(self) -> List[str]:
        return ["timer", "alarm", "remind", "minutes", "seconds", "hours"]

    def __init__(self):
        """Initialize timer skill."""
        self._timers: Dict[str, dict] = {}
        self._timer_count = 0
        self._on_timer_complete = None

    def set_callback(self, callback) -> None:
        """Set callback for timer completion."""
        self._on_timer_complete = callback

    def execute(self, params: dict) -> str:
        """
        Execute timer command.

        Args:
            params: {"duration": "5 minutes", "action": "set/cancel/list"}

        Returns:
            Result message
        """
        action = params.get("action", "set")
        duration = params.get("duration", "")

        if action == "cancel":
            return self._cancel_timer(params.get("timer_id"))
        elif action == "list":
            return self._list_timers()
        else:
            return self._set_timer(duration)

    def _set_timer(self, duration_str: str) -> str:
        """Set a new timer."""
        seconds = self._parse_duration(duration_str)
        if seconds is None or seconds <= 0:
            return "I couldn't understand that duration. Try something like '5 minutes' or '30 seconds'."

        self._timer_count += 1
        timer_id = f"timer_{self._timer_count}"
        end_time = datetime.now() + timedelta(seconds=seconds)

        # Create timer thread
        timer = threading.Timer(seconds, self._timer_finished, args=[timer_id])
        timer.daemon = True
        timer.start()

        self._timers[timer_id] = {
            "id": timer_id,
            "duration": duration_str,
            "seconds": seconds,
            "end_time": end_time,
            "timer": timer,
        }

        # Format duration for display
        display_duration = self._format_duration(seconds)
        logger.info(f"Timer set: {timer_id} for {display_duration}")

        return f"Timer set for {display_duration}! I'll let you know when it's done."

    def _cancel_timer(self, timer_id: Optional[str] = None) -> str:
        """Cancel a timer."""
        if not self._timers:
            return "There are no active timers to cancel."

        if timer_id and timer_id in self._timers:
            timer_info = self._timers[timer_id]
            timer_info["timer"].cancel()
            del self._timers[timer_id]
            return f"Cancelled timer for {timer_info['duration']}."

        # Cancel most recent timer
        if self._timers:
            timer_id = list(self._timers.keys())[-1]
            timer_info = self._timers[timer_id]
            timer_info["timer"].cancel()
            del self._timers[timer_id]
            return f"Cancelled timer for {timer_info['duration']}."

        return "No timer to cancel."

    def _list_timers(self) -> str:
        """List active timers."""
        if not self._timers:
            return "There are no active timers."

        lines = ["Active timers:"]
        now = datetime.now()

        for timer_id, info in self._timers.items():
            remaining = (info["end_time"] - now).total_seconds()
            if remaining > 0:
                display = self._format_duration(int(remaining))
                lines.append(f"  - {info['duration']}: {display} remaining")

        return "\n".join(lines)

    def _timer_finished(self, timer_id: str) -> None:
        """Called when a timer finishes."""
        if timer_id in self._timers:
            timer_info = self._timers[timer_id]
            logger.info(f"Timer finished: {timer_id}")

            # Remove from active timers
            del self._timers[timer_id]

            # Call callback if set
            if self._on_timer_complete:
                try:
                    self._on_timer_complete(f"Your timer for {timer_info['duration']} is done!")
                except Exception as e:
                    logger.error(f"Timer callback error: {e}")

            # Play notification sound
            try:
                from voice.audio_utils import play_sound_file
                from pathlib import Path
                sound_path = Path("assets/sounds/notification.wav")
                if sound_path.exists():
                    play_sound_file(str(sound_path))
            except Exception:
                pass

    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds."""
        duration_str = duration_str.lower().strip()

        total_seconds = 0

        # Pattern: number + unit (e.g., "5 minutes", "30 seconds")
        patterns = [
            (r"(\d+)\s*(?:hour|hr|h)", 3600),
            (r"(\d+)\s*(?:minute|min|m)", 60),
            (r"(\d+)\s*(?:second|sec|s)", 1),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, duration_str)
            if match:
                total_seconds += int(match.group(1)) * multiplier

        # If just a number, assume minutes
        if total_seconds == 0:
            match = re.search(r"(\d+)", duration_str)
            if match:
                total_seconds = int(match.group(1)) * 60

        return total_seconds if total_seconds > 0 else None

    def _format_duration(self, seconds: int) -> str:
        """Format seconds to readable duration."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            if secs:
                return f"{minutes} minutes {secs} seconds"
            return f"{minutes} minutes"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes:
                return f"{hours} hours {minutes} minutes"
            return f"{hours} hours"

    def get_remaining_time(self, timer_id: str) -> Optional[int]:
        """Get remaining time for a timer in seconds."""
        if timer_id in self._timers:
            remaining = (self._timers[timer_id]["end_time"] - datetime.now()).total_seconds()
            return max(0, int(remaining))
        return None
