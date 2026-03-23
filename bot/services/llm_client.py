"""
LLM client for intent recognition.

Sends user messages to the LLM and receives responses.
In Task 3, this client will use tool calling to let the LLM decide which API to call.

Why async?
- LLM calls can be slow (several seconds)
- Async doesn't block the bot while waiting for a response
- Multiple users can be handled concurrently
"""

from typing import Any


class LLMClient:
    """Client for LLM API interactions."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """
        Initialize the LLM client.
        
        Args:
            base_url: LLM API base URL
            api_key: API key for authentication
            model: Model name to use (e.g., "coder-model")
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def chat(self, message: str, tools: list[dict] | None = None) -> dict[str, Any]:
        """
        Send a message to the LLM and get a response.
        
        Args:
            message: User's message text
            tools: Optional list of tool definitions for function calling
            
        Returns:
            LLM response with content and/or tool calls.
        """
        # TODO: Implement LLM API call (Task 3)
        return {
            "content": f"LLM response to: {message}",
            "tool_calls": []
        }

    def get_tool_definitions(self) -> list[dict]:
        """
        Get tool definitions for the LLM.
        
        Tools tell the LLM what actions it can take.
        The LLM reads these descriptions to decide which tool to call.
        
        Returns:
            List of tool definition dictionaries.
        """
        # TODO: Define tools for /health, /labs, /scores, etc. (Task 3)
        return []


# Singleton instance
_llm_client: LLMClient | None = None


def get_llm_client(base_url: str, api_key: str, model: str) -> LLMClient:
    """
    Get or create the LLM client singleton.
    
    Args:
        base_url: LLM API base URL
        api_key: API key for authentication
        model: Model name to use
        
    Returns:
        LLMClient instance.
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(base_url, api_key, model)
    return _llm_client
