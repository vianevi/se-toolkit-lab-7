"""
LMS API client.

Makes HTTP requests to the backend API with Bearer token authentication.
All API calls go through this client - makes testing and error handling centralized.

Why a client class?
- Centralized error handling
- Consistent authentication (Bearer token)
- Easy to mock in tests
- Base URL from config, not hardcoded
"""

import httpx


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Initialize the API client.
        
        Args:
            base_url: Backend API base URL (e.g., http://localhost:42002)
            api_key: API key for Bearer authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get headers with Bearer authentication."""
        return {"Authorization": f"Bearer {self.api_key}"}

    async def health_check(self) -> dict:
        """
        Check backend health status.
        
        Returns:
            Health status dict with 'status' and 'message' keys.
        """
        # TODO: Implement real health check endpoint call (Task 2)
        return {"status": "ok", "message": "Backend is healthy"}

    async def get_labs(self) -> list[dict]:
        """
        Fetch all available labs.
        
        Returns:
            List of lab dictionaries.
        """
        # TODO: Implement GET /items or similar endpoint (Task 2)
        return []

    async def get_scores(self, lab_id: str) -> dict:
        """
        Fetch scores for a specific lab.
        
        Args:
            lab_id: Lab identifier (e.g., "lab-04")
            
        Returns:
            Score data dictionary.
        """
        # TODO: Implement scores endpoint call (Task 2)
        return {"lab_id": lab_id, "scores": []}

    async def close(self) -> None:
        """Close the HTTP client session."""
        if self._client:
            await self._client.aclose()


# Singleton instance - created when config is available
_api_client: LMSAPIClient | None = None


def get_api_client(base_url: str, api_key: str) -> LMSAPIClient:
    """
    Get or create the API client singleton.
    
    Args:
        base_url: Backend API base URL
        api_key: API key for authentication
        
    Returns:
        LMSAPIClient instance.
    """
    global _api_client
    if _api_client is None:
        _api_client = LMSAPIClient(base_url, api_key)
    return _api_client
