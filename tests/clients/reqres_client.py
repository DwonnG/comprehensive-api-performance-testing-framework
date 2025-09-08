"""
ReqRes API client for testing user management workflows.

This client provides methods to interact with ReqRes API endpoints
for testing user CRUD operations, authentication patterns, and data validation.
"""

import logging
from typing import Any, Dict

import requests

from .api_client import APIClient

logger = logging.getLogger(__name__)


class ReqResClient(APIClient):
    """
    Client for ReqRes API testing.

    ReqRes provides a hosted REST API ready to respond to AJAX requests.
    This client implements user management and authentication testing patterns.
    """

    def __init__(self, base_url: str = "https://reqres.in/api", **kwargs):
        """Initialize ReqRes client."""
        super().__init__(base_url, **kwargs)
        logger.info("Initialized ReqRes API client")

    # User management endpoints
    def get_users(self, page: int = 1, per_page: int = 6) -> requests.Response:
        """
        Get paginated list of users.

        Args:
            page: Page number to retrieve
            per_page: Number of users per page

        Returns:
            Response containing paginated user data
        """
        params = {"page": page, "per_page": per_page}
        return self.get("/users", params=params)

    def get_user(self, user_id: int) -> requests.Response:
        """
        Get a specific user by ID.

        Args:
            user_id: User ID to retrieve

        Returns:
            Response containing user data
        """
        return self.get(f"/users/{user_id}")

    def create_user(self, user_data: Dict[str, Any]) -> requests.Response:
        """
        Create a new user.

        Args:
            user_data: User data containing name, job, etc.

        Returns:
            Response containing created user data with ID and timestamp
        """
        return self.post("/users", data=user_data)

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> requests.Response:
        """
        Update an existing user (PUT).

        Args:
            user_id: User ID to update
            user_data: Updated user data

        Returns:
            Response containing updated user data with timestamp
        """
        return self.put(f"/users/{user_id}", data=user_data)

    def patch_user(self, user_id: int, user_data: Dict[str, Any]) -> requests.Response:
        """
        Partially update an existing user (PATCH).

        Args:
            user_id: User ID to update
            user_data: Partial user data to update

        Returns:
            Response containing updated user data with timestamp
        """
        return self.patch(f"/users/{user_id}", data=user_data)

    def delete_user(self, user_id: int) -> requests.Response:
        """
        Delete a user.

        Args:
            user_id: User ID to delete

        Returns:
            Response confirming deletion (204 No Content)
        """
        return self.delete(f"/users/{user_id}")

    # Authentication endpoints
    def register_user(self, email: str, password: str) -> requests.Response:
        """
        Register a new user account.

        Args:
            email: User email address
            password: User password

        Returns:
            Response containing registration result with token or error
        """
        data = {"email": email, "password": password}
        return self.post("/register", data=data)

    def login_user(self, email: str, password: str) -> requests.Response:
        """
        Login with user credentials.

        Args:
            email: User email address
            password: User password

        Returns:
            Response containing login result with token or error
        """
        data = {"email": email, "password": password}
        return self.post("/login", data=data)

    def register_user_unsuccessful(self, email: str) -> requests.Response:
        """
        Test unsuccessful registration (missing password).

        Args:
            email: User email address (without password)

        Returns:
            Response containing error message
        """
        data = {"email": email}
        return self.post("/register", data=data)

    def login_user_unsuccessful(self, email: str) -> requests.Response:
        """
        Test unsuccessful login (missing password).

        Args:
            email: User email address (without password)

        Returns:
            Response containing error message
        """
        data = {"email": email}
        return self.post("/login", data=data)

    # Resource endpoints
    def get_resources(self, page: int = 1, per_page: int = 6) -> requests.Response:
        """
        Get paginated list of resources.

        Args:
            page: Page number to retrieve
            per_page: Number of resources per page

        Returns:
            Response containing paginated resource data
        """
        params = {"page": page, "per_page": per_page}
        return self.get("/unknown", params=params)

    def get_resource(self, resource_id: int) -> requests.Response:
        """
        Get a specific resource by ID.

        Args:
            resource_id: Resource ID to retrieve

        Returns:
            Response containing resource data
        """
        return self.get(f"/unknown/{resource_id}")

    # Utility methods for testing
    def get_delayed_response(self, delay: int = 3) -> requests.Response:
        """
        Get a delayed response for testing timeout scenarios.

        Args:
            delay: Delay in seconds

        Returns:
            Response after specified delay
        """
        params = {"delay": delay}
        return self.get("/users", params=params)

    def test_valid_user_credentials(self) -> Dict[str, str]:
        """
        Get valid test credentials for authentication testing.

        Returns:
            Dictionary containing valid email and password
        """
        return {"email": "eve.holt@reqres.in", "password": "cityslicka"}

    def test_invalid_user_credentials(self) -> Dict[str, str]:
        """
        Get invalid test credentials for negative testing.

        Returns:
            Dictionary containing invalid email and password
        """
        return {"email": "invalid@example.com", "password": "wrongpassword"}
