"""
Main entry point for the Filler Words Detector Bot.
"""

import logging
from decouple import config
from bot.telegram_filler_bot import TelegramFillerBot


def main():
    """Initialize and run the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    telegram_token = config("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        logging.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Get filler words from environment variable
    filler_words_str = config("FILLER_WORDS", default="")
    filler_words = [
        word.strip() for word in filler_words_str.split(",") if word.strip()
    ]

    if not filler_words:
        logging.warning(
            "No filler words configured! Set FILLER_WORDS environment variable."
        )
        filler_words = []

    # Get allowed and admin handles
    allowed_handles_str = config("ALLOWED_HANDLES", default="")
    allowed_handles = [
        h.strip() for h in allowed_handles_str.split(",") if h.strip()
    ] or None

    admin_handles_str = config("ADMIN_HANDLES", default="")
    admin_handles = [
        h.strip() for h in admin_handles_str.split(",") if h.strip()
    ] or None

    # Get database path
    db_path = config("DATABASE_PATH", default="filler_words.db")

    # Initialize and run the bot
    tg_bot = TelegramFillerBot(
        telegram_token=telegram_token,
        filler_words=filler_words,
        db_path=db_path,
        allowed_handles=allowed_handles,
        admin_handles=admin_handles,
        logger=logging.getLogger("FillerWordsBot"),
    )

    logging.info(f"Bot configured with filler words: {', '.join(filler_words)}")
    tg_bot.run()


if __name__ == "__main__":
    main()
