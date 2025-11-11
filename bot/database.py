"""
Database management for filler words tracking using SQLite.
"""

import sqlite3
from datetime import datetime, timedelta
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
                """
                CREATE INDEX IF NOT EXISTS idx_user_chat 
                ON filler_words_usage(user_id, chat_id)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON filler_words_usage(timestamp)
                """
            )
            conn.commit()
            self.logger.info(f"Database initialized at {self.db_path}")

    def record_filler_word(
        self, user_id: int, chat_id: int, word: str, timestamp: datetime = None
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

        # Convert datetime to ISO format string for SQLite compatibility
        timestamp_str = (
            timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO filler_words_usage (user_id, chat_id, word, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, chat_id, word.lower(), timestamp_str),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            # Database constraint violation
            self.logger.warning(
                f"Database integrity error for user {user_id} in chat {chat_id}: {word} - {e}"
            )
            return False
        except Exception as e:
            self.logger.error(f"Error recording filler word: {e}")
            return False

    def get_stats_all_time(self, user_id: int, chat_id: int) -> dict:
        """
        Get all-time statistics for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute(
                """
                SELECT COUNT(*) FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ?
                """,
                (user_id, chat_id),
            )
            total_count = cursor.fetchone()[0]

            # Word breakdown
            cursor.execute(
                """
                SELECT word, COUNT(*) as count FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ?
                GROUP BY word
                ORDER BY count DESC
                """,
                (user_id, chat_id),
            )
            word_breakdown = cursor.fetchall()

            return {
                "total": total_count,
                "breakdown": word_breakdown,
            }

    def get_stats_monthly(self, user_id: int, chat_id: int) -> dict:
        """
        Get monthly statistics (last 30 days) for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        thirty_days_ago = datetime.now() - timedelta(days=30)
        # Convert datetime to ISO format string for SQLite compatibility
        thirty_days_ago_str = thirty_days_ago.isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count for last 30 days
            cursor.execute(
                """
                SELECT COUNT(*) FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                """,
                (user_id, chat_id, thirty_days_ago_str),
            )
            total_count = cursor.fetchone()[0]

            # Word breakdown for last 30 days
            cursor.execute(
                """
                SELECT word, COUNT(*) as count FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                GROUP BY word
                ORDER BY count DESC
                """,
                (user_id, chat_id, thirty_days_ago_str),
            )
            word_breakdown = cursor.fetchall()

            return {
                "total": total_count,
                "breakdown": word_breakdown,
            }

    def get_stats_daily(self, user_id: int, chat_id: int) -> dict:
        """
        Get daily statistics (today) for a user in a specific chat.

        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID

        Returns:
            Dictionary with statistics
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Convert datetime to ISO format string for SQLite compatibility
        today_start_str = today_start.isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count for today
            cursor.execute(
                """
                SELECT COUNT(*) FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                """,
                (user_id, chat_id, today_start_str),
            )
            total_count = cursor.fetchone()[0]

            # Word breakdown for today
            cursor.execute(
                """
                SELECT word, COUNT(*) as count FROM filler_words_usage
                WHERE user_id = ? AND chat_id = ? AND timestamp >= ?
                GROUP BY word
                ORDER BY count DESC
                """,
                (user_id, chat_id, today_start_str),
            )
            word_breakdown = cursor.fetchall()

            return {
                "total": total_count,
                "breakdown": word_breakdown,
            }

    def close(self) -> None:
        """Close the database connection (cleanup method)."""
        # sqlite3 connections are closed automatically when exiting context manager
        pass
