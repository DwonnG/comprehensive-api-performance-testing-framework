"""
Environment configuration management for multi-environment testing.

This module provides centralized configuration management for different
testing environments with proper validation and fallback mechanisms.
"""

import logging
import os
from typing import Any, Dict, cast

logger = logging.getLogger(__name__)


class EnvironmentConfigError(Exception):
    """Raised when environment configuration is invalid."""

    pass


class EnvironmentConfig:
    """
    Centralized environment configuration for API testing.

    Manages environment-specific settings including API endpoints,
    timeouts, retry policies, and authentication configurations.
    """

    # Environment configurations
    ENVIRONMENTS = {
        "development": {
            "jsonplaceholder_base_url": "https://jsonplaceholder.typicode.com",
            "gorest_base_url": "https://gorest.co.in/public/v2",
            "gorest_api_key": "test-key",
            "httpbin_base_url": "https://httpbin.org",
            "default_timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0,
            "parallel_workers": 4,
            "performance_duration": 30,
            "max_rps": 50,
        },
        "staging": {
            "jsonplaceholder_base_url": "https://jsonplaceholder.typicode.com",
            "gorest_base_url": "https://gorest.co.in/public/v2",
            "gorest_api_key": "test-key",
            "httpbin_base_url": "https://httpbin.org",
            "default_timeout": 20,
            "max_retries": 2,
            "retry_delay": 0.5,
            "parallel_workers": 6,
            "performance_duration": 60,
            "max_rps": 100,
        },
        "production": {
            "jsonplaceholder_base_url": "https://jsonplaceholder.typicode.com",
            "gorest_base_url": "https://gorest.co.in/public/v2",
            "gorest_api_key": "test-key",
            "httpbin_base_url": "https://httpbin.org",
            "default_timeout": 15,
            "max_retries": 1,
            "retry_delay": 0.2,
            "parallel_workers": 8,
            "performance_duration": 120,
            "max_rps": 200,
        },
    }

    def __init__(self, environment: str = "development"):
        """
        Initialize environment configuration.

        Args:
            environment: Target environment name

        Raises:
            EnvironmentConfigError: If environment is not supported
        """
        if environment not in self.ENVIRONMENTS:
            available = ", ".join(self.ENVIRONMENTS.keys())
            raise EnvironmentConfigError(
                f"Unknown environment '{environment}'. Available: {available}"
            )

        self.environment = environment
        self.config = self.ENVIRONMENTS[environment].copy()

        # Override with environment variables if present
        self._load_environment_overrides()

        logger.info(f"Initialized configuration for environment: {environment}")

    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables."""
        overrides = {
            "JSONPLACEHOLDER_BASE_URL": "jsonplaceholder_base_url",
            "GOREST_BASE_URL": "gorest_base_url",
            "HTTPBIN_BASE_URL": "httpbin_base_url",
            "API_TIMEOUT": ("default_timeout", int),
            "MAX_RETRIES": ("max_retries", int),
            "RETRY_DELAY": ("retry_delay", float),
            "PARALLEL_WORKERS": ("parallel_workers", int),
            "PERFORMANCE_DURATION": ("performance_duration", int),
            "MAX_RPS": ("max_rps", int),
        }

        for env_var, config_key in overrides.items():
            value = os.getenv(env_var)
            if value:
                try:
                    if isinstance(config_key, tuple):
                        key, converter = config_key
                        self.config[key] = converter(value)
                    else:
                        self.config[config_key] = value
                    logger.debug(f"Override {config_key} = {value} from {env_var}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {value} - {e}")

    @property
    def jsonplaceholder_base_url(self) -> str:
        """Get JSONPlaceholder API base URL."""
        return cast(str, self.config["jsonplaceholder_base_url"])

    @property
    def gorest_base_url(self) -> str:
        """Get GoRest API base URL."""
        return cast(str, self.config["gorest_base_url"])

    @property
    def gorest_api_key(self) -> str:
        """Get GoRest API key."""
        return cast(str, self.config["gorest_api_key"])

    @property
    def httpbin_base_url(self) -> str:
        """Get HTTPBin API base URL."""
        return cast(str, self.config["httpbin_base_url"])

    @property
    def default_timeout(self) -> int:
        """Get default API timeout in seconds."""
        return cast(int, self.config["default_timeout"])

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts."""
        return cast(int, self.config["max_retries"])

    @property
    def retry_delay(self) -> float:
        """Get retry delay in seconds."""
        return cast(float, self.config["retry_delay"])

    @property
    def parallel_workers(self) -> int:
        """Get number of parallel test workers."""
        return cast(int, self.config["parallel_workers"])

    @property
    def performance_duration(self) -> int:
        """Get performance test duration in seconds."""
        return cast(int, self.config["performance_duration"])

    @property
    def max_rps(self) -> int:
        """Get maximum requests per second for performance tests."""
        return cast(int, self.config["max_rps"])

    def get_client_config(self, client_type: str) -> Dict[str, Any]:
        """
        Get configuration for specific API client.

        Args:
            client_type: Type of client (jsonplaceholder, reqres, httpbin)

        Returns:
            Configuration dictionary for the client

        Raises:
            EnvironmentConfigError: If client type is not supported
        """
        client_configs = {
            "jsonplaceholder": {
                "base_url": self.jsonplaceholder_base_url,
                "timeout": self.default_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
            },
            "reqres": {
                "base_url": self.gorest_base_url,
                "timeout": self.default_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
            },
            "httpbin": {
                "base_url": self.httpbin_base_url,
                "timeout": self.default_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
            },
        }

        if client_type not in client_configs:
            available = ", ".join(client_configs.keys())
            raise EnvironmentConfigError(
                f"Unknown client type '{client_type}'. Available: {available}"
            )

        return client_configs[client_type]

    def get_performance_config(self, endpoint: str) -> Dict[str, Any]:
        """
        Get performance testing configuration for specific endpoint.

        Args:
            endpoint: Endpoint name for performance testing

        Returns:
            Performance configuration dictionary
        """
        # Default performance configurations per endpoint type
        endpoint_configs = {
            "users": {
                "target_rps": min(self.max_rps, 100),
                "max_test_rate": min(self.max_rps * 2, 200),
                "test_duration": self.performance_duration,
                "concurrent_users": min(self.parallel_workers * 5, 20),
            },
            "posts": {
                "target_rps": min(self.max_rps, 50),
                "max_test_rate": min(self.max_rps, 100),
                "test_duration": self.performance_duration,
                "concurrent_users": min(self.parallel_workers * 3, 12),
            },
            "comments": {
                "target_rps": min(self.max_rps, 30),
                "max_test_rate": min(self.max_rps, 60),
                "test_duration": self.performance_duration // 2,
                "concurrent_users": min(self.parallel_workers * 2, 8),
            },
            "default": {
                "target_rps": min(self.max_rps // 2, 25),
                "max_test_rate": min(self.max_rps, 50),
                "test_duration": self.performance_duration // 2,
                "concurrent_users": self.parallel_workers,
            },
        }

        return endpoint_configs.get(endpoint, endpoint_configs["default"])

    def validate_config(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required URLs are accessible
            required_urls = [
                self.jsonplaceholder_base_url,
                self.gorest_base_url,
                self.httpbin_base_url,
            ]

            for url in required_urls:
                if not url or not url.startswith(("http://", "https://")):
                    logger.error(f"Invalid URL in configuration: {url}")
                    return False

            # Check numeric values are positive
            if self.default_timeout <= 0:
                logger.error(f"Invalid timeout: {self.default_timeout}")
                return False

            if self.max_retries < 0:
                logger.error(f"Invalid max_retries: {self.max_retries}")
                return False

            if self.parallel_workers <= 0:
                logger.error(f"Invalid parallel_workers: {self.parallel_workers}")
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"EnvironmentConfig(environment={self.environment})"

    def __repr__(self) -> str:
        """Detailed string representation of configuration."""
        return (
            f"EnvironmentConfig(environment={self.environment}, config={self.config})"
        )
