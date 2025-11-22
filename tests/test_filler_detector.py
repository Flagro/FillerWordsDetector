"""Tests for FillerWordsDetector."""

from bot.filler_detector import FillerWordsDetector


def test_detect_filler_words():
    """Test basic filler word detection."""
    detector = FillerWordsDetector(["like", "um", "uh"])
    text = "I like this, um, thing like that"

    detected = detector.detect_filler_words(text)

    assert len(detected) == 3
    assert detected.count("like") == 2
    assert detected.count("um") == 1


def test_get_filler_words_breakdown():
    """Test filler words breakdown statistics."""
    detector = FillerWordsDetector(["basically", "literally"])
    text = "Basically, it's literally amazing, literally"

    breakdown = detector.get_filler_words_breakdown(text)

    assert breakdown["basically"] == 1
    assert breakdown["literally"] == 2
