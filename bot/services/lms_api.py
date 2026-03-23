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


class LMSAPIError(Exception):
    """Exception raised when the LMS API request fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


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

    def _get_headers(self) -> dict[str, str]:
        """Get headers with Bearer authentication."""
        return {"Authorization": f"Bearer {self.api_key}"}

    async def health_check(self) -> dict:
        """
        Check backend health status by fetching items.

        Returns:
            Health status dict with 'status' and 'message' keys.

        Raises:
            LMSAPIError: If the backend is unreachable or returns an error.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                item_count = len(data) if isinstance(data, list) else 0
                return {"status": "ok", "item_count": item_count}
        except httpx.ConnectError as e:
            raise LMSAPIError(
                f"connection refused ({self.base_url}). Check that the services are running.",
                e
            )
        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                e
            )
        except httpx.HTTPError as e:
            raise LMSAPIError(f"HTTP error: {str(e)}", e)
        except Exception as e:
            raise LMSAPIError(f"unexpected error: {str(e)}", e)

    async def get_labs(self) -> list[dict]:
        """
        Fetch all available labs from the backend.

        Returns:
            List of lab dictionaries with 'id', 'name', 'type' keys.

        Raises:
            LMSAPIError: If the backend is unreachable or returns an error.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                # Filter for labs (type might be "lab" or similar)
                if isinstance(data, list):
                    return [
                        item for item in data
                        if item.get("type") == "lab" or "lab" in item.get("name", "").lower()
                    ]
                return []
        except httpx.ConnectError as e:
            raise LMSAPIError(
                f"connection refused ({self.base_url}). Check that the services are running.",
                e
            )
        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                e
            )
        except httpx.HTTPError as e:
            raise LMSAPIError(f"HTTP error: {str(e)}", e)
        except Exception as e:
            raise LMSAPIError(f"unexpected error: {str(e)}", e)

    async def get_pass_rates(self, lab_id: str) -> dict:
        """
        Fetch pass rates for a specific lab.

        Args:
            lab_id: Lab identifier (e.g., "lab-04")

        Returns:
            Dictionary with task names and pass rates.

        Raises:
            LMSAPIError: If the backend is unreachable or returns an error.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/analytics/pass-rates",
                    params={"lab": lab_id},
                    headers=self._get_headers(),
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise LMSAPIError(
                f"connection refused ({self.base_url}). Check that the services are running.",
                e
            )
        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                e
            )
        except httpx.HTTPError as e:
            raise LMSAPIError(f"HTTP error: {str(e)}", e)
        except Exception as e:
            raise LMSAPIError(f"unexpected error: {str(e)}", e)


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
