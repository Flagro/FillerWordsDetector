"""Tests for FillerWordsDatabase."""

import tempfile
import os
from datetime import datetime, timedelta
from bot.database import FillerWordsDatabase


def test_record_and_get_stats():
    """Test recording filler words and retrieving statistics."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        db_path = tmp_file.name

    try:
        db = FillerWordsDatabase(db_path)

        # Record some filler words
        db.record_filler_word(user_id=1, chat_id=100, word="like")
        db.record_filler_word(user_id=1, chat_id=100, word="um")
        db.record_filler_word(user_id=1, chat_id=100, word="like")

        # Get stats
        stats = db.get_stats_all_time(user_id=1, chat_id=100)

        assert stats["total"] == 3
        assert len(stats["breakdown"]) == 2
        assert dict(stats["breakdown"])["like"] == 2
    finally:
        os.unlink(db_path)


def test_reset_user_stats():
    """Test resetting user statistics."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        db_path = tmp_file.name

    try:
        db = FillerWordsDatabase(db_path)

        db.record_filler_word(user_id=1, chat_id=100, word="basically")
        db.reset_user_stats(user_id=1, chat_id=100)

        stats = db.get_stats_all_time(user_id=1, chat_id=100)
        assert stats["total"] == 0
    finally:
        os.unlink(db_path)
