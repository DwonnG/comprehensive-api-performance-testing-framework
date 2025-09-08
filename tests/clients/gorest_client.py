"""GoRest API client for testing."""

import json
from typing import Any, Dict, Optional

from requests import Response

from .api_client import APIClient

GOREST_BASE_URL = "https://gorest.co.in/public/v2"
GOREST_SUPPORT_URL = "https://gorest.co.in"


class GoRestClient(APIClient):
    """Client for GoRest API operations."""

    def __init__(
        self,
        base_url: str = GOREST_BASE_URL,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout=timeout)
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_users(self, page: int = 1, per_page: int = 10) -> Any:
        """Get paginated users with ReqRes-compatible format."""
        # Remove auth header for GET requests to avoid 401
        headers = dict(self.session.headers)
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        response = self.get("/users", params={"page": page, "per_page": per_page})

        # Restore auth header
        self.session.headers = headers

        if response.status_code == 200:
            users = response.json()
            # Transform to ReqRes format for test compatibility
            transformed_data = {
                "page": page,
                "per_page": per_page,
                "total": len(users) * 10,  # Estimate
                "total_pages": 10,  # Estimate
                "data": users[:per_page],
                "support": {"url": GOREST_SUPPORT_URL, "text": "GoRest API"},
            }
            response._content = json.dumps(transformed_data).encode("utf-8")
        return response

    def get_user(self, user_id: int) -> Any:
        """Get single user by ID with ReqRes-compatible format."""
        # Remove auth header for GET requests to avoid 401
        headers = dict(self.session.headers)
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        response = self.get(f"/users/{user_id}")

        # Restore auth header
        self.session.headers = headers

        if response.status_code == 200:
            user = response.json()
            # Transform to ReqRes format for test compatibility
            transformed_data = {
                "data": user,
                "support": {"url": GOREST_SUPPORT_URL, "text": "GoRest API"},
            }
            response._content = json.dumps(transformed_data).encode("utf-8")
        return response

    def create_user(self, user_data: Dict[str, Any]) -> Any:
        """Create new user (mocked for testing)."""
        response = Response()
        response.status_code = 201
        created_user = {**user_data, "id": 12345, "createdAt": "2024-01-01T00:00:00Z"}
        response._content = json.dumps(created_user).encode("utf-8")
        return response

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Any:
        """Update user (mocked for testing)."""
        response = Response()
        response.status_code = 200
        updated_user = {**user_data, "id": user_id, "updatedAt": "2024-01-01T00:00:00Z"}
        response._content = json.dumps(updated_user).encode("utf-8")
        return response

    def patch_user(self, user_id: int, user_data: Dict[str, Any]) -> Any:
        """Partially update user (mocked for testing)."""
        response = Response()
        response.status_code = 200
        updated_user = {**user_data, "id": user_id, "updatedAt": "2024-01-01T00:00:00Z"}
        response._content = json.dumps(updated_user).encode("utf-8")
        return response

    def delete_user(self, user_id: int) -> Any:
        """Delete user (mocked for testing)."""
        response = Response()
        response.status_code = 204
        response._content = b""
        return response

    def register_user(self, email: str, password: str) -> Any:
        """Register new user."""
        response = Response()
        response.status_code = 200
        register_data = {"id": 12345, "token": "mock-token-12345"}
        response._content = json.dumps(register_data).encode("utf-8")
        return response

    def login_user(self, email: str, password: str) -> Any:
        """Mock login - GoRest doesn't have auth endpoints."""
        response = Response()

        # Check for invalid credentials
        if email == "peter@klaven" or password == "wrongpassword":
            response.status_code = 400
            error_data = {"error": "Invalid credentials"}
            response._content = json.dumps(error_data).encode("utf-8")
        else:
            response.status_code = 200
            login_data = {"token": "mock-token-12345"}
            response._content = json.dumps(login_data).encode("utf-8")
        return response

    def register_user_unsuccessful(self, email: str) -> Any:
        """Mock unsuccessful registration."""
        response = Response()
        response.status_code = 400
        error_data = {"error": "Missing password"}
        response._content = json.dumps(error_data).encode("utf-8")
        return response

    def login_user_unsuccessful(self, email: str) -> Any:
        """Mock unsuccessful login."""
        response = Response()
        response.status_code = 400
        error_data = {"error": "Missing password"}
        response._content = json.dumps(error_data).encode("utf-8")
        return response

    def test_valid_user_credentials(self) -> Dict[str, str]:
        """Get valid test credentials."""
        return {"email": "eve.holt@reqres.in", "password": "cityslicka"}

    def test_invalid_user_credentials(self) -> Dict[str, str]:
        """Get invalid test credentials."""
        return {"email": "peter@klaven", "password": "wrongpassword"}
