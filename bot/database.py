"""
Database management for filler words tracking using SQLite.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import logging


class FillerWordsDatabase:
    """SQLite database for tracking filler words usage."""

    def __init__(self, db_path: str = "filler_words.db"):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS filler_words_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # Create indexes for faster queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_chat ON filler_words_usage(user_id, chat_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON filler_words_usage(timestamp)"
            )
            conn.commit()
            self.logger.info(f"Database initialized at {self.db_path}")

    @staticmethod
    def _to_iso_string(timestamp: datetime) -> str:
        """Convert datetime to ISO format string for SQLite compatibility."""
        return timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp

    def record_filler_word(
        self,
        user_id: int,
        chat_id: int,
        word: str,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Record a filler word usage.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            word: The filler word used
            timestamp: Optional timestamp (defaults to now)

        Returns:
            True if recorded successfully, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.now()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO filler_words_usage (user_id, chat_id, word, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, chat_id, word.lower(), self._to_iso_string(timestamp)),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            self.logger.warning(
                f"Database integrity error for user {user_id} in chat {chat_id}: {word} - {e}"
            )
            return False
        except Exception as e:
            self.logger.error(f"Error recording filler word: {e}")
            return False

    def _get_total_count(
        self, user_id: int, chat_id: int, since: Optional[datetime] = None
    ) -> int:
        """
        Get total count of filler words for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            since: Optional datetime to filter records from (inclusive)

        Returns:
            Total count of filler words
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if since:
                query = """
                    SELECT COUNT(*) FROM filler_words_usage
                    WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                """
                params = (user_id, chat_id, self._to_iso_string(since))
            else:
                query = """
                    SELECT COUNT(*) FROM filler_words_usage
                    WHERE user_id = ? AND chat_id = ?
                """
                params = (user_id, chat_id)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def _get_word_breakdown(
        self, user_id: int, chat_id: int, since: Optional[datetime] = None
    ) -> list:
        """
        Get word breakdown statistics for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            since: Optional datetime to filter records from (inclusive)

        Returns:
            List of tuples (word, count) ordered by count descending
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if since:
                query = """
                    SELECT word, COUNT(*) as count FROM filler_words_usage
                    WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                    GROUP BY word
                    ORDER BY count DESC
                """
                params = (user_id, chat_id, self._to_iso_string(since))
            else:
                query = """
                    SELECT word, COUNT(*) as count FROM filler_words_usage
                    WHERE user_id = ? AND chat_id = ?
                    GROUP BY word
                    ORDER BY count DESC
                """
                params = (user_id, chat_id)

            cursor.execute(query, params)
            return cursor.fetchall()

    def _get_stats(
        self, user_id: int, chat_id: int, since: Optional[datetime] = None
    ) -> dict:
        """
        Get statistics for a user in a specific chat, optionally filtered by time.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            since: Optional datetime to filter records from (inclusive)

        Returns:
            Dictionary with 'total' count and 'breakdown' list of (word, count) tuples
        """
        return {
            "total": self._get_total_count(user_id, chat_id, since),
            "breakdown": self._get_word_breakdown(user_id, chat_id, since),
        }

    def get_stats_all_time(self, user_id: int, chat_id: int) -> dict:
        """
        Get all-time statistics for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        return self._get_stats(user_id, chat_id)

    def get_stats_monthly(self, user_id: int, chat_id: int) -> dict:
        """
        Get monthly statistics (last 30 days) for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        since = datetime.now() - timedelta(days=30)
        return self._get_stats(user_id, chat_id, since)

    def get_stats_daily(self, user_id: int, chat_id: int) -> dict:
        """
        Get daily statistics (today) for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self._get_stats(user_id, chat_id, since)
