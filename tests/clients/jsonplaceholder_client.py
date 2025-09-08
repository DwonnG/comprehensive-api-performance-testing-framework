"""
JSONPlaceholder API client for testing REST API patterns.

This client provides methods to interact with JSONPlaceholder API endpoints
for testing CRUD operations, data validation, and API response patterns.
"""

import logging
from typing import Any, Dict, Optional

import requests

from .api_client import APIClient

logger = logging.getLogger(__name__)


class JSONPlaceholderClient(APIClient):
    """
    Client for JSONPlaceholder API testing.

    JSONPlaceholder provides a fake REST API for testing and prototyping.
    This client implements all major endpoints with proper error handling.
    """

    def __init__(
        self, base_url: str = "https://jsonplaceholder.typicode.com", **kwargs
    ):
        """Initialize JSONPlaceholder client."""
        super().__init__(base_url, **kwargs)
        logger.info("Initialized JSONPlaceholder API client")

    # Posts endpoints
    def get_posts(self, user_id: Optional[int] = None) -> requests.Response:
        """
        Get all posts or posts by user ID.

        Args:
            user_id: Optional user ID to filter posts

        Returns:
            Response containing list of posts
        """
        params = {"userId": user_id} if user_id else None
        return self.get("/posts", params=params)

    def get_post(self, post_id: int) -> requests.Response:
        """
        Get a specific post by ID.

        Args:
            post_id: Post ID to retrieve

        Returns:
            Response containing post data
        """
        return self.get(f"/posts/{post_id}")

    def create_post(self, post_data: Dict[str, Any]) -> requests.Response:
        """
        Create a new post.

        Args:
            post_data: Post data containing title, body, userId

        Returns:
            Response containing created post data
        """
        return self.post("/posts", data=post_data)

    def update_post(self, post_id: int, post_data: Dict[str, Any]) -> requests.Response:
        """
        Update an existing post.

        Args:
            post_id: Post ID to update
            post_data: Updated post data

        Returns:
            Response containing updated post data
        """
        return self.put(f"/posts/{post_id}", data=post_data)

    def patch_post(self, post_id: int, post_data: Dict[str, Any]) -> requests.Response:
        """
        Partially update an existing post.

        Args:
            post_id: Post ID to update
            post_data: Partial post data to update

        Returns:
            Response containing updated post data
        """
        return self.patch(f"/posts/{post_id}", data=post_data)

    def delete_post(self, post_id: int) -> requests.Response:
        """
        Delete a post.

        Args:
            post_id: Post ID to delete

        Returns:
            Response confirming deletion
        """
        return self.delete(f"/posts/{post_id}")

    # Comments endpoints
    def get_comments(self, post_id: Optional[int] = None) -> requests.Response:
        """
        Get all comments or comments for a specific post.

        Args:
            post_id: Optional post ID to filter comments

        Returns:
            Response containing list of comments
        """
        if post_id:
            return self.get(f"/posts/{post_id}/comments")
        return self.get("/comments")

    def get_comment(self, comment_id: int) -> requests.Response:
        """
        Get a specific comment by ID.

        Args:
            comment_id: Comment ID to retrieve

        Returns:
            Response containing comment data
        """
        return self.get(f"/comments/{comment_id}")

    def create_comment(self, comment_data: Dict[str, Any]) -> requests.Response:
        """
        Create a new comment.

        Args:
            comment_data: Comment data containing name, email, body, postId

        Returns:
            Response containing created comment data
        """
        return self.post("/comments", data=comment_data)

    # Users endpoints
    def get_users(self) -> requests.Response:
        """
        Get all users.

        Returns:
            Response containing list of users
        """
        return self.get("/users")

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
            user_data: User data containing name, username, email, etc.

        Returns:
            Response containing created user data
        """
        return self.post("/users", data=user_data)

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> requests.Response:
        """
        Update an existing user.

        Args:
            user_id: User ID to update
            user_data: Updated user data

        Returns:
            Response containing updated user data
        """
        return self.put(f"/users/{user_id}", data=user_data)

    def delete_user(self, user_id: int) -> requests.Response:
        """
        Delete a user.

        Args:
            user_id: User ID to delete

        Returns:
            Response confirming deletion
        """
        return self.delete(f"/users/{user_id}")

    # Albums endpoints
    def get_albums(self, user_id: Optional[int] = None) -> requests.Response:
        """
        Get all albums or albums by user ID.

        Args:
            user_id: Optional user ID to filter albums

        Returns:
            Response containing list of albums
        """
        params = {"userId": user_id} if user_id else None
        return self.get("/albums", params=params)

    def get_album(self, album_id: int) -> requests.Response:
        """
        Get a specific album by ID.

        Args:
            album_id: Album ID to retrieve

        Returns:
            Response containing album data
        """
        return self.get(f"/albums/{album_id}")

    # Photos endpoints
    def get_photos(self, album_id: Optional[int] = None) -> requests.Response:
        """
        Get all photos or photos by album ID.

        Args:
            album_id: Optional album ID to filter photos

        Returns:
            Response containing list of photos
        """
        if album_id:
            return self.get(f"/albums/{album_id}/photos")
        return self.get("/photos")

    def get_photo(self, photo_id: int) -> requests.Response:
        """
        Get a specific photo by ID.

        Args:
            photo_id: Photo ID to retrieve

        Returns:
            Response containing photo data
        """
        return self.get(f"/photos/{photo_id}")

    # Todos endpoints
    def get_todos(
        self, user_id: Optional[int] = None, completed: Optional[bool] = None
    ) -> requests.Response:
        """
        Get todos with optional filtering.

        Args:
            user_id: Optional user ID to filter todos
            completed: Optional completion status filter

        Returns:
            Response containing list of todos
        """
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if completed is not None:
            params["completed"] = completed

        return self.get("/todos", params=params if params else None)

    def get_todo(self, todo_id: int) -> requests.Response:
        """
        Get a specific todo by ID.

        Args:
            todo_id: Todo ID to retrieve

        Returns:
            Response containing todo data
        """
        return self.get(f"/todos/{todo_id}")

    def create_todo(self, todo_data: Dict[str, Any]) -> requests.Response:
        """
        Create a new todo.

        Args:
            todo_data: Todo data containing title, completed, userId

        Returns:
            Response containing created todo data
        """
        return self.post("/todos", data=todo_data)
