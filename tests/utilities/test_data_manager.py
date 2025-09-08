"""
Test data management utilities for comprehensive API testing.

This module provides sophisticated test data creation, management, and cleanup
functionality for complex testing scenarios.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from faker import Faker

logger = logging.getLogger(__name__)
faker = Faker()


class TestDataManager:
    """
    Professional test data manager for API testing scenarios.

    Provides centralized test data creation, tracking, and cleanup
    with support for complex data relationships and dependencies.
    """

    def __init__(self, environment: str = "development"):
        """
        Initialize test data manager.

        Args:
            environment: Testing environment (development, staging, production)
        """
        self.environment = environment
        self.created_users: List[Dict[str, Any]] = []
        self.created_posts: List[Dict[str, Any]] = []
        self.created_comments: List[Dict[str, Any]] = []
        self.test_session_id = str(uuid.uuid4())

        logger.info(f"Initialized TestDataManager for {environment} environment")
        logger.info(f"Test session ID: {self.test_session_id}")

    def generate_user_data(self, **overrides) -> Dict[str, Any]:
        """
        Generate realistic user data with optional field overrides.

        Args:
            **overrides: Field values to override in generated data

        Returns:
            Dictionary containing user data
        """
        user_data = {
            "name": faker.name(),
            "username": faker.user_name(),
            "email": faker.email(),
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

        # Apply any overrides
        user_data.update(overrides)

        return user_data

    def generate_post_data(
        self, user_id: Optional[int] = None, **overrides
    ) -> Dict[str, Any]:
        """
        Generate realistic post data.

        Args:
            user_id: Optional user ID to associate with post
            **overrides: Field values to override

        Returns:
            Dictionary containing post data
        """
        post_data = {
            "title": faker.sentence(nb_words=faker.random_int(min=4, max=8)),
            "body": faker.text(max_nb_chars=faker.random_int(min=100, max=500)),
            "userId": user_id or faker.random_int(min=1, max=10),
        }

        post_data.update(overrides)
        return post_data

    def generate_comment_data(
        self, post_id: Optional[int] = None, **overrides
    ) -> Dict[str, Any]:
        """
        Generate realistic comment data.

        Args:
            post_id: Optional post ID to associate with comment
            **overrides: Field values to override

        Returns:
            Dictionary containing comment data
        """
        comment_data = {
            "name": faker.sentence(nb_words=3),
            "email": faker.email(),
            "body": faker.text(max_nb_chars=faker.random_int(min=50, max=200)),
            "postId": post_id or faker.random_int(min=1, max=100),
        }

        comment_data.update(overrides)
        return comment_data

    def generate_reqres_user_data(self, **overrides) -> Dict[str, Any]:
        """
        Generate user data compatible with ReqRes API format.

        Args:
            **overrides: Field values to override

        Returns:
            Dictionary containing ReqRes-compatible user data
        """
        user_data = {"name": faker.name(), "job": faker.job()}

        user_data.update(overrides)
        return user_data

    def generate_bulk_user_data(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate bulk user data for performance testing.

        Args:
            count: Number of users to generate

        Returns:
            List of user data dictionaries
        """
        logger.info(f"Generating {count} user records for bulk testing")

        users = []
        for i in range(count):
            user = self.generate_user_data()
            user["test_session_id"] = self.test_session_id
            user["sequence_number"] = i + 1
            users.append(user)

        return users

    def generate_bulk_post_data(
        self, count: int, user_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate bulk post data for performance testing.

        Args:
            count: Number of posts to generate
            user_ids: Optional list of user IDs to cycle through

        Returns:
            List of post data dictionaries
        """
        logger.info(f"Generating {count} post records for bulk testing")

        posts = []
        for i in range(count):
            user_id = None
            if user_ids:
                user_id = user_ids[i % len(user_ids)]

            post = self.generate_post_data(user_id=user_id)
            post["test_session_id"] = self.test_session_id
            post["sequence_number"] = i + 1
            posts.append(post)

        return posts

    def create_test_dataset(
        self, user_count: int = 10, posts_per_user: int = 5, comments_per_post: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a complete test dataset with relationships.

        Args:
            user_count: Number of users to create
            posts_per_user: Number of posts per user
            comments_per_post: Number of comments per post

        Returns:
            Dictionary containing users, posts, and comments
        """
        logger.info(
            f"Creating test dataset: {user_count} users, "
            f"{posts_per_user} posts/user, {comments_per_post} comments/post"
        )

        dataset: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "posts": [],
            "comments": [],
        }

        # Generate users
        for user_id in range(1, user_count + 1):
            user = self.generate_user_data()
            user["id"] = user_id
            user["test_session_id"] = self.test_session_id
            dataset["users"].append(user)

        # Generate posts for each user
        post_id = 1
        for user_id in range(1, user_count + 1):
            for _ in range(posts_per_user):
                post = self.generate_post_data(user_id=user_id)
                post["id"] = post_id
                post["test_session_id"] = self.test_session_id
                dataset["posts"].append(post)

                # Generate comments for this post
                for _ in range(comments_per_post):
                    comment = self.generate_comment_data(post_id=post_id)
                    comment["test_session_id"] = self.test_session_id
                    dataset["comments"].append(comment)

                post_id += 1

        logger.info(
            f"Created dataset with {len(dataset['users'])} users, "
            f"{len(dataset['posts'])} posts, {len(dataset['comments'])} comments"
        )

        return dataset

    def track_created_user(self, user_data: Dict[str, Any]):
        """Track a created user for cleanup."""
        self.created_users.append(user_data)
        logger.debug(f"Tracking created user: {user_data.get('id', 'unknown')}")

    def track_created_post(self, post_data: Dict[str, Any]):
        """Track a created post for cleanup."""
        self.created_posts.append(post_data)
        logger.debug(f"Tracking created post: {post_data.get('id', 'unknown')}")

    def track_created_comment(self, comment_data: Dict[str, Any]):
        """Track a created comment for cleanup."""
        self.created_comments.append(comment_data)
        logger.debug(f"Tracking created comment: {comment_data.get('id', 'unknown')}")

    def get_test_statistics(self) -> Dict[str, Any]:
        """Get statistics about created test data."""
        return {
            "environment": self.environment,
            "test_session_id": self.test_session_id,
            "created_users": len(self.created_users),
            "created_posts": len(self.created_posts),
            "created_comments": len(self.created_comments),
            "total_objects": len(self.created_users)
            + len(self.created_posts)
            + len(self.created_comments),
        }

    def cleanup_test_data(self):
        """
        Clean up tracked test data.

        Note: For public APIs like JSONPlaceholder and ReqRes,
        actual cleanup is not needed as they don't persist data.
        This method serves as a template for real API implementations.
        """
        stats = self.get_test_statistics()

        logger.info(f"Cleaning up test data for session {self.test_session_id}")
        logger.info(
            f"Would cleanup: {stats['created_users']} users, "
            f"{stats['created_posts']} posts, {stats['created_comments']} comments"
        )

        # In a real implementation, you would make DELETE requests here
        # For demo APIs, we just clear the tracking lists
        self.created_users.clear()
        self.created_posts.clear()
        self.created_comments.clear()

        logger.info("Test data cleanup completed")

    def generate_performance_test_data(
        self, endpoint_type: str, count: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Generate data specifically for performance testing scenarios.

        Args:
            endpoint_type: Type of endpoint (users, posts, comments)
            count: Number of records to generate

        Returns:
            List of test data records
        """
        logger.info(
            f"Generating {count} records for {endpoint_type} performance testing"
        )

        if endpoint_type == "users":
            return self.generate_bulk_user_data(count)
        elif endpoint_type == "posts":
            return self.generate_bulk_post_data(count)
        elif endpoint_type == "comments":
            return [self.generate_comment_data() for _ in range(count)]
        elif endpoint_type == "reqres_users":
            return [self.generate_reqres_user_data() for _ in range(count)]
        else:
            raise ValueError(f"Unsupported endpoint type: {endpoint_type}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup_test_data()
