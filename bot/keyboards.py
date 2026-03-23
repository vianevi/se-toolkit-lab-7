"""
Inline keyboard definitions for the Telegram bot.

Keyboards provide quick action buttons so users can discover actions
without typing. Each keyboard is a list of button rows.

Used with aiogram's InlineKeyboardMarkup.
"""


def get_start_keyboard() -> list[list[dict[str, str]]]:
    """
    Get inline keyboard for /start message.

    Shows common actions users might want to take.

    Returns:
        List of button rows for InlineKeyboardMarkup.
    """
    return [
        [
            {"text": "📚 Available Labs", "callback_data": "labs"},
            {"text": "📊 Health Check", "callback_data": "health"}
        ],
        [
            {"text": "🏆 Top Learners", "callback_data": "top_learners"},
            {"text": "📈 Completion Rates", "callback_data": "completion"}
        ],
        [
            {"text": "❓ Help", "callback_data": "help"}
        ]
    ]


def get_lab_actions_keyboard(lab_id: str) -> list[list[dict[str, str]]]:
    """
    Get inline keyboard for lab-specific actions.

    Args:
        lab_id: Lab identifier (e.g., "lab-04")

    Returns:
        List of button rows for InlineKeyboardMarkup.
    """
    return [
        [
            {"text": "📊 Pass Rates", "callback_data": f"scores_{lab_id}"},
            {"text": "📈 Timeline", "callback_data": f"timeline_{lab_id}"}
        ],
        [
            {"text": "👥 Groups", "callback_data": f"groups_{lab_id}"},
            {"text": "🏆 Top Learners", "callback_data": f"top_{lab_id}"}
        ],
        [
            {"text": "✅ Completion Rate", "callback_data": f"completion_{lab_id}"}
        ]
    ]


def get_help_keyboard() -> list[list[dict[str, str]]]:
    """
    Get inline keyboard for /help message.

    Returns:
        List of button rows for InlineKeyboardMarkup.
    """
    return [
        [
            {"text": "📚 View Labs", "callback_data": "labs"},
            {"text": "📊 Health Check", "callback_data": "health"}
        ]
    ]


def get_back_keyboard() -> list[list[dict[str, str]]]:
    """
    Get a simple back button keyboard.

    Returns:
        List of button rows with just a back button.
    """
    return [
        [{"text": "🔙 Back", "callback_data": "back"}]
    ]
