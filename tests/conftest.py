"""
Global pytest configuration and fixtures for comprehensive API testing.

This module provides session-scoped fixtures for API clients, test data management,
and environment configuration following enterprise testing patterns.
"""

import os
import sys
from typing import Any, Dict

import pytest
from faker import Faker

# Add the tests directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from clients.api_client import APIClient  # noqa: E402
from clients.gorest_client import GoRestClient  # noqa: E402
from clients.jsonplaceholder_client import JSONPlaceholderClient  # noqa: E402
from utilities.environment_config import EnvironmentConfig  # noqa: E402
from utilities.test_data_manager import TestDataManager  # noqa: E402

faker = Faker()


@pytest.fixture(scope="session")
def environment() -> str:
    """Get the current test environment from environment variable."""
    env_value = os.getenv("ENVIRONMENT", "development")
    print(f"DEBUG: Running tests in environment: {env_value}")
    return env_value


@pytest.fixture(scope="session")
def environment_config(environment: str) -> EnvironmentConfig:
    """Provide environment-specific configuration."""
    return EnvironmentConfig(environment)


@pytest.fixture(scope="session")
def api_timeout(environment: str) -> int:
    """Get API timeout based on environment."""
    timeouts = {"development": 30, "staging": 20, "production": 15}
    return int(os.getenv("API_TIMEOUT", timeouts.get(environment, 30)))


@pytest.fixture(scope="session")
def jsonplaceholder_client(
    environment_config: EnvironmentConfig, api_timeout: int
) -> JSONPlaceholderClient:
    """Provide JSONPlaceholder API client for testing."""
    return JSONPlaceholderClient(
        base_url=environment_config.jsonplaceholder_base_url, timeout=api_timeout
    )


@pytest.fixture(scope="session")
def gorest_client(
    environment_config: EnvironmentConfig, api_timeout: int
) -> GoRestClient:
    """Provide GoRest API client for testing."""
    return GoRestClient(
        base_url=environment_config.gorest_base_url,
        api_key=environment_config.gorest_api_key,
        timeout=api_timeout,
    )


@pytest.fixture(scope="session")
def httpbin_client(
    environment_config: EnvironmentConfig, api_timeout: int
) -> APIClient:
    """Provide HTTPBin client for HTTP protocol testing."""
    return APIClient(base_url=environment_config.httpbin_base_url, timeout=api_timeout)


@pytest.fixture
def fake_user_data() -> Dict[str, Any]:
    """Generate fake user data for testing."""
    return {
        "name": faker.name(),
        "email": faker.email(),
        "username": faker.user_name(),
        "phone": faker.phone_number(),
        "website": faker.url(),
        "company": {
            "name": faker.company(),
            "catchPhrase": faker.catch_phrase(),
            "bs": faker.bs(),
        },
        "address": {
            "street": faker.street_address(),
            "suite": faker.secondary_address(),
            "city": faker.city(),
            "zipcode": faker.zipcode(),
            "geo": {"lat": str(faker.latitude()), "lng": str(faker.longitude())},
        },
    }


@pytest.fixture
def fake_post_data() -> Dict[str, Any]:
    """Generate fake post data for testing."""
    return {
        "title": faker.sentence(nb_words=6),
        "body": faker.text(max_nb_chars=200),
        "userId": faker.random_int(min=1, max=10),
    }


@pytest.fixture
def fake_user_id() -> int:
    """Generate a fake user ID for testing."""
    return faker.random_int(min=1000, max=9999)


@pytest.fixture
def fake_post_id() -> int:
    """Generate a fake post ID for testing."""
    return faker.random_int(min=1000, max=9999)


@pytest.fixture(scope="session")
def test_data_manager(environment: str) -> TestDataManager:
    """Provide test data manager for complex test scenarios."""
    return TestDataManager(environment)


@pytest.fixture
def test_user_cleanup(gorest_client: GoRestClient):
    """Fixture to cleanup test users after test completion."""
    created_users = []

    def _create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user and track for cleanup."""
        response = gorest_client.create_user(user_data)
        if response.status_code == 201:
            user = response.json()
            created_users.append(user.get("id"))
            return user
        return {}

    yield _create_user

    # Cleanup created users
    for user_id in created_users:
        try:
            gorest_client.delete_user(user_id)
        except Exception as e:
            print(f"Warning: Failed to cleanup user {user_id}: {e}")


@pytest.fixture
def performance_test_data():
    """Generate performance test data sets."""
    return {
        "small_dataset": [faker.simple_profile() for _ in range(10)],
        "medium_dataset": [faker.simple_profile() for _ in range(100)],
        "large_dataset": [faker.simple_profile() for _ in range(1000)],
    }


def pytest_configure(config):
    """Configure pytest with custom markers and setup."""
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test for quick validation"
    )
    config.addinivalue_line(
        "markers", "users: mark test as related to user management functionality"
    )
    config.addinivalue_line(
        "markers", "posts: mark test as related to post management functionality"
    )
    config.addinivalue_line(
        "markers", "comments: mark test as related to comment functionality"
    )
    config.addinivalue_line("markers", "health_check: mark test as a health check test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add performance marker to performance tests
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Add integration marker to end_to_end tests
        if "end_to_end" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    """Clean up resources at the end of the test session."""
    try:
        # Perform any global cleanup here
        print("Test session completed - performing cleanup")
    except Exception:
        # Silently handle cleanup errors during pytest shutdown
        pass
