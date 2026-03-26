"""
Aara Core Module
Exports main classes for the assistant brain.
"""

from core.brain import create_brain, LLMBrain
from core.personality import (
    AARA_SYSTEM_PROMPT,
    EMOTION_DEFINITIONS,
    extract_emotion_tag,
    get_emotion_color,
)
from core.intent_parser import IntentParser, Intent, IntentType
from core.command_handler import CommandHandler, CommandResult
from core.emotion_detector import EmotionDetector

__all__ = [
    "create_brain",
    "LLMBrain",
    "AARA_SYSTEM_PROMPT",
    "EMOTION_DEFINITIONS",
    "extract_emotion_tag",
    "get_emotion_color",
    "IntentParser",
    "Intent",
    "IntentType",
    "CommandHandler",
    "CommandResult",
    "EmotionDetector",
]
