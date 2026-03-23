"""
Service clients for the LMS bot.

Services handle external dependencies:
- LMS API client: Fetches labs, scores, analytics from backend
- LLM client: Sends requests to the AI model for intent recognition

Services are separate from handlers - handlers orchestrate, services make API calls.
"""
