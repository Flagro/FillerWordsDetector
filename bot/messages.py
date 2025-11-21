"""
Messages for the Filler Words Detector Bot.
"""

from typing import Optional


class Messages:
    """Container for all bot messages."""

    # Command responses
    START_MESSAGE = (
        "👋 Hello! I'm a Filler Words Detector Bot!\n\n"
        "I track filler words in your messages and provide statistics.\n\n"
        "*Commands:*\n"
        "• /start - Start tracking filler words (admin only)\n"
        "• /stop - Stop tracking filler words (admin only)\n"
        "• /stats - View your usage statistics\n"
        "• /reset - Reset your personal statistics\n"
        "• /group_reset - Reset statistics for entire group (admin only)\n\n"
        "*How it works:*\n"
        "I'll monitor all messages and notify you when filler words are detected. "
        "You can view stats for today, this month, or all time!"
    )

    STOP_MESSAGE = "🛑 Filler words tracking stopped. Use /start to resume tracking."

    STATS_HEADER = "📊 *Filler Words Statistics*\n\n"

    STATS_PERIOD_DAILY = "📅 *Today's Stats:*\n"
    STATS_PERIOD_MONTHLY = "📆 *Last 30 Days:*\n"
    STATS_PERIOD_ALL_TIME = "🕐 *All-Time Stats:*\n"

    NO_STATS_MESSAGE = "No filler words detected yet. Keep chatting!"

    FILLER_WORD_DETECTED = "🔔 Filler word detected: *{words}*"

    BOT_NOT_ACTIVE = "Bot is not tracking in this chat. Use /start to activate."

    UNAUTHORIZED_USER = "Sorry, you are not authorized to use this bot."

    UNAUTHORIZED_ADMIN = "Sorry, only administrators can manage this bot."

    RESET_SUCCESS = "✅ Your statistics have been reset successfully!"

    RESET_ERROR = "❌ Failed to reset your statistics. Please try again later."

    GROUP_RESET_SUCCESS = (
        "✅ All statistics for this group have been reset successfully!"
    )

    GROUP_RESET_ERROR = "❌ Failed to reset group statistics. Please try again later."

    # Settings
    TOP_N_WORDS: Optional[int] = None

    def format_stats(self, daily: dict, monthly: dict, all_time: dict) -> str:
        """
        Format statistics into a readable message.

        Args:
            daily: Daily statistics dict
            monthly: Monthly statistics dict
            all_time: All-time statistics dict

        Returns:
            Formatted statistics message
        """
        message = self.STATS_HEADER

        # Show totals for each period
        message += f"📅 Today: *{daily['total']}* | "
        message += f"📆 Last 30 Days: *{monthly['total']}* | "
        message += f"🕐 All-Time: *{all_time['total']}*\n\n"

        # Collect all unique words across all periods
        all_words = set()
        daily_dict = dict(daily.get("breakdown", []))
        monthly_dict = dict(monthly.get("breakdown", []))
        all_time_dict = dict(all_time.get("breakdown", []))

        all_words.update(daily_dict.keys())
        all_words.update(monthly_dict.keys())
        all_words.update(all_time_dict.keys())

        if not all_words:
            message += self.NO_STATS_MESSAGE
            return message

        # Sort words by all-time count (descending)
        sorted_words = sorted(
            all_words, key=lambda w: all_time_dict.get(w, 0), reverse=True
        )

        # Apply TOP_N_WORDS limit if set
        if self.TOP_N_WORDS is not None:
            sorted_words = sorted_words[: self.TOP_N_WORDS]

        # Format each word with its counts across periods
        message += "*Breakdown by word (word - daily - monthly - all-time):*\n"
        for word in sorted_words:
            daily_count = daily_dict.get(word, 0)
            monthly_count = monthly_dict.get(word, 0)
            all_time_count = all_time_dict.get(word, 0)

            message += f"• {word}: {daily_count} / {monthly_count} / {all_time_count}\n"

        return message
