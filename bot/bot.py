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
import sys
from pathlib import Path

# Add parent directory to path so we can import handlers
sys.path.insert(0, str(Path(__file__).parent))

from handlers.slash.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
from services.intent_router import handle_natural_language


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
        # TODO: Implement Telegram bot startup (Task 2+)
        print("Starting Telegram bot... (not yet implemented)")
        print("Use --test mode for offline testing:")
        print("  uv run bot.py --test '/start'")


if __name__ == "__main__":
    main()
