"""
Aara Helper Utilities
Common utility functions.
"""

import json
import re
from pathlib import Path
from typing import Optional, Any, List
from difflib import SequenceMatcher


def safe_json_loads(text: str) -> Optional[dict]:
    """
    Safely parse JSON from text.

    Args:
        text: Text that may contain JSON

    Returns:
        Parsed dict or None
    """
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in text
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return None


def fuzzy_match(
    query: str,
    options: List[str],
    threshold: float = 0.6
) -> Optional[str]:
    """
    Find the best fuzzy match for a query.

    Args:
        query: Query string
        options: List of options to match against
        threshold: Minimum similarity threshold (0-1)

    Returns:
        Best matching option or None
    """
    query_lower = query.lower()
    best_match = None
    best_score = 0

    for option in options:
        option_lower = option.lower()

        # Exact match
        if query_lower == option_lower:
            return option

        # Substring match
        if query_lower in option_lower or option_lower in query_lower:
            score = 0.9
        else:
            # Sequence matching
            score = SequenceMatcher(None, query_lower, option_lower).ratio()

        if score > best_score and score >= threshold:
            best_score = score
            best_match = option

    return best_match


def sanitize_for_speech(text: str) -> str:
    """
    Sanitize text for text-to-speech.

    Args:
        text: Raw text

    Returns:
        Cleaned text suitable for TTS
    """
    # Remove emotion tags
    text = re.sub(r'\[[\w]+\]', '', text)

    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.+?)`', r'\1', text)        # Code
    text = re.sub(r'#{1,6}\s*', '', text)         # Headers

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove special characters that shouldn't be spoken
    text = re.sub(r'[<>{}[\]|\\]', '', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text.strip()


def ensure_dir(path: str) -> Path:
    """
    Ensure a directory exists.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_data_dir() -> Path:
    """
    Get the data directory path.

    Returns:
        Path to data directory
    """
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def format_duration(seconds: int) -> str:
    """
    Format seconds into a human-readable duration.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string (e.g., "2h 30m")
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        if secs:
            return f"{minutes}m {secs}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes:
            return f"{hours}h {minutes}m"
        return f"{hours}h"


def parse_duration(text: str) -> Optional[int]:
    """
    Parse a duration string to seconds.

    Args:
        text: Duration string (e.g., "5 minutes", "1h 30m")

    Returns:
        Seconds or None
    """
    text = text.lower().strip()
    total = 0

    patterns = [
        (r'(\d+)\s*(?:hour|hr|h)', 3600),
        (r'(\d+)\s*(?:minute|min|m)', 60),
        (r'(\d+)\s*(?:second|sec|s)', 1),
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, text)
        if match:
            total += int(match.group(1)) * multiplier

    return total if total > 0 else None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix
