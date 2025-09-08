"""
Base API client with professional error handling and retry mechanisms.

This module provides a robust foundation for API testing with enterprise-grade
features including retry logic, timeout handling, and comprehensive logging.
"""

import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Base exception for API client errors."""

    pass


class APITimeoutError(APIClientError):
    """Raised when API requests timeout."""

    pass


class APIConnectionError(APIClientError):
    """Raised when API connection fails."""

    pass


class APIClient:
    """
    Professional API client with retry mechanisms and comprehensive error handling.

    Features:
    - Automatic retry with exponential backoff
    - Comprehensive logging and metrics
    - Timeout handling
    - Request/response validation
    - Session management for connection pooling
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
            headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize session for connection pooling
        self.session = requests.Session()

        # Set default headers
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Comprehensive-API-Testing-Framework/1.0",
        }
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)

        logger.info(f"Initialized API client for {self.base_url}")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
        reraise=True,
    )
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            headers: Additional headers for this request
            **kwargs: Additional arguments for requests

        Returns:
            requests.Response object

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
            APIClientError: For other API-related errors
        """
        url = self._build_url(endpoint)
        start_time = time.time()

        try:
            # Merge headers if provided
            request_headers = dict(self.session.headers)
            if headers:
                request_headers.update(headers)

            logger.debug(f"Making {method} request to {url}")

            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )

            # Log request metrics
            duration = time.time() - start_time
            logger.info(
                f"{method} {url} - Status: {response.status_code}, "
                f"Duration: {duration:.3f}s"
            )

            return response

        except requests.Timeout as e:
            duration = time.time() - start_time
            logger.error(f"Request timeout after {duration:.3f}s: {url}")
            raise APITimeoutError(
                f"Request to {url} timed out after {self.timeout}s"
            ) from e

        except requests.ConnectionError as e:
            duration = time.time() - start_time
            logger.error(f"Connection error after {duration:.3f}s: {url}")
            raise APIConnectionError(f"Failed to connect to {url}") from e

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Unexpected error after {duration:.3f}s: {url} - {e}")
            raise APIClientError(f"Unexpected error for {url}: {e}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make GET request."""
        return self._make_request(
            "GET", endpoint, params=params, headers=headers, **kwargs
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make POST request."""
        return self._make_request(
            "POST", endpoint, data=data, params=params, headers=headers, **kwargs
        )

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make PUT request."""
        return self._make_request(
            "PUT", endpoint, data=data, params=params, headers=headers, **kwargs
        )

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make DELETE request."""
        return self._make_request(
            "DELETE", endpoint, params=params, headers=headers, **kwargs
        )

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make PATCH request."""
        return self._make_request(
            "PATCH", endpoint, data=data, params=params, headers=headers, **kwargs
        )

    def health_check(self) -> bool:
        """
        Perform basic health check against the API.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.get("/")
            return response.status_code < 500
        except Exception as e:
            logger.warning(f"Health check failed for {self.base_url}: {e}")
            return False

    def close(self):
        """Close the session and cleanup resources."""
        if hasattr(self, "session"):
            self.session.close()
            logger.info(f"Closed API client session for {self.base_url}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
