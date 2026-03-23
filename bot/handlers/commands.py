"""
Command handlers for slash commands: /start, /help, /health, /labs, /scores.

Each handler is a pure function: takes input, returns text response.
No Telegram dependencies here - makes testing easy.
"""


def handle_start() -> str:
    """
    Handle /start command.
    
    Returns:
        Welcome message for new users.
    """
    return "Welcome to the LMS Bot! 🎓\n\nI can help you check your lab scores, view available labs, and get system status. Use /help to see all available commands."


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


def handle_health() -> str:
    """
    Handle /health command.
    
    Returns:
        Backend health status.
    
    Note: Currently returns placeholder. Task 2 will add real API calls.
    """
    # TODO: Call backend API and return real status (Task 2)
    return "Backend status: OK (placeholder - will connect to real backend in Task 2)"


def handle_labs() -> str:
    """
    Handle /labs command.
    
    Returns:
        List of available labs.
    
    Note: Currently returns placeholder. Task 2 will fetch from backend.
    """
    # TODO: Fetch labs from backend API (Task 2)
    return "Available labs:\n- Lab 01: Introduction\n- Lab 02: Setup\n- Lab 03: Testing\n- Lab 04: Deployment\n\n(placeholder - will fetch real data in Task 2)"


def handle_scores(lab: str | None = None) -> str:
    """
    Handle /scores command.
    
    Args:
        lab: Optional lab identifier (e.g., "lab-04").
    
    Returns:
        Score information for the specified lab or general scores.
    
    Note: Currently returns placeholder. Task 2 will fetch from backend.
    """
    # TODO: Fetch scores from backend API (Task 2)
    if lab:
        return f"Scores for {lab}:\n- Task 1: 100%\n- Task 2: 85%\n- Task 3: 92%\n\n(placeholder - will fetch real data in Task 2)"
    else:
        return "Usage: /scores <lab>\nExample: /scores lab-04\n\n(placeholder - will fetch real data in Task 2)"
