"""
Messages for the Filler Words Detector Bot.
"""


class Messages:
    """Container for all bot messages."""

    # Command responses
    START_MESSAGE = (
        "👋 Hello! I'm a Filler Words Detector Bot!\n\n"
        "I track filler words in your messages and provide statistics.\n\n"
        "*Commands:*\n"
        "• /start - Start tracking filler words\n"
        "• /stop - Stop tracking filler words\n"
        "• /stats - View your usage statistics\n\n"
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

        # Daily stats
        message += self.STATS_PERIOD_DAILY
        if daily["total"] > 0:
            message += f"Total: *{daily['total']}*\n"
            if daily["breakdown"]:
                for word, count in daily["breakdown"][:5]:  # Show top 5
                    message += f"  • {word}: {count}\n"
        else:
            message += self.NO_STATS_MESSAGE + "\n"
        message += "\n"

        # Monthly stats
        message += self.STATS_PERIOD_MONTHLY
        if monthly["total"] > 0:
            message += f"Total: *{monthly['total']}*\n"
            if monthly["breakdown"]:
                for word, count in monthly["breakdown"][:5]:  # Show top 5
                    message += f"  • {word}: {count}\n"
        else:
            message += self.NO_STATS_MESSAGE + "\n"
        message += "\n"

        # All-time stats
        message += self.STATS_PERIOD_ALL_TIME
        if all_time["total"] > 0:
            message += f"Total: *{all_time['total']}*\n"
            if all_time["breakdown"]:
                for word, count in all_time["breakdown"][:5]:  # Show top 5
                    message += f"  • {word}: {count}\n"
        else:
            message += self.NO_STATS_MESSAGE + "\n"

        return message
