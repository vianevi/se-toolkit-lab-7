"""
Command handlers for slash commands: /start, /help, /health, /labs, /scores.

Each handler is a pure function: takes input, returns text response.
No Telegram dependencies here - makes testing easy.

Handlers use the LMS API client to fetch real data from the backend.
Errors are caught and returned as friendly messages (not tracebacks).
"""

import asyncio

from config import get_settings
from services.lms_api import LMSAPIClient, LMSAPIError, get_api_client


def handle_start() -> str:
    """
    Handle /start command.

    Returns:
        Welcome message for new users.
    """
    return """Welcome to the LMS Bot! 🎓

I can help you check your lab scores, view available labs, and get system status.

Quick actions:
• /labs - See all available labs
• /health - Check system status
• /scores <lab> - Get scores for a lab

Or just ask me a question like "which lab has the lowest pass rate?"

Use /help to see all available commands."""


def handle_help() -> str:
    """
    Handle /help command.

    Returns:
        List of available commands with descriptions.
    """
    return """Available commands:

/start - Welcome message and introduction
/help - Show this help message
/health - Check backend system status
/labs - List all available labs
/scores <lab> - Get scores for a specific lab (e.g., /scores lab-04)

You can also ask questions in plain language (coming soon)."""


def _fetch_health() -> str:
    """
    Fetch backend health status asynchronously.

    Returns:
        Formatted health status message.
    """
    settings = get_settings()
    client = get_api_client(settings.lms_api_base_url, settings.lms_api_key or "")
    
    try:
        result = asyncio.run(client.health_check())
        return f"Backend is healthy. {result['item_count']} items available."
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


def handle_health() -> str:
    """
    Handle /health command.

    Returns:
        Backend health status with item count, or error message.
    """
    return _fetch_health()


def _fetch_labs() -> str:
    """
    Fetch labs from backend asynchronously.

    Returns:
        Formatted list of available labs.
    """
    settings = get_settings()
    client = get_api_client(settings.lms_api_base_url, settings.lms_api_key or "")
    
    try:
        labs = asyncio.run(client.get_labs())
        if not labs:
            return "No labs available. The backend may be empty or the data hasn't been synced yet."
        
        lines = ["Available labs:"]
        for lab in labs:
            lab_name = lab.get("title", lab.get("name", "Unknown"))
            lab_id = lab.get("id", "unknown")
            lines.append(f"- {lab_name}")
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


def handle_labs() -> str:
    """
    Handle /labs command.

    Returns:
        List of available labs from the backend.
    """
    return _fetch_labs()


def _fetch_scores(lab: str) -> str:
    """
    Fetch scores for a specific lab asynchronously.

    Args:
        lab: Lab identifier (e.g., "lab-04")

    Returns:
        Formatted pass rates for each task.
    """
    settings = get_settings()
    client = get_api_client(settings.lms_api_base_url, settings.lms_api_key or "")
    
    try:
        data = asyncio.run(client.get_pass_rates(lab))
        
        # The API returns a list of task pass rates
        if not data:
            return f"No scores found for {lab}. The lab may not exist or has no submissions."
        
        lines = [f"Pass rates for {lab}:"]
        for item in data:
            task_name = item.get("task", item.get("task_name", "Unknown"))
            # API returns avg_score, use pass_rate as fallback
            score = item.get("avg_score", item.get("pass_rate", 0))
            attempts = item.get("attempts", 0)
            lines.append(f"- {task_name}: {score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


def handle_scores(lab: str | None = None) -> str:
    """
    Handle /scores command.

    Args:
        lab: Optional lab identifier (e.g., "lab-04").

    Returns:
        Score information for the specified lab or usage instructions.
    """
    if not lab:
        return "Usage: /scores <lab>\nExample: /scores lab-04"
    
    return _fetch_scores(lab)
