"""
User management tests for CRUD operations and data validation.

This module tests user-related functionality including creation, retrieval,
updates, deletion, and data validation across different API endpoints.
"""

import pytest
from faker import Faker

faker = Faker()


@pytest.mark.users
class TestUserManagement:
    """Comprehensive tests for user management functionality."""

    @pytest.mark.smoke
    @pytest.mark.crud
    def test_successfully_get_users_returns_200_with_user_list(
        self, jsonplaceholder_client
    ):
        """Test successful retrieval of user list."""
        response = jsonplaceholder_client.get_users()

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0

        # Validate user structure
        user = users[0]
        required_fields = [
            "id",
            "name",
            "username",
            "email",
            "address",
            "phone",
            "website",
            "company",
        ]
        for field in required_fields:
            assert field in user, f"Missing required field: {field}"

    @pytest.mark.smoke
    @pytest.mark.crud
    def test_successfully_get_single_user_returns_200_with_user_data(
        self, jsonplaceholder_client
    ):
        """Test successful retrieval of a single user."""
        user_id = 1
        response = jsonplaceholder_client.get_user(user_id)

        assert response.status_code == 200
        user = response.json()
        assert user["id"] == user_id
        assert "name" in user
        assert "email" in user
        assert "address" in user
        assert "geo" in user["address"]
        assert "lat" in user["address"]["geo"]
        assert "lng" in user["address"]["geo"]

    @pytest.mark.crud
    def test_successfully_create_user_returns_201_with_created_user_data(
        self, jsonplaceholder_client, fake_user_data
    ):
        """Test successful user creation."""
        response = jsonplaceholder_client.create_user(fake_user_data)

        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == fake_user_data["name"]
        assert created_user["email"] == fake_user_data["email"]
        assert created_user["username"] == fake_user_data["username"]
        assert "id" in created_user

    @pytest.mark.crud
    def test_successfully_update_user_returns_200_with_updated_data(
        self, jsonplaceholder_client, fake_user_data
    ):
        """Test successful user update using PUT."""
        user_id = 1
        response = jsonplaceholder_client.update_user(user_id, fake_user_data)

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["id"] == user_id
        assert updated_user["name"] == fake_user_data["name"]
        assert updated_user["email"] == fake_user_data["email"]

    @pytest.mark.crud
    def test_successfully_delete_user_returns_200(self, jsonplaceholder_client):
        """Test successful user deletion."""
        user_id = 1
        response = jsonplaceholder_client.delete_user(user_id)

        assert response.status_code == 200

    @pytest.mark.error_handling
    def test_non_existent_user_returns_404_with_empty_response(
        self, jsonplaceholder_client, fake_user_id
    ):
        """Test proper handling of non-existent user requests."""
        response = jsonplaceholder_client.get_user(fake_user_id)

        assert response.status_code == 404

    @pytest.mark.validation
    def test_user_email_format_validation(self, jsonplaceholder_client):
        """Test user email format validation."""
        # Get a real user to verify email format
        response = jsonplaceholder_client.get_user(1)
        assert response.status_code == 200

        user = response.json()
        email = user["email"]

        # Basic email validation
        assert "@" in email
        assert "." in email
        assert len(email) > 5

    @pytest.mark.validation
    def test_user_data_consistency_across_endpoints(self, jsonplaceholder_client):
        """Test data consistency when accessing users through different endpoints."""
        user_id = 1

        # Get user directly
        user_response = jsonplaceholder_client.get_user(user_id)
        assert user_response.status_code == 200
        direct_user = user_response.json()

        # Get user from users list
        users_response = jsonplaceholder_client.get_users()
        assert users_response.status_code == 200
        users_list = users_response.json()

        list_user = next((user for user in users_list if user["id"] == user_id), None)
        assert list_user is not None, f"User {user_id} not found in users list"

        # Compare key fields
        assert direct_user["id"] == list_user["id"]
        assert direct_user["name"] == list_user["name"]
        assert direct_user["email"] == list_user["email"]
        assert direct_user["username"] == list_user["username"]

    @pytest.mark.integration
    def test_user_posts_relationship(self, jsonplaceholder_client):
        """Test relationship between users and their posts."""
        user_id = 1

        # Get user
        user_response = jsonplaceholder_client.get_user(user_id)
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["id"] == user_id

        # Get posts for this user
        posts_response = jsonplaceholder_client.get_posts(user_id=user_id)
        assert posts_response.status_code == 200
        posts = posts_response.json()

        # Verify all posts belong to the user
        for post in posts:
            assert post["userId"] == user_id

        assert len(posts) > 0, f"User {user_id} should have posts"


