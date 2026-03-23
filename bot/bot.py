#!/usr/bin/env python3
"""
Telegram bot entry point.

Supports two modes:
- Normal mode: Connects to Telegram and listens for messages
- Test mode (--test): Calls handlers directly from CLI for offline testing

Usage:
    uv run bot.py                    # Start Telegram bot
    uv run bot.py --test "/start"    # Test a command offline
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path so we can import handlers
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import get_settings
from handlers.slash.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
from services.intent_router import handle_natural_language

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_test_mode(command: str) -> None:
    """
    Run a command in test mode - calls the handler directly and prints result.

    Args:
        command: The command to test (e.g., "/start", "/help", "/health")
    """
    # Check if this is a slash command or natural language
    if command.strip().startswith("/"):
        # Slash command - route to command handlers
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None

        # Route to appropriate handler
        if cmd == "/start":
            response = handle_start()
        elif cmd == "/help":
            response = handle_help()
        elif cmd == "/health":
            response = handle_health()
        elif cmd == "/labs":
            response = handle_labs()
        elif cmd == "/scores":
            response = handle_scores(arg)
        else:
            response = f"Unknown command: {cmd}. Use /help to see available commands."
    else:
        # Natural language query - use intent router
        response = handle_natural_language(command)

    print(response)


async def start_command(message: types.Message) -> None:
    """Handle /start command."""
    response = handle_start()
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Available Labs", callback_data="labs"),
                InlineKeyboardButton(text="📊 Health Check", callback_data="health")
            ],
            [
                InlineKeyboardButton(text="❓ Help", callback_data="help")
            ]
        ]
    )
    await message.answer(response, reply_markup=keyboard)


async def help_command(message: types.Message) -> None:
    """Handle /help command."""
    response = handle_help()
    await message.answer(response)


async def health_command(message: types.Message) -> None:
    """Handle /health command."""
    response = handle_health()
    await message.answer(response)


async def labs_command(message: types.Message) -> None:
    """Handle /labs command."""
    response = handle_labs()
    await message.answer(response)


async def scores_command(message: types.Message) -> None:
    """Handle /scores command."""
    args = message.text.split(maxsplit=1)
    lab = args[1] if len(args) > 1 else None
    response = handle_scores(lab)
    await message.answer(response)


async def handle_message(message: types.Message) -> None:
    """Handle natural language messages."""
    if message.text:
        response = handle_natural_language(message.text)
        await message.answer(response)


async def handle_callback(message: types.CallbackQuery) -> None:
    """Handle inline keyboard callbacks."""
    action = message.data
    
    if action == "labs":
        response = handle_labs()
    elif action == "health":
        response = handle_health()
    elif action == "help":
        response = handle_help()
    else:
        response = "Unknown action"
    
    await message.message.answer(response)
    await message.answer()


async def run_telegram_bot() -> None:
    """Run the Telegram bot."""
    settings = get_settings()
    
    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set. Cannot start Telegram bot.")
        sys.exit(1)
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Register handlers
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(health_command, Command("health"))
    dp.message.register(labs_command, Command("labs"))
    dp.message.register(scores_command, Command("scores"))
    dp.message.register(handle_message)  # For natural language messages
    dp.callback_query.register(handle_callback)
    
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command (e.g., --test '/start')"
    )

    args = parser.parse_args()

    if args.test:
        # Test mode: call handlers directly
        run_test_mode(args.test)
    else:
        # Normal mode: start Telegram bot
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
