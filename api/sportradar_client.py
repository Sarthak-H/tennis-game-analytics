"""
Official SportRadar Tennis API Client.
Handles authentication, rate limits (1 req/sec on trial plans), retries with
exponential backoff, error inspection, and JSON response verification.
"""

import time
import logging
import requests
from typing import Dict, Any, Optional
from config import (
    SPORTRADAR_API_KEY,
    SPORTRADAR_BASE_URL,
    API_REQUEST_DELAY,
    API_TIMEOUT,
    API_MAX_RETRIES
)

logger = logging.getLogger(__name__)


class SportRadarAPIError(Exception):
    """Custom exception for SportRadar API failures."""
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint

    def __str__(self):
        code_str = f" [HTTP {self.status_code}]" if self.status_code else ""
        end_str = f" for '{self.endpoint}'" if self.endpoint else ""
        return f"SportRadarAPIError{code_str}{end_str}: {self.message}"


class SportRadarClient:
    """
    HTTP Client for interacting with Sportradar Tennis v3 endpoints.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = (api_key or SPORTRADAR_API_KEY).strip()
        self.base_url = (base_url or SPORTRADAR_BASE_URL).rstrip("/")
        self.last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "TennisAnalyticsApp/1.0"
        })

    def _apply_rate_limit(self):
        """Enforces minimum interval between consecutive API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < API_REQUEST_DELAY:
            sleep_duration = API_REQUEST_DELAY - elapsed
            time.sleep(sleep_duration)

    def request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes an authenticated GET request with rate-limiting, retries, and error handling.
        """
        if not self.api_key:
            raise SportRadarAPIError(
                "SportRadar API Key is not configured. Please supply an API key in your .env file "
                "or via the Data Management settings page."
            )

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        query_params = dict(params or {})
        # Support both query param authentication and header authentication for Sportradar
        query_params["api_key"] = self.api_key
        headers = {"x-api-key": self.api_key}

        retries = 0
        backoff = 2.0

        while retries <= API_MAX_RETRIES:
            self._apply_rate_limit()
            try:
                self.last_request_time = time.time()
                logger.info(f"Dispatching GET request to: {self.base_url}/{endpoint.lstrip('/')}")
                response = self.session.get(
                    url,
                    params=query_params,
                    headers=headers,
                    timeout=API_TIMEOUT
                )

                # Check HTTP Status Codes
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError as err:
                        raise SportRadarAPIError(
                            f"Invalid JSON returned from endpoint: {err}",
                            status_code=response.status_code,
                            endpoint=endpoint
                        )

                elif response.status_code == 401 or response.status_code == 403:
                    raise SportRadarAPIError(
                        "Authentication Failed: Invalid SportRadar API Key or access forbidden. "
                        "Verify your key at https://console.sportradar.com/.",
                        status_code=response.status_code,
                        endpoint=endpoint
                    )

                elif response.status_code == 429:
                    # Rate limit exceeded
                    retries += 1
                    if retries > API_MAX_RETRIES:
                        raise SportRadarAPIError(
                            "SportRadar Rate Limit Exceeded (429): Maximum retry attempts reached.",
                            status_code=429,
                            endpoint=endpoint
                        )
                    logger.warning(f"Rate limited (429). Retrying in {backoff} seconds (Attempt {retries}/{API_MAX_RETRIES})...")
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue

                elif response.status_code >= 500:
                    retries += 1
                    if retries > API_MAX_RETRIES:
                        raise SportRadarAPIError(
                            f"SportRadar Server Error: Received status {response.status_code}.",
                            status_code=response.status_code,
                            endpoint=endpoint
                        )
                    logger.warning(f"Server error ({response.status_code}). Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 1.5
                    continue

                else:
                    raise SportRadarAPIError(
                        f"Unexpected API response: {response.status_code} - {response.text[:200]}",
                        status_code=response.status_code,
                        endpoint=endpoint
                    )

            except requests.exceptions.Timeout:
                retries += 1
                if retries > API_MAX_RETRIES:
                    raise SportRadarAPIError(
                        f"Request timed out after {API_TIMEOUT}s.",
                        endpoint=endpoint
                    )
                logger.warning(f"Timeout on {endpoint}. Retrying in {backoff}s...")
                time.sleep(backoff)
            except requests.exceptions.RequestException as exc:
                raise SportRadarAPIError(
                    f"Network communication failed: {exc}",
                    endpoint=endpoint
                )

        raise SportRadarAPIError("Maximum retries exhausted without a successful response.", endpoint=endpoint)

    def test_connection(self) -> Dict[str, Any]:
        """
        Tests API connectivity by attempting to fetch competitions endpoint.
        Returns a dict with success boolean and details.
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "API key is not configured.",
                "status_code": 401
            }
        try:
            from config import ENDPOINT_COMPETITIONS
            data = self.request(ENDPOINT_COMPETITIONS)
            return {
                "success": True,
                "message": "Connection to SportRadar Tennis API successful!",
                "data_keys": list(data.keys()) if isinstance(data, dict) else []
            }
        except SportRadarAPIError as exc:
            return {
                "success": False,
                "message": str(exc.message),
                "status_code": exc.status_code
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Unexpected error during connection test: {exc}",
                "status_code": None
            }

