"""Tests for ChatState and ChatStateManager."""

from bot.chat_state import ChatState, ChatStateManager


def test_chat_state_toggle():
    """Test toggling chat state."""
    state = ChatState()

    assert state.is_active is False
    assert state.toggle_active() is True
    assert state.is_active is True


def test_chat_state_manager():
    """Test managing multiple chat states."""
    manager = ChatStateManager()

    manager.set_active(123, True)
    manager.set_active(456, False)

    assert manager.is_active(123) is True
    assert manager.is_active(456) is False
