"""
LLM client for intent recognition and tool calling.

Sends user messages to the LLM and receives responses with tool calls.
The LLM decides which backend API to call based on the user's intent.

Tool calling pattern:
1. Send user message + tool definitions to LLM
2. LLM returns tool calls (which function to call with what args)
3. Execute the tools, get results
4. Feed results back to LLM
5. LLM produces final answer
"""

import httpx
from typing import Any


class LLMClient:
    """Client for LLM API interactions with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """
        Initialize the LLM client.

        Args:
            base_url: LLM API base URL (OpenAI-compatible)
            api_key: API key for authentication
            model: Model name to use (e.g., "coder-model")
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None
    ) -> dict[str, Any]:
        """
        Send messages to the LLM and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            tools: Optional list of tool definitions for function calling

        Returns:
            LLM response with 'content' and/or 'tool_calls' keys.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                # Extract tool calls if present
                tool_calls = []
                for tc in message.get("tool_calls", []):
                    tool_calls.append({
                        "id": tc.get("id"),
                        "name": tc.get("function", {}).get("name"),
                        "arguments": tc.get("function", {}).get("arguments", "{}")
                    })
                
                return {
                    "content": message.get("content", ""),
                    "tool_calls": tool_calls
                }
        except httpx.HTTPStatusError as e:
            return {
                "content": f"LLM error: HTTP {e.response.status_code}. The AI service may be unavailable.",
                "tool_calls": []
            }
        except httpx.ConnectError as e:
            return {
                "content": f"LLM connection error: {str(e)}. Check that the LLM service is running.",
                "tool_calls": []
            }
        except Exception as e:
            return {
                "content": f"LLM error: {str(e)}",
                "tool_calls": []
            }

    def get_tool_definitions(self) -> list[dict]:
        """
        Get all tool definitions for the LLM.

        These 9 tools cover all backend endpoints. The LLM reads these
        descriptions to decide which tool to call for a given query.

        Returns:
            List of tool definition dictionaries.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get the list of all labs and tasks available in the LMS. Use this to find what labs exist or to get lab IDs.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get the list of enrolled students/learners. Use this to find information about students or count enrollments.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed across ranges.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a specific lab. Use this to see how students performed on each task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline (submissions per day) for a specific lab. Use this to see when students submitted their work.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group performance scores and student counts for a specific lab. Use this to compare how different groups performed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a specific lab. Use this to find the best performing students.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                            "limit": {"type": "integer", "description": "Number of top learners to return, e.g., 5"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a specific lab. Use this to see what percentage of students completed the lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger the ETL pipeline to sync data from the autochecker API. Use this when the user wants to refresh or update the data.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]


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
