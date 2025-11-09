"""
Filler words detection module.
"""

import re


class FillerWordsDetector:
    """Detector for filler words in text messages."""

    def __init__(self, filler_words: list[str]):
        """
        Initialize the filler words detector.

        Args:
            filler_words: List of filler words to detect (case-insensitive)
        """
        self.filler_words = [
            word.lower().strip() for word in filler_words if word.strip()
        ]

    def detect_filler_words(self, text: str) -> list[str]:
        """
        Detect all filler words in the given text.

        Args:
            text: The text to analyze

        Returns:
            List of detected filler words (can contain duplicates if word appears multiple times)
        """
        if not text or not self.filler_words:
            return []

        text_lower = text.lower()
        detected = []

        for filler_word in self.filler_words:
            # Use word boundaries to match whole words only
            # This prevents matching "like" in "unlikely"
            pattern = r"\b" + re.escape(filler_word) + r"\b"
            matches = re.findall(pattern, text_lower)
            detected.extend(matches)

        return detected

    def count_filler_words(self, text: str) -> int:
        """
        Count the total number of filler words in the text.

        Args:
            text: The text to analyze

        Returns:
            Total count of filler words
        """
        return len(self.detect_filler_words(text))

    def get_filler_words_breakdown(self, text: str) -> dict:
        """
        Get a breakdown of filler words found in the text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary mapping each detected filler word to its count
        """
        detected = self.detect_filler_words(text)
        breakdown = {}
        for word in detected:
            breakdown[word] = breakdown.get(word, 0) + 1
        return breakdown