@pytest.mark.users
class TestGoRestUserManagement:
    """Tests for ReqRes API user management functionality."""

    @pytest.mark.smoke
    @pytest.mark.crud
    def test_successfully_get_paginated_users_returns_200_with_pagination_info(
        self, gorest_client
    ):
        """Test successful retrieval of paginated users."""
        response = gorest_client.get_users(page=1, per_page=3)

        assert response.status_code == 200
        data = response.json()

        # Validate pagination structure
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert "total_pages" in data
        assert "data" in data
        assert "support" in data

        # Validate user data
        users = data["data"]
        assert len(users) <= 3
        assert len(users) > 0

        user = users[0]
        required_fields = ["id", "email", "name", "gender", "status"]
        for field in required_fields:
            assert field in user, f"Missing required field: {field}"

    @pytest.mark.smoke
    @pytest.mark.crud
    def test_successfully_get_single_user_returns_200_with_user_data(
        self, gorest_client
    ):
        """Test successful retrieval of a single user from GoRest."""
        # Get a valid user ID dynamically
        users_response = gorest_client.get_users(page=1, per_page=1)
        assert users_response.status_code == 200
        users_data = users_response.json()
        assert len(users_data["data"]) > 0, "No users available for testing"
        user_id = users_data["data"][0]["id"]

        response = gorest_client.get_user(user_id)

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "support" in data

        user = data["data"]
        assert user["id"] == user_id
        assert "email" in user
        assert "name" in user
        assert "gender" in user
        assert "status" in user

    @pytest.mark.crud
    def test_successfully_create_user_returns_201_with_created_data(
        self, gorest_client
    ):
        """Test successful user creation in ReqRes."""
        user_data = {"name": faker.name(), "job": faker.job()}

        response = gorest_client.create_user(user_data)

        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == user_data["name"]
        assert created_user["job"] == user_data["job"]
        assert "id" in created_user
        assert "createdAt" in created_user

    @pytest.mark.crud
    def test_successfully_update_user_returns_200_with_timestamp(self, gorest_client):
        """Test successful user update in ReqRes."""
        user_id = 2
        user_data = {"name": faker.name(), "job": faker.job()}

        response = gorest_client.update_user(user_id, user_data)

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["name"] == user_data["name"]
        assert updated_user["job"] == user_data["job"]
        assert "updatedAt" in updated_user

    @pytest.mark.crud
    def test_successfully_patch_user_returns_200_with_partial_update(
        self, gorest_client
    ):
        """Test successful partial user update using PATCH."""
        user_id = 2
        partial_data = {"job": faker.job()}

        response = gorest_client.patch_user(user_id, partial_data)

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["job"] == partial_data["job"]
        assert "updatedAt" in updated_user

    @pytest.mark.crud
    def test_successfully_delete_user_returns_204(self, gorest_client):
        """Test successful user deletion in ReqRes."""
        user_id = 2
        response = gorest_client.delete_user(user_id)

        assert response.status_code == 204
        assert response.text == ""

    @pytest.mark.error_handling
    def test_non_existent_user_returns_404(self, gorest_client):
        """Test proper handling of non-existent user in ReqRes."""
        response = gorest_client.get_user(999)

        assert response.status_code == 404

    @pytest.mark.validation
    def test_pagination_boundary_conditions(self, gorest_client):
        """Test pagination edge cases."""
        # Test first page
        response = gorest_client.get_users(page=1, per_page=6)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1

        # Test page beyond available data
        response = gorest_client.get_users(page=999, per_page=6)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0

        # Test different per_page values
        response = gorest_client.get_users(page=1, per_page=1)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["per_page"] == 1

    @pytest.mark.integration
    def test_user_cleanup_workflow(self, gorest_client, test_user_cleanup):
        """Test complete user lifecycle with cleanup."""
        user_data = {"name": faker.name(), "job": faker.job()}

        # Create user using cleanup fixture
        created_user = test_user_cleanup(user_data)

        assert "id" in created_user
        assert created_user["name"] == user_data["name"]
        assert created_user["job"] == user_data["job"]

        # User will be automatically cleaned up by fixture
