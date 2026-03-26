"""
Aara Text Processing Utilities
Text cleaning and formatting functions.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def remove_markdown(text: str) -> str:
    """
    Remove markdown formatting from text.

    Args:
        text: Markdown text

    Returns:
        Plain text
    """
    # Remove headers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # Remove inline code
    text = re.sub(r'`(.+?)`', r'\1', text)

    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)

    # Remove links - keep the text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # Remove images
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)

    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Remove list markers
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)

    return clean_text(text)


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    # Try to truncate at a word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.5:
        truncated = truncated[:last_space]

    return truncated.rstrip() + suffix


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.

    Args:
        text: Text containing URLs

    Returns:
        List of URLs
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
    return re.findall(url_pattern, text)


def extract_email(text: str) -> List[str]:
    """
    Extract email addresses from text.

    Args:
        text: Text containing emails

    Returns:
        List of email addresses
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace to single spaces.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    return ' '.join(text.split())


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from text.

    Args:
        text: Input text

    Returns:
        Text without punctuation
    """
    return re.sub(r'[^\w\s]', '', text)


def capitalize_sentences(text: str) -> str:
    """
    Capitalize the first letter of each sentence.

    Args:
        text: Input text

    Returns:
        Text with capitalized sentences
    """
    # Split by sentence endings
    sentences = re.split(r'([.!?]\s+)', text)

    result = []
    for i, part in enumerate(sentences):
        if i % 2 == 0 and part:  # Sentence content
            result.append(part[0].upper() + part[1:] if part else part)
        else:  # Punctuation
            result.append(part)

    return ''.join(result)


def extract_numbers(text: str) -> List[float]:
    """
    Extract numbers from text.

    Args:
        text: Text containing numbers

    Returns:
        List of numbers
    """
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    return [float(m) for m in matches]


def highlight_keywords(text: str, keywords: List[str], marker: str = "**") -> str:
    """
    Highlight keywords in text.

    Args:
        text: Input text
        keywords: Keywords to highlight
        marker: Marker for highlighting (markdown style)

    Returns:
        Text with highlighted keywords
    """
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f"{marker}{keyword}{marker}", text)
    return text


def word_count(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Input text

    Returns:
        Number of words
    """
    return len(text.split())


def char_count(text: str, include_spaces: bool = False) -> int:
    """
    Count characters in text.

    Args:
        text: Input text
        include_spaces: Whether to include spaces

    Returns:
        Number of characters
    """
    if include_spaces:
        return len(text)
    return len(text.replace(' ', ''))
