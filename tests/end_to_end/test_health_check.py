"""
Health check tests for API availability and basic connectivity.

This module tests the basic health and availability of all configured APIs
to ensure they are accessible and responding correctly.
"""

import pytest
import requests


@pytest.mark.health_check
class TestHealthCheck:
    """Health check tests for all API endpoints."""

    @pytest.mark.smoke
    def test_jsonplaceholder_health_check_returns_successful_response(
        self, jsonplaceholder_client
    ):
        """Test JSONPlaceholder API is accessible and responding."""
        response = jsonplaceholder_client.get("/posts/1")

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data
        assert "title" in response_data
        assert "body" in response_data
        assert "userId" in response_data

    @pytest.mark.smoke
    def test_reqres_health_check_returns_successful_response(self, gorest_client):
        """Test ReqRes API is accessible and responding."""
        response = gorest_client.get_users(page=1)

        assert response.status_code == 200
        response_data = response.json()
        assert "data" in response_data
        assert "page" in response_data
        assert "per_page" in response_data
        assert "total" in response_data
        assert len(response_data["data"]) > 0

    @pytest.mark.smoke
    def test_httpbin_health_check_returns_successful_response(self, httpbin_client):
        """Test HTTPBin API is accessible and responding."""
        response = httpbin_client.get("/get")

        assert response.status_code == 200
        response_data = response.json()
        assert "args" in response_data
        assert "headers" in response_data
        assert "origin" in response_data
        assert "url" in response_data

    def test_api_response_times_are_within_acceptable_limits(
        self, jsonplaceholder_client, gorest_client, httpbin_client
    ):
        """Test that API response times are within acceptable limits."""
        import time

        # Test JSONPlaceholder response time
        start_time = time.time()
        response = jsonplaceholder_client.get("/posts/1")
        jsonplaceholder_duration = time.time() - start_time

        assert response.status_code == 200
        assert (
            jsonplaceholder_duration < 5.0
        ), f"JSONPlaceholder too slow: {jsonplaceholder_duration}s"

        # Test ReqRes response time
        start_time = time.time()
        response = gorest_client.get_users(page=1)
        reqres_duration = time.time() - start_time

        assert response.status_code == 200
        assert reqres_duration < 5.0, f"ReqRes too slow: {reqres_duration}s"

        # Test HTTPBin response time
        start_time = time.time()
        response = httpbin_client.get("/get")
        httpbin_duration = time.time() - start_time

        assert response.status_code == 200
        assert httpbin_duration < 5.0, f"HTTPBin too slow: {httpbin_duration}s"

    def test_api_error_handling_for_non_existent_endpoints(
        self, jsonplaceholder_client, gorest_client, httpbin_client
    ):
        """Test proper error handling for non-existent endpoints."""
        # Test JSONPlaceholder 404 handling
        response = jsonplaceholder_client.get("/nonexistent")
        assert response.status_code == 404

        # Test ReqRes 404 handling
        response = gorest_client.get("/nonexistent")
        assert response.status_code == 404

        # Test HTTPBin 404 handling
        response = httpbin_client.get("/nonexistent")
        assert response.status_code == 404

    @pytest.mark.slow
    def test_api_timeout_handling(self, httpbin_client):
        """Test proper timeout handling for slow endpoints."""
        # HTTPBin provides a delay endpoint for testing timeouts
        import time

        start_time = time.time()
        try:
            # Request a 2-second delay, should complete successfully
            response = httpbin_client.get("/delay/2")
            duration = time.time() - start_time

            assert response.status_code == 200
            assert duration >= 2.0, "Response came back too quickly"
            assert duration < 10.0, "Response took too long"

        except requests.Timeout:
            duration = time.time() - start_time
            pytest.fail(f"Request timed out unexpectedly after {duration}s")

    def test_concurrent_health_checks(
        self, jsonplaceholder_client, gorest_client, httpbin_client
    ):
        """Test that APIs can handle concurrent requests."""
        import concurrent.futures
        import time

        def make_request(client, endpoint):
            start_time = time.time()
            if client == jsonplaceholder_client:
                response = client.get("/posts/1")
            elif client == gorest_client:
                response = client.get_users(page=1)
            else:  # httpbin_client
                response = client.get("/get")

            duration = time.time() - start_time
            return response.status_code, duration

        # Make concurrent requests to all APIs
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(make_request, jsonplaceholder_client, "/posts/1"),
                executor.submit(make_request, gorest_client, "/users"),
                executor.submit(make_request, httpbin_client, "/get"),
            ]

            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Verify all requests succeeded
        for status_code, duration in results:
            assert status_code == 200
            assert duration < 10.0, f"Concurrent request too slow: {duration}s"
