"""
Telegram bot for detecting and tracking filler words in messages.
"""

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

from bot.database import FillerWordsDatabase
from bot.filler_detector import FillerWordsDetector
from bot.messages import Messages
from bot.chat_state import ChatStateManager


class TelegramFillerBot:
    """Telegram bot that detects and tracks filler words."""

    def __init__(
        self,
        telegram_token: str,
        filler_words: list[str],
        db_path: str = "filler_words.db",
        allowed_handles: list[str] | None = None,
        admin_handles: list[str] | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the Telegram Filler Words Bot.

        Args:
            telegram_token: Telegram bot API token
            filler_words: List of filler words to detect
            db_path: Path to SQLite database file
            allowed_handles: Optional list of allowed usernames (without @)
            admin_handles: Optional list of admin usernames (without @)
            logger: Optional logger instance
        """
        self.telegram_token = telegram_token
        self.filler_words = filler_words
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.database = FillerWordsDatabase(db_path)
        self.detector = FillerWordsDetector(filler_words)
        self.state_manager = ChatStateManager()
        self.messages = Messages()

    def run(self) -> None:
        """Run the bot."""
        application = ApplicationBuilder().token(self.telegram_token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("stop", self.stop_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("reset", self.reset_command))
        application.add_handler(CommandHandler("group_reset", self.group_reset_command))

        # Add message handler for filler word detection
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        self.logger.info("Filler Words Bot started")
        application.run_polling()

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /start command."""
        if not update.message or not update.effective_chat:
            return

        # Check if user is an admin (if admin list is configured, empty/None = allow all)
        if (
            self.admin_handles
            and len(self.admin_handles) > 0
            and not self._is_admin(update)
        ):
            try:
                await update.message.reply_text(self.messages.UNAUTHORIZED_ADMIN)
            except Exception as e:
                self.logger.error(f"Error sending unauthorized message: {e}")
            username = update.message.from_user.username or "Unknown"
            self.logger.warning(
                f"Unauthorized start attempt by user {username} (ID: {update.message.from_user.id})"
            )
            return

        # Activate bot for this chat
        chat_id = update.effective_chat.id
        self.state_manager.set_active(chat_id, True)

        try:
            await update.message.reply_text(
                self.messages.START_MESSAGE,
                parse_mode=ParseMode.MARKDOWN,
            )
            self.logger.info(f"Bot activated in chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Error sending start message: {e}")

    async def stop_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /stop command."""
        if not update.message or not update.effective_chat:
            return

        # Check if user is an admin (if admin list is configured, empty/None = allow all)
        if (
            self.admin_handles
            and len(self.admin_handles) > 0
            and not self._is_admin(update)
        ):
            try:
                await update.message.reply_text(self.messages.UNAUTHORIZED_ADMIN)
            except Exception as e:
                self.logger.error(f"Error sending unauthorized message: {e}")
            username = update.message.from_user.username or "Unknown"
            self.logger.warning(
                f"Unauthorized stop attempt by user {username} (ID: {update.message.from_user.id})"
            )
            return

        # Deactivate bot for this chat
        chat_id = update.effective_chat.id
        self.state_manager.set_active(chat_id, False)

        try:
            await update.message.reply_text(self.messages.STOP_MESSAGE)
            self.logger.info(f"Bot deactivated in chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Error sending stop message: {e}")

    async def stats_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /stats command - show statistics for the user."""
        if (
            not update.message
            or not update.effective_chat
            or not update.message.from_user
        ):
            return

        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id

        # Check if bot is active in this chat
        if not self.state_manager.is_active(chat_id):
            try:
                await update.message.reply_text(self.messages.BOT_NOT_ACTIVE)
            except Exception as e:
                self.logger.error(f"Error sending bot not active message: {e}")
            return

        # Check if user is allowed to use the bot
        if (
            self.allowed_handles
            and len(self.allowed_handles) > 0
            and not self._is_allowed(update)
        ):
            try:
                await update.message.reply_text(self.messages.UNAUTHORIZED_USER)
            except Exception as e:
                self.logger.error(f"Error sending unauthorized user message: {e}")
            return

        # Get statistics from database
        daily_stats = self.database.get_stats_daily(user_id, chat_id)
        monthly_stats = self.database.get_stats_monthly(user_id, chat_id)
        all_time_stats = self.database.get_stats_all_time(user_id, chat_id)

        # Format and send statistics
        stats_message = self.messages.format_stats(
            daily_stats, monthly_stats, all_time_stats
        )

        try:
            await update.message.reply_text(
                stats_message,
                parse_mode=ParseMode.MARKDOWN,
            )
            self.logger.info(f"Stats requested by user {user_id} in chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Error sending stats message: {e}")

    async def reset_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /reset command - reset statistics for the requesting user."""
        if (
            not update.message
            or not update.effective_chat
            or not update.message.from_user
        ):
            return

        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Unknown"

        # Check if bot is active in this chat
        if not self.state_manager.is_active(chat_id):
            try:
                await update.message.reply_text(self.messages.BOT_NOT_ACTIVE)
            except Exception as e:
                self.logger.error(f"Error sending bot not active message: {e}")
            return

        # Check if user is allowed to use the bot
        if (
            self.allowed_handles
            and len(self.allowed_handles) > 0
            and not self._is_allowed(update)
        ):
            try:
                await update.message.reply_text(self.messages.UNAUTHORIZED_USER)
            except Exception as e:
                self.logger.error(f"Error sending unauthorized user message: {e}")
            return

        # Reset user's statistics
        success = self.database.reset_user_stats(user_id, chat_id)

        if success:
            try:
                await update.message.reply_text(self.messages.RESET_SUCCESS)
                self.logger.info(
                    f"Stats reset by user {username} (ID: {user_id}) in chat {chat_id}"
                )
            except Exception as e:
                self.logger.error(f"Error sending reset success message: {e}")
        else:
            try:
                await update.message.reply_text(self.messages.RESET_ERROR)
            except Exception as e:
                self.logger.error(f"Error sending reset error message: {e}")

    async def group_reset_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /group_reset command - reset statistics for entire group (admin only)."""
        if not update.message or not update.effective_chat:
            return

        chat_id = update.effective_chat.id

        # Check if bot is active in this chat
        if not self.state_manager.is_active(chat_id):
            try:
                await update.message.reply_text(self.messages.BOT_NOT_ACTIVE)
            except Exception as e:
                self.logger.error(f"Error sending bot not active message: {e}")
            return

        # Check if user is an admin (required for group reset)
        if (
            self.admin_handles
            and len(self.admin_handles) > 0
            and not self._is_admin(update)
        ):
            try:
                await update.message.reply_text(self.messages.UNAUTHORIZED_ADMIN)
            except Exception as e:
                self.logger.error(f"Error sending unauthorized admin message: {e}")
            username = update.message.from_user.username or "Unknown"
            self.logger.warning(
                f"Unauthorized group_reset attempt by user {username} "
                f"(ID: {update.message.from_user.id}) in chat {chat_id}"
            )
            return

        # Reset all statistics for this chat
        success = self.database.reset_chat_stats(chat_id)

        if success:
            try:
                await update.message.reply_text(self.messages.GROUP_RESET_SUCCESS)
                username = update.message.from_user.username or "Unknown"
                self.logger.info(
                    f"Group stats reset by admin {username} (ID: {update.message.from_user.id}) "
                    f"in chat {chat_id}"
                )
            except Exception as e:
                self.logger.error(f"Error sending group reset success message: {e}")
        else:
            try:
                await update.message.reply_text(self.messages.GROUP_RESET_ERROR)
            except Exception as e:
                self.logger.error(f"Error sending group reset error message: {e}")

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming messages and detect filler words."""
        if not update.message or not update.message.text or not update.effective_chat:
            return

        if not update.message.from_user:
            return

        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Unknown"

        # Check if bot is active in this chat
        if not self.state_manager.is_active(chat_id):
            self.logger.debug(f"Bot is not active in chat {chat_id}, ignoring message")
            return

        # Check if user is allowed to use the bot
        if (
            self.allowed_handles
            and len(self.allowed_handles) > 0
            and not self._is_allowed(update)
        ):
            self.logger.debug(f"Message from unauthorized user {username} ignored")
            return

        text = update.message.text

        # Detect filler words in the message
        detected_words = self.detector.detect_filler_words(text)

        if detected_words:
            # Record each filler word in the database
            for word in detected_words:
                self.database.record_filler_word(user_id, chat_id, word)

            # Notify the user about detected filler words
            unique_words = list(set(detected_words))
            words_text = ", ".join(f"*{word}*" for word in unique_words)

            notification = self.messages.FILLER_WORD_DETECTED.format(words=words_text)

            try:
                await update.message.reply_text(
                    notification,
                    parse_mode=ParseMode.MARKDOWN,
                )
                self.logger.info(
                    f"Filler words detected from user {username} (ID: {user_id}) "
                    f"in chat {chat_id}: {detected_words}"
                )
            except Exception as e:
                self.logger.error(f"Error sending filler word notification: {e}")

    def _is_admin(self, update: Update) -> bool:
        """Check if the user is an admin."""
        if not update.message or not update.message.from_user:
            return False

        username = update.message.from_user.username
        if not username:
            return False

        # Handle both with and without @ prefix
        handle_with_at = "@" + username

        return (
            (username in self.admin_handles or handle_with_at in self.admin_handles)
            if self.admin_handles
            else False
        )

    def _is_allowed(self, update: Update) -> bool:
        """Check if the user is allowed to use the bot."""
        if not update.message or not update.message.from_user:
            return False

        username = update.message.from_user.username
        if not username:
            return False

        # Handle both with and without @ prefix
        handle_with_at = "@" + username

        return (
            (username in self.allowed_handles or handle_with_at in self.allowed_handles)
            if self.allowed_handles
            else False
        )
