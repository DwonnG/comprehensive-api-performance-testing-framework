"""
Async API client for high-performance concurrent testing.

This module provides async HTTP client capabilities for performance testing
with proper connection pooling, timeout handling, and error management.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class AsyncAPIClientError(Exception):
    """Base exception for async API client errors."""

    pass


class AsyncAPITimeoutError(AsyncAPIClientError):
    """Raised when async API requests timeout."""

    pass


class AsyncAPIConnectionError(AsyncAPIClientError):
    """Raised when async API connection fails."""

    pass


class AsyncAPIClient:
    """
    High-performance async API client for concurrent testing.

    Features:
    - Connection pooling for optimal performance
    - Automatic retry with exponential backoff
    - Comprehensive metrics collection
    - Timeout and error handling
    - Context manager support for proper cleanup
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        connector_limit: int = 100,
        connector_limit_per_host: int = 30,
    ):
        """
        Initialize async API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            connector_limit: Total connection pool limit
            connector_limit_per_host: Connection limit per host
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries

        # Configure connection pooling for high performance
        self.connector = aiohttp.TCPConnector(
            limit=connector_limit,
            limit_per_host=connector_limit_per_host,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        # Session will be created in async context
        self.session: Optional[aiohttp.ClientSession] = None

        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Comprehensive-Performance-Testing/1.0",
        }

        logger.info(f"Initialized async API client for {self.base_url}")

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            connector=self.connector, timeout=self.timeout, headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[int, Dict[str, Any], float]:
        """
        Make async HTTP request with retry logic and metrics.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            headers: Additional headers
            **kwargs: Additional arguments

        Returns:
            Tuple of (status_code, response_data, duration)

        Raises:
            AsyncAPITimeoutError: If request times out
            AsyncAPIConnectionError: If connection fails
            AsyncAPIClientError: For other API-related errors
        """
        if not self.session:
            raise AsyncAPIClientError(
                "Session not initialized. Use async context manager."
            )

        url = self._build_url(endpoint)
        start_time = time.time()

        try:
            # Merge headers if provided
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)

            logger.debug(f"Making async {method} request to {url}")

            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                **kwargs,
            ) as response:
                duration = time.time() - start_time

                try:
                    response_data = await response.json()
                except aiohttp.ContentTypeError:
                    response_data = {"text": await response.text()}

                logger.debug(
                    f"Async {method} {url} - Status: {response.status}, "
                    f"Duration: {duration:.3f}s"
                )

                return response.status, response_data, duration

        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            logger.error(f"Async request timeout after {duration:.3f}s: {url}")
            raise AsyncAPITimeoutError(f"Request to {url} timed out") from e

        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            logger.error(f"Async connection error after {duration:.3f}s: {url}")
            raise AsyncAPIConnectionError(f"Failed to connect to {url}") from e

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Unexpected async error after {duration:.3f}s: {url} - {e}")
            raise AsyncAPIClientError(f"Unexpected error for {url}: {e}") from e

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[int, Dict[str, Any], float]:
        """Make async GET request."""
        return await self._make_request(
            "GET", endpoint, params=params, headers=headers, **kwargs
        )

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[int, Dict[str, Any], float]:
        """Make async POST request."""
        return await self._make_request(
            "POST", endpoint, data=data, params=params, headers=headers, **kwargs
        )

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[int, Dict[str, Any], float]:
        """Make async PUT request."""
        return await self._make_request(
            "PUT", endpoint, data=data, params=params, headers=headers, **kwargs
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Tuple[int, Dict[str, Any], float]:
        """Make async DELETE request."""
        return await self._make_request(
            "DELETE", endpoint, params=params, headers=headers, **kwargs
        )

    async def health_check(self) -> bool:
        """
        Perform async health check.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            status, _, _ = await self.get("/")
            return status < 500
        except Exception as e:
            logger.warning(f"Async health check failed for {self.base_url}: {e}")
            return False


class AsyncJSONPlaceholderClient(AsyncAPIClient):
    """Async client for JSONPlaceholder API performance testing."""

    def __init__(
        self, base_url: str = "https://jsonplaceholder.typicode.com", **kwargs
    ):
        super().__init__(base_url, **kwargs)

    async def get_posts(
        self, user_id: Optional[int] = None
    ) -> Tuple[int, Dict[str, Any], float]:
        """Get posts with optional user filtering."""
        params = {"userId": user_id} if user_id else None
        return await self.get("/posts", params=params)

    async def get_post(self, post_id: int) -> Tuple[int, Dict[str, Any], float]:
        """Get specific post by ID."""
        return await self.get(f"/posts/{post_id}")

    async def create_post(
        self, post_data: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], float]:
        """Create new post."""
        return await self.post("/posts", data=post_data)

    async def get_users(self) -> Tuple[int, Dict[str, Any], float]:
        """Get all users."""
        return await self.get("/users")

    async def get_user(self, user_id: int) -> Tuple[int, Dict[str, Any], float]:
        """Get specific user by ID."""
        return await self.get(f"/users/{user_id}")

    async def get_comments(
        self, post_id: Optional[int] = None
    ) -> Tuple[int, Dict[str, Any], float]:
        """Get comments with optional post filtering."""
        if post_id:
            return await self.get(f"/posts/{post_id}/comments")
        return await self.get("/comments")


class AsyncReqResClient(AsyncAPIClient):
    """Async client for ReqRes API performance testing."""

    def __init__(self, base_url: str = "https://reqres.in/api", **kwargs):
        super().__init__(base_url, **kwargs)

    async def get_users(
        self, page: int = 1, per_page: int = 6
    ) -> Tuple[int, Dict[str, Any], float]:
        """Get paginated users."""
        params = {"page": page, "per_page": per_page}
        return await self.get("/users", params=params)

    async def get_user(self, user_id: int) -> Tuple[int, Dict[str, Any], float]:
        """Get specific user by ID."""
        return await self.get(f"/users/{user_id}")

    async def create_user(
        self, user_data: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], float]:
        """Create new user."""
        return await self.post("/users", data=user_data)

    async def login_user(
        self, email: str, password: str
    ) -> Tuple[int, Dict[str, Any], float]:
        """Login user."""
        data = {"email": email, "password": password}
        return await self.post("/login", data=data)
