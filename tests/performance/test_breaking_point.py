"""
Breaking point performance testing for API endpoints.

This module finds the maximum sustainable request rate for API endpoints
using sophisticated async testing patterns and comprehensive metrics collection.
"""

import asyncio
import logging
import statistics
import sys
import time
from typing import Any, Dict

from faker import Faker

from .async_api_client import AsyncJSONPlaceholderClient
from .performance_metrics import PerformanceMetrics, TestResult

# Configure logging for clean output during performance tests
logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)
faker = Faker()


class BreakingPointTester:
    """
    Advanced breaking point tester for API endpoints.

    Finds the maximum sustainable request rate using binary search
    and comprehensive performance metrics.
    """

    def __init__(self):
        self.metrics = PerformanceMetrics()

        # Endpoint configurations based on expected performance characteristics
        self.endpoint_configs = {
            "posts": {
                "target_rps": 100,
                "max_test_rate": 300,
                "start_rate": 20,
                "use_case": "Content retrieval",
                "priority": "HIGH",
            },
            "users": {
                "target_rps": 50,
                "max_test_rate": 150,
                "start_rate": 10,
                "use_case": "User management",
                "priority": "HIGH",
            },
            "comments": {
                "target_rps": 30,
                "max_test_rate": 100,
                "start_rate": 5,
                "use_case": "Comment retrieval",
                "priority": "MEDIUM",
            },
            "create_operations": {
                "target_rps": 20,
                "max_test_rate": 60,
                "start_rate": 3,
                "use_case": "Data creation",
                "priority": "MEDIUM",
            },
        }

    async def verify_connectivity(self) -> bool:
        """Verify API connectivity using async clients."""
        try:
            async with AsyncJSONPlaceholderClient() as client:
                return await client.health_check()
        except Exception as e:
            logger.error(f"Connectivity check failed: {e}")
            return False

    async def test_rate_for_endpoint(
        self, endpoint: str, rate: int, duration: int = 10
    ) -> TestResult:
        """
        Test API performance at specific rate for a specific endpoint.

        Args:
            endpoint: Endpoint to test (posts, users, comments, etc.)
            rate: Requests per second to attempt
            duration: Test duration in seconds

        Returns:
            TestResult containing comprehensive metrics
        """
        try:
            interval = 1.0 / rate
            total_requests = rate * duration
            results = []

            async def make_api_call(request_id: int, client):
                """Make async API call with timing and error tracking."""
                start_time = time.time()

                try:
                    if endpoint == "posts":
                        status, data, duration = await client.get_posts()
                    elif endpoint == "users":
                        status, data, duration = await client.get_users()
                    elif endpoint == "comments":
                        status, data, duration = await client.get_comments()
                    elif endpoint == "single_post":
                        post_id = (request_id % 100) + 1  # Cycle through posts 1-100
                        status, data, duration = await client.get_post(post_id)
                    elif endpoint == "single_user":
                        user_id = (request_id % 10) + 1  # Cycle through users 1-10
                        status, data, duration = await client.get_user(user_id)
                    elif endpoint == "create_post":
                        post_data = {
                            "title": faker.sentence(nb_words=6),
                            "body": faker.text(max_nb_chars=200),
                            "userId": faker.random_int(min=1, max=10),
                        }
                        status, data, duration = await client.create_post(post_data)
                    else:
                        # Default to posts endpoint
                        status, data, duration = await client.get_posts()

                    total_duration = time.time() - start_time

                    return {
                        "request_id": request_id,
                        "status_code": status,
                        "duration": total_duration,
                        "api_duration": duration,
                        "success": 200 <= status < 400,
                        "timestamp": start_time,
                    }

                except Exception as e:
                    total_duration = time.time() - start_time
                    logger.debug(f"Request {request_id} failed: {e}")

                    return {
                        "request_id": request_id,
                        "status_code": 0,
                        "duration": total_duration,
                        "api_duration": 0,
                        "success": False,
                        "error": str(e),
                        "timestamp": start_time,
                    }

            # Execute performance test
            logger.info(f"Testing {endpoint} at {rate} RPS for {duration}s...")

            async with AsyncJSONPlaceholderClient() as client:
                start_time = time.time()

                # Create semaphore to control concurrency
                semaphore = asyncio.Semaphore(min(rate * 2, 100))

                async def controlled_request(request_id: int):
                    async with semaphore:
                        return await make_api_call(request_id, client)

                # Schedule requests with proper timing
                tasks = []
                for i in range(total_requests):
                    # Calculate when this request should start
                    target_time = start_time + (i * interval)
                    current_time = time.time()

                    if target_time > current_time:
                        await asyncio.sleep(target_time - current_time)

                    task = asyncio.create_task(controlled_request(i))
                    tasks.append(task)

                    # Batch process completed tasks to avoid memory buildup
                    if len(tasks) >= 50:
                        completed_results = await asyncio.gather(
                            *tasks, return_exceptions=True
                        )
                        for result in completed_results:
                            if not isinstance(result, Exception):
                                results.append(result)
                        tasks = []

                # Process remaining tasks
                if tasks:
                    completed_results = await asyncio.gather(
                        *tasks, return_exceptions=True
                    )
                    for result in completed_results:
                        if not isinstance(result, Exception):
                            results.append(result)

                actual_duration = time.time() - start_time

            # Calculate comprehensive metrics
            if not results:
                return TestResult(
                    endpoint=endpoint,
                    target_rps=rate,
                    actual_rps=0,
                    duration=actual_duration,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=total_requests,
                    avg_response_time=0,
                    p95_response_time=0,
                    p99_response_time=0,
                    min_response_time=0,
                    max_response_time=0,
                    error_rate=100.0,
                    success_rate=0.0,
                )

            # Extract metrics from results (filter out any exceptions)
            valid_results = [r for r in results if isinstance(r, dict)]
            successful_results = [r for r in valid_results if r["success"]]
            failed_results = [r for r in valid_results if not r["success"]]

            durations = [r["duration"] for r in successful_results]
            actual_rps = (
                len(valid_results) / actual_duration if actual_duration > 0 else 0
            )

            if durations:
                avg_response_time = statistics.mean(durations)
                p95_response_time = (
                    statistics.quantiles(durations, n=20)[18]
                    if len(durations) >= 20
                    else max(durations)
                )
                p99_response_time = (
                    statistics.quantiles(durations, n=100)[98]
                    if len(durations) >= 100
                    else max(durations)
                )
                min_response_time = min(durations)
                max_response_time = max(durations)
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
                min_response_time = max_response_time = 0

            success_rate = (
                (len(successful_results) / len(valid_results)) * 100
                if valid_results
                else 0
            )
            error_rate = (
                (len(failed_results) / len(valid_results)) * 100 if valid_results else 0
            )

            return TestResult(
                endpoint=endpoint,
                target_rps=rate,
                actual_rps=actual_rps,
                duration=actual_duration,
                total_requests=len(valid_results),
                successful_requests=len(successful_results),
                failed_requests=len(failed_results),
                avg_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                min_response_time=min_response_time,
                max_response_time=max_response_time,
                error_rate=error_rate,
                success_rate=success_rate,
            )

        except Exception as e:
            logger.error(f"Performance test failed for {endpoint} at {rate} RPS: {e}")
            return TestResult(
                endpoint=endpoint,
                target_rps=rate,
                actual_rps=0,
                duration=0,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                min_response_time=0,
                max_response_time=0,
                error_rate=100.0,
                success_rate=0.0,
            )

    async def find_breaking_point(
        self,
        endpoint: str,
        success_threshold: float = 95.0,
        response_time_threshold: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Find breaking point using binary search algorithm.

        Args:
            endpoint: Endpoint to test
            success_threshold: Minimum success rate percentage
            response_time_threshold: Maximum acceptable response time in seconds

        Returns:
            Dictionary with breaking point analysis
        """
        config = self.endpoint_configs.get(endpoint, self.endpoint_configs["posts"])

        low = config["start_rate"]
        high = config["max_test_rate"]
        breaking_point = low
        test_results = []

        logger.info(f"\n🔍 Finding breaking point for {endpoint}")
        logger.info(
            f"Target: {config['target_rps']} RPS | Use case: {config['use_case']}"
        )
        logger.info(f"Testing range: {low} - {high} RPS")
        logger.info("-" * 60)

        while low <= high:
            mid = (low + high) // 2

            logger.info(f"Testing {mid} RPS...")
            result = await self.test_rate_for_endpoint(endpoint, mid, duration=15)
            test_results.append(result)

            # Check if this rate meets our criteria
            meets_success_criteria = result.success_rate >= success_threshold
            meets_response_time_criteria = (
                result.p95_response_time <= response_time_threshold
            )

            if meets_success_criteria and meets_response_time_criteria:
                breaking_point = mid
                logger.info(
                    f"✅ {mid} RPS: Success rate {result.success_rate:.1f}%, "
                    f"P95 {result.p95_response_time:.3f}s"
                )
                low = mid + 1
            else:
                logger.info(
                    f"❌ {mid} RPS: Success rate {result.success_rate:.1f}%, "
                    f"P95 {result.p95_response_time:.3f}s"
                )
                high = mid - 1

        # Analyze results
        target_rps = config["target_rps"]
        target_met = breaking_point >= target_rps

        logger.info("-" * 60)
        logger.info(f"🎯 BREAKING POINT ANALYSIS for {endpoint}")
        logger.info(f"Breaking Point: {breaking_point} RPS")
        logger.info(
            f"Target RPS: {target_rps} ({'✅ MET' if target_met else '❌ NOT MET'})"
        )
        logger.info(
            f"Safety Margin: {((breaking_point / target_rps) - 1) * 100:.1f}%"
            if target_rps > 0
            else "N/A"
        )

        return {
            "endpoint": endpoint,
            "breaking_point_rps": breaking_point,
            "target_rps": target_rps,
            "target_met": target_met,
            "safety_margin_percent": (
                ((breaking_point / target_rps) - 1) * 100 if target_rps > 0 else 0
            ),
            "test_results": test_results,
            "use_case": config["use_case"],
            "priority": config["priority"],
        }

    async def run_comprehensive_breaking_point_analysis(self) -> Dict[str, Any]:
        """Run breaking point analysis for all configured endpoints."""
        if not await self.verify_connectivity():
            raise Exception("API connectivity check failed")

        logger.info("🚀 Starting Comprehensive Breaking Point Analysis")
        logger.info("=" * 60)

        results = {}

        for endpoint in ["posts", "users", "single_post", "single_user", "create_post"]:
            try:
                result = await self.find_breaking_point(endpoint)
                results[endpoint] = result

                # Brief pause between tests
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Failed to test {endpoint}: {e}")
                results[endpoint] = {"error": str(e)}

        # Summary report
        logger.info("\n" + "=" * 60)
        logger.info("📊 COMPREHENSIVE BREAKING POINT SUMMARY")
        logger.info("=" * 60)

        for endpoint, result in results.items():
            if "error" not in result:
                status = "✅ PASS" if result["target_met"] else "❌ FAIL"
                logger.info(
                    f"{endpoint:15} | {result['breaking_point_rps']:3d} RPS | {status}"
                )

        return results


# Pytest integration
import pytest  # noqa: E402


@pytest.mark.asyncio
@pytest.mark.performance
async def test_posts_breaking_point():
    """Test breaking point for posts endpoint."""
    tester = BreakingPointTester()
    result = await tester.find_breaking_point("posts")

    assert result["breaking_point_rps"] > 0
    assert "test_results" in result
    assert len(result["test_results"]) > 0


@pytest.mark.asyncio
@pytest.mark.performance
async def test_users_breaking_point():
    """Test breaking point for users endpoint."""
    tester = BreakingPointTester()
    result = await tester.find_breaking_point("users")

    assert result["breaking_point_rps"] > 0
    assert "test_results" in result


@pytest.mark.asyncio
@pytest.mark.performance
@pytest.mark.slow
async def test_comprehensive_breaking_point_analysis():
    """Run comprehensive breaking point analysis for all endpoints."""
    tester = BreakingPointTester()
    results = await tester.run_comprehensive_breaking_point_analysis()

    assert len(results) > 0

    # Verify at least some endpoints passed
    passed_endpoints = [
        ep
        for ep, result in results.items()
        if "error" not in result and result.get("target_met", False)
    ]

    assert len(passed_endpoints) > 0, "No endpoints met their performance targets"


# CLI execution
if __name__ == "__main__":

    async def main():
        tester = BreakingPointTester()
        await tester.run_comprehensive_breaking_point_analysis()

    asyncio.run(main())
