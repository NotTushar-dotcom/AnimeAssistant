"""
Aara Emotion Detector
Extracts and validates emotions from LLM responses.
"""

import re
import logging
from typing import Optional

from core.personality import (
    EMOTION_DEFINITIONS,
    VALID_EMOTIONS,
    DEFAULT_EMOTION,
    extract_emotion_tag,
    get_emotion_color,
    get_emotion_animation,
)

logger = logging.getLogger(__name__)


class EmotionDetector:
    """Detects and validates emotions in text responses."""

    def __init__(self):
        """Initialize detector."""
        self.valid_emotions = VALID_EMOTIONS
        self.default_emotion = DEFAULT_EMOTION
        self.current_emotion = DEFAULT_EMOTION

    def detect(self, text: str) -> str:
        """
        Detect emotion from response text.

        Args:
            text: Response text potentially containing emotion tag

        Returns:
            Detected emotion string
        """
        _, emotion = extract_emotion_tag(text)
        self.current_emotion = emotion
        logger.debug(f"Detected emotion: {emotion}")
        return emotion

    def validate(self, emotion: str) -> str:
        """
        Validate emotion and return valid emotion or default.

        Args:
            emotion: Emotion to validate

        Returns:
            Valid emotion string
        """
        emotion = emotion.lower().strip()
        if emotion in self.valid_emotions:
            return emotion
        logger.warning(f"Invalid emotion '{emotion}', using default: {self.default_emotion}")
        return self.default_emotion

    def get_clean_text(self, text: str) -> str:
        """
        Remove emotion tag from text.

        Args:
            text: Text with potential emotion tag

        Returns:
            Clean text without emotion tag
        """
        clean_text, _ = extract_emotion_tag(text)
        return clean_text

    def get_animation_params(self, emotion: str) -> dict:
        """
        Get animation parameters for an emotion.

        Args:
            emotion: Emotion name

        Returns:
            Dict with animation parameters
        """
        emotion = self.validate(emotion)
        emotion_def = EMOTION_DEFINITIONS.get(emotion, EMOTION_DEFINITIONS[self.default_emotion])

        return {
            "emotion": emotion,
            "animation": emotion_def.get("animation", "idle"),
            "color": emotion_def.get("color", "#E6E6FA"),
            "description": emotion_def.get("description", ""),
            "triggers": emotion_def.get("triggers", []),
        }

    def get_color(self, emotion: Optional[str] = None) -> str:
        """
        Get color for emotion.

        Args:
            emotion: Optional emotion name (uses current if not provided)

        Returns:
            Hex color code
        """
        if emotion is None:
            emotion = self.current_emotion
        return get_emotion_color(emotion)

    def get_animation(self, emotion: Optional[str] = None) -> str:
        """
        Get animation name for emotion.

        Args:
            emotion: Optional emotion name (uses current if not provided)

        Returns:
            Animation identifier
        """
        if emotion is None:
            emotion = self.current_emotion
        return get_emotion_animation(emotion)

    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze text for emotional content without relying on tags.

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment analysis results
        """
        text_lower = text.lower()

        # Simple keyword-based sentiment analysis
        sentiment_keywords = {
            "happy": ["great", "wonderful", "amazing", "love", "happy", "yay", "awesome"],
            "excited": ["exciting", "can't wait", "wow", "incredible", "fantastic"],
            "sad": ["sorry", "sad", "unfortunately", "apologize", "regret"],
            "concerned": ["worry", "careful", "caution", "warning", "please be"],
            "playful": ["haha", "lol", "tease", "joke", "fun", "silly"],
            "curious": ["interesting", "wonder", "curious", "tell me", "learn"],
            "surprised": ["surprised", "unexpected", "didn't expect", "wow"],
        }

        scores = {emotion: 0 for emotion in sentiment_keywords}

        for emotion, keywords in sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[emotion] += 1

        # Find highest scoring emotion
        max_emotion = max(scores, key=scores.get)
        if scores[max_emotion] > 0:
            confidence = min(scores[max_emotion] / 3, 1.0)  # Normalize
        else:
            max_emotion = self.default_emotion
            confidence = 0.5

        return {
            "detected_emotion": max_emotion,
            "confidence": confidence,
            "scores": scores,
        }

    def transition_emotion(self, from_emotion: str, to_emotion: str) -> list[str]:
        """
        Get intermediate emotions for smooth transition.

        Args:
            from_emotion: Starting emotion
            to_emotion: Target emotion

        Returns:
            List of emotions for transition
        """
        # Define emotion groups for natural transitions
        positive = ["happy", "excited", "playful", "proud"]
        calm = ["relaxed", "focused", "thinking", "curious"]
        negative = ["sad", "worried", "concerned"]
        special = ["shy", "surprised", "determined"]

        # If same emotion or adjacent, direct transition
        if from_emotion == to_emotion:
            return [to_emotion]

        # Find transition path
        transitions = [from_emotion]

        # Transition through neutral state if going between opposites
        if from_emotion in positive and to_emotion in negative:
            transitions.append("relaxed")
        elif from_emotion in negative and to_emotion in positive:
            transitions.append("thinking")

        transitions.append(to_emotion)
        return transitions
