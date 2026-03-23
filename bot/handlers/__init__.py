"""
Command handlers for the LMS Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - same function works from:
- --test mode (CLI)
- Unit tests
- Telegram bot

This is separation of concerns: handler logic is separate from transport.
"""

from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores

__all__ = [
    "handle_start",
    "handle_help", 
    "handle_health",
    "handle_labs",
    "handle_scores",
]
