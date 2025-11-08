"""
Chat state management for the Telegram Filler Words Bot.
Stores per-chat settings in memory.
"""

from typing import Dict


class ChatState:
    """State for a single chat."""

    def __init__(self):
        """Initialize chat state with default values."""
        self.is_active: bool = False

    def toggle_active(self) -> bool:
        """Toggle the active state and return the new state."""
        self.is_active = not self.is_active
        return self.is_active

    def set_active(self, active: bool) -> None:
        """Set the active state."""
        self.is_active = active


class ChatStateManager:
    """Manages state for all chats."""

    def __init__(self):
        """Initialize the state manager."""
        self._states: Dict[int, ChatState] = {}

    def get_state(self, chat_id: int) -> ChatState:
        """
        Get the state for a chat, creating it if it doesn't exist.

        Args:
            chat_id: The Telegram chat ID

        Returns:
            The ChatState for this chat
        """
        if chat_id not in self._states:
            self._states[chat_id] = ChatState()
        return self._states[chat_id]

    def is_active(self, chat_id: int) -> bool:
        """Check if the bot is active in a chat."""
        return self.get_state(chat_id).is_active

    def set_active(self, chat_id: int, active: bool) -> None:
        """Set whether the bot is active in a chat."""
        self.get_state(chat_id).set_active(active)
