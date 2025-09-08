"""
Authentication and authorization tests for API security validation.

This module tests authentication flows, token handling, and security
scenarios to ensure proper access control and error handling.
"""

import pytest


@pytest.mark.authentication
class TestAuthentication:
    """Authentication and authorization tests using ReqRes API."""

    @pytest.mark.smoke
    def test_successful_user_registration_returns_201_with_token(self, gorest_client):
        """Test successful user registration with valid credentials."""
        credentials = gorest_client.test_valid_user_credentials()

        response = gorest_client.register_user(
            credentials["email"], credentials["password"]
        )

        assert response.status_code == 200  # ReqRes returns 200 for register
        data = response.json()
        assert "id" in data
        assert "token" in data
        assert len(data["token"]) > 0

    @pytest.mark.smoke
    def test_successful_user_login_returns_200_with_token(self, gorest_client):
        """Test successful user login with valid credentials."""
        credentials = gorest_client.test_valid_user_credentials()

        response = gorest_client.login_user(
            credentials["email"], credentials["password"]
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0

    @pytest.mark.error_handling
    def test_unsuccessful_registration_missing_password_returns_400(
        self, gorest_client
    ):
        """Test registration failure when password is missing."""
        response = gorest_client.register_user_unsuccessful("sydney@fife")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Missing password" in data["error"]

    @pytest.mark.error_handling
    def test_unsuccessful_login_missing_password_returns_400(self, gorest_client):
        """Test login failure when password is missing."""
        response = gorest_client.login_user_unsuccessful("sydney@fife")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Missing password" in data["error"]

    @pytest.mark.error_handling
    def test_unsuccessful_registration_invalid_email_returns_400(self, gorest_client):
        """Test registration failure with invalid email."""
        response = gorest_client.register_user_unsuccessful("invalid.email")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @pytest.mark.error_handling
    def test_unsuccessful_login_invalid_credentials_returns_400(self, gorest_client):
        """Test login failure with invalid credentials."""
        invalid_credentials = gorest_client.test_invalid_user_credentials()

        response = gorest_client.login_user(
            invalid_credentials["email"], invalid_credentials["password"]
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @pytest.mark.validation
    def test_token_format_validation(self, gorest_client):
        """Test that returned tokens have expected format."""
        credentials = gorest_client.test_valid_user_credentials()

        # Test login token
        login_response = gorest_client.login_user(
            credentials["email"], credentials["password"]
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        login_token = login_data["token"]

        # Basic token validation
        assert isinstance(login_token, str)
        assert len(login_token) > 10  # Reasonable minimum token length

        # Test registration token
        register_response = gorest_client.register_user(
            credentials["email"], credentials["password"]
        )
        assert register_response.status_code == 200
        register_data = register_response.json()
        register_token = register_data["token"]

        # Basic token validation
        assert isinstance(register_token, str)
        assert len(register_token) > 10

    @pytest.mark.validation
    def test_registration_response_structure(self, gorest_client):
        """Test that registration response has correct structure."""
        credentials = gorest_client.test_valid_user_credentials()

        response = gorest_client.register_user(
            credentials["email"], credentials["password"]
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        required_fields = ["id", "token"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate data types
        assert isinstance(data["id"], int)
        assert isinstance(data["token"], str)

    @pytest.mark.validation
    def test_login_response_structure(self, gorest_client):
        """Test that login response has correct structure."""
        credentials = gorest_client.test_valid_user_credentials()

        response = gorest_client.login_user(
            credentials["email"], credentials["password"]
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "token" in data, "Missing token field"
        assert isinstance(data["token"], str)

    @pytest.mark.integration
    def test_authentication_workflow_end_to_end(self, gorest_client):
        """Test complete authentication workflow."""
        credentials = gorest_client.test_valid_user_credentials()

        # Step 1: Register user
        register_response = gorest_client.register_user(
            credentials["email"], credentials["password"]
        )
        assert register_response.status_code == 200
        register_data = register_response.json()

        # Step 2: Login with same credentials
        login_response = gorest_client.login_user(
            credentials["email"], credentials["password"]
        )
        assert login_response.status_code == 200
        login_data = login_response.json()

        # Step 3: Validate both operations returned tokens
        assert "token" in register_data
        assert "token" in login_data
        assert len(register_data["token"]) > 0
        assert len(login_data["token"]) > 0

    @pytest.mark.error_handling
    def test_authentication_error_consistency(self, gorest_client):
        """Test that authentication errors are consistent across endpoints."""
        # Test missing password error for both endpoints
        email = "test@example.com"

        register_response = gorest_client.register_user_unsuccessful(email)
        login_response = gorest_client.login_user_unsuccessful(email)

        # Both should return 400
        assert register_response.status_code == 400
        assert login_response.status_code == 400

        # Both should have error field
        register_data = register_response.json()
        login_data = login_response.json()

        assert "error" in register_data
        assert "error" in login_data

        # Both should mention missing password
        assert "password" in register_data["error"].lower()
        assert "password" in login_data["error"].lower()
