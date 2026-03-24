"""
Intent router for natural language queries.

Routes user messages to the LLM, executes tool calls, and feeds results back.
This is the core of the natural language interface.

Tool calling loop:
1. Send user message + system prompt + tools to LLM
2. LLM returns tool calls (or direct answer)
3. Execute each tool call, collect results
4. Feed tool results back to LLM
5. LLM produces final answer
"""

import asyncio
import json
import sys
from typing import Any

from config import get_settings
from services.llm_client import LLMClient, get_llm_client
from services.lms_api import LMSAPIClient, get_api_client


# System prompt tells the LLM how to behave
SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System (LMS).
You help users get information about labs, scores, learners, and analytics.

You have access to tools that fetch data from the LMS backend.
When a user asks a question, use the tools to get the data, then provide a clear, helpful answer.

For multi-step queries (like "which lab has the lowest pass rate"):
1. First get the list of labs
2. Then get data for each lab
3. Compare and provide the answer

Always be specific and include numbers from the data. If you don't have enough information, ask for clarification.

If the user's message is a greeting or doesn't require data, respond naturally without using tools.
If the message is unclear or seems like gibberish, politely ask for clarification and suggest what you can help with.
"""


class IntentRouter:
    """Routes natural language queries to backend tools via LLM."""

    def __init__(self) -> None:
        """Initialize the intent router with LLM and API clients."""
        settings = get_settings()
        self.llm_client = get_llm_client(
            settings.llm_api_base_url or "",
            settings.llm_api_key or "",
            settings.llm_api_model or "coder-model"
        )
        self.api_client = get_api_client(
            settings.lms_api_base_url,
            settings.lms_api_key or ""
        )
        self.tools = self.llm_client.get_tool_definitions()

    def _log(self, message: str) -> None:
        """Log debug message to stderr (visible in --test mode)."""
        print(f"[tool] {message}", file=sys.stderr)

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """
        Execute a tool call and return the result.

        Args:
            name: Tool/function name
            arguments: Arguments for the tool

        Returns:
            Tool execution result.
        """
        try:
            if name == "get_items":
                result = await self.api_client.get_labs()
            elif name == "get_learners":
                # Fetch all items and filter for learners if needed
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/learners/",
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "get_scores":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/analytics/scores",
                        params={"lab": arguments.get("lab", "")},
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "get_pass_rates":
                result = await self.api_client.get_pass_rates(arguments.get("lab", ""))
            elif name == "get_timeline":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/analytics/timeline",
                        params={"lab": arguments.get("lab", "")},
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "get_groups":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/analytics/groups",
                        params={"lab": arguments.get("lab", "")},
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "get_top_learners":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/analytics/top-learners",
                        params={
                            "lab": arguments.get("lab", ""),
                            "limit": arguments.get("limit", 5)
                        },
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "get_completion_rate":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.get(
                        f"{settings.lms_api_base_url}/analytics/completion-rate",
                        params={"lab": arguments.get("lab", "")},
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            elif name == "trigger_sync":
                async with __import__("httpx").AsyncClient() as client:
                    settings = get_settings()
                    response = await client.post(
                        f"{settings.lms_api_base_url}/pipeline/sync",
                        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    result = response.json()
            else:
                result = {"error": f"Unknown tool: {name}"}

            self._log(f"Result: {self._truncate_result(result)}")
            return result
        except Exception as e:
            self._log(f"Error executing {name}: {e}")
            return {"error": str(e)}

    def _truncate_result(self, result: Any, max_len: int = 200) -> str:
        """Truncate result for logging."""
        result_str = str(result)
        if len(result_str) > max_len:
            return result_str[:max_len] + "..."
        return result_str

    async def route(self, message: str) -> str:
        """
        Route a user message through the LLM tool calling loop.

        Args:
            message: User's natural language query

        Returns:
            Final response from the LLM.
        """
        # Initialize conversation with system prompt and user message
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        self._log(f"User message: {message}")

        # Tool calling loop - max 5 iterations to prevent infinite loops
        max_iterations = 5
        for iteration in range(max_iterations):
            self._log(f"Calling LLM (iteration {iteration + 1})")

            # Get LLM response
            response = await self.llm_client.chat(messages, self.tools)

            # Check if LLM returned tool calls
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - LLM has a final answer
                self._log(f"LLM returned final answer")
                return response.get("content", "I don't have an answer for that.")

            # Execute tool calls
            self._log(f"LLM called {len(tool_calls)} tool(s)")

            for tc in tool_calls:
                name = tc.get("name", "")
                try:
                    arguments = json.loads(tc.get("arguments", "{}"))
                except json.JSONDecodeError:
                    arguments = {}

                self._log(f"LLM called: {name}({arguments})")

                # Execute the tool
                result = await self._execute_tool(name, arguments)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })

            self._log(f"Feeding {len(tool_calls)} tool result(s) back to LLM")

        # If we get here, we hit max iterations
        return "I'm having trouble processing this query. Please try rephrasing."


# Singleton instance
_router: IntentRouter | None = None


def get_router() -> IntentRouter:
    """Get or create the intent router singleton."""
    global _router
    if _router is None:
        _router = IntentRouter()
    return _router


def handle_natural_language(message: str) -> str:
    """
    Handle a natural language query.

    This is the synchronous wrapper for use in handlers.

    Args:
        message: User's natural language query

    Returns:
        Response from the intent router.
    """
    router = get_router()
    return asyncio.run(router.route(message))
