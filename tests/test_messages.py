"""Tests for Messages."""

from bot.messages import Messages


def test_format_stats():
    """Test formatting statistics message."""
    messages = Messages()

    daily = {"total": 5, "breakdown": [("like", 3), ("um", 2)]}
    monthly = {"total": 20, "breakdown": [("like", 12), ("um", 8)]}
    all_time = {"total": 50, "breakdown": [("like", 30), ("um", 20)]}

    result = messages.format_stats(daily, monthly, all_time)

    assert "5" in result
    assert "20" in result
    assert "50" in result
    assert "like" in result
    assert "um" in result


def test_format_stats_empty():
    """Test formatting with no statistics."""
    messages = Messages()

    empty = {"total": 0, "breakdown": []}

    result = messages.format_stats(empty, empty, empty)

    assert messages.NO_STATS_MESSAGE in result
