"""
Performance metrics collection and analysis for comprehensive API testing.

This module provides sophisticated metrics collection, analysis, and reporting
capabilities for performance testing scenarios.
"""

import json
import logging
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Comprehensive test result data structure."""

    endpoint: str
    target_rps: float
    actual_rps: float
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    error_rate: float
    success_rate: float
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class RequestMetric:
    """Individual request metric."""

    request_id: int
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: float
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceMetrics:
    """
    Advanced performance metrics collector and analyzer.

    Provides comprehensive metrics collection, statistical analysis,
    and professional reporting capabilities.
    """

    def __init__(self):
        self.request_metrics: List[RequestMetric] = []
        self.test_results: List[TestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start_collection(self):
        """Start metrics collection."""
        self.start_time = time.time()
        self.request_metrics.clear()
        logger.info("Started performance metrics collection")

    def stop_collection(self):
        """Stop metrics collection."""
        self.end_time = time.time()
        logger.info(
            f"Stopped performance metrics collection after {self.get_collection_duration():.2f}s"
        )

    def get_collection_duration(self) -> float:
        """Get total collection duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def record_request(
        self,
        request_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Record individual request metric."""
        metric = RequestMetric(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            timestamp=time.time(),
            success=success,
            error=error,
        )
        self.request_metrics.append(metric)

    def add_test_result(self, result: TestResult):
        """Add test result to collection."""
        self.test_results.append(result)

    def calculate_statistics(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate comprehensive statistics from response times."""
        if not response_times:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "p50": 0.0,
                "p90": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        sorted_times = sorted(response_times)
        n = len(sorted_times)

        stats = {
            "min": min(response_times),
            "max": max(response_times),
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "std_dev": statistics.stdev(response_times) if n > 1 else 0.0,
        }

        # Calculate percentiles
        percentiles = [50, 90, 95, 99]
        for p in percentiles:
            index = int((p / 100.0) * (n - 1))
            stats[f"p{p}"] = sorted_times[index]

        return stats

    def analyze_endpoint_performance(self, endpoint: str) -> Dict[str, Any]:
        """Analyze performance for specific endpoint."""
        endpoint_metrics = [m for m in self.request_metrics if m.endpoint == endpoint]

        if not endpoint_metrics:
            return {"error": f"No metrics found for endpoint: {endpoint}"}

        # Separate successful and failed requests
        successful_metrics = [m for m in endpoint_metrics if m.success]
        failed_metrics = [m for m in endpoint_metrics if not m.success]

        # Calculate response time statistics
        response_times = [m.response_time for m in successful_metrics]
        stats = self.calculate_statistics(response_times)

        # Calculate rates
        total_requests = len(endpoint_metrics)
        success_rate = (
            (len(successful_metrics) / total_requests) * 100
            if total_requests > 0
            else 0
        )
        error_rate = (
            (len(failed_metrics) / total_requests) * 100 if total_requests > 0 else 0
        )

        # Calculate throughput
        if endpoint_metrics:
            time_span = max(m.timestamp for m in endpoint_metrics) - min(
                m.timestamp for m in endpoint_metrics
            )
            throughput = total_requests / time_span if time_span > 0 else 0
        else:
            throughput = 0

        # Status code distribution
        status_codes: Dict[int, int] = {}
        for metric in endpoint_metrics:
            status_codes[metric.status_code] = (
                status_codes.get(metric.status_code, 0) + 1
            )

        # Error analysis
        errors: Dict[str, int] = {}
        for metric in failed_metrics:
            if metric.error:
                errors[metric.error] = errors.get(metric.error, 0) + 1

        return {
            "endpoint": endpoint,
            "total_requests": total_requests,
            "successful_requests": len(successful_metrics),
            "failed_requests": len(failed_metrics),
            "success_rate": success_rate,
            "error_rate": error_rate,
            "throughput_rps": throughput,
            "response_time_stats": stats,
            "status_code_distribution": status_codes,
            "error_distribution": errors,
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.request_metrics:
            return {"error": "No metrics collected"}

        # Overall statistics
        all_response_times = [
            m.response_time for m in self.request_metrics if m.success
        ]
        overall_stats = self.calculate_statistics(all_response_times)

        # Per-endpoint analysis
        endpoints = set(m.endpoint for m in self.request_metrics)
        endpoint_analysis = {}
        for endpoint in endpoints:
            endpoint_analysis[endpoint] = self.analyze_endpoint_performance(endpoint)

        # Overall metrics
        total_requests = len(self.request_metrics)
        successful_requests = len([m for m in self.request_metrics if m.success])
        failed_requests = total_requests - successful_requests

        # Time-based analysis
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            overall_throughput = total_requests / duration
        else:
            duration = 0
            overall_throughput = 0

        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (
                    (successful_requests / total_requests) * 100
                    if total_requests > 0
                    else 0
                ),
                "error_rate": (
                    (failed_requests / total_requests) * 100
                    if total_requests > 0
                    else 0
                ),
                "duration_seconds": duration,
                "overall_throughput_rps": overall_throughput,
                "response_time_stats": overall_stats,
            },
            "endpoint_analysis": endpoint_analysis,
            "test_results": [result.to_dict() for result in self.test_results],
            "collection_info": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": self.get_collection_duration(),
                "metrics_count": len(self.request_metrics),
            },
        }

    def export_metrics_csv(self, filename: str):
        """Export metrics to CSV file."""
        import csv

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "request_id",
                "endpoint",
                "method",
                "status_code",
                "response_time",
                "timestamp",
                "success",
                "error",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for metric in self.request_metrics:
                writer.writerow(metric.to_dict())

        logger.info(f"Exported {len(self.request_metrics)} metrics to {filename}")

    def export_report_json(self, filename: str):
        """Export performance report to JSON file."""
        report = self.generate_performance_report()

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Exported performance report to {filename}")

    def print_summary_report(self):
        """Print formatted summary report to console."""
        report = self.generate_performance_report()

        if "error" in report:
            logger.error(f"Report generation failed: {report['error']}")
            return

        summary = report["summary"]

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY REPORT")
        print("=" * 60)

        print(f"Total Requests:      {summary['total_requests']:,}")
        print(
            f"Successful:          {summary['successful_requests']:,} "
            f"({summary['success_rate']:.1f}%)"
        )
        print(
            f"Failed:              {summary['failed_requests']:,} ({summary['error_rate']:.1f}%)"
        )
        print(f"Duration:            {summary['duration_seconds']:.2f}s")
        print(f"Throughput:          {summary['overall_throughput_rps']:.2f} RPS")

        print("\nResponse Time Statistics:")
        stats = summary["response_time_stats"]
        print(f"  Average:           {stats['mean']:.3f}s")
        print(f"  Median:            {stats['median']:.3f}s")
        print(f"  95th Percentile:   {stats['p95']:.3f}s")
        print(f"  99th Percentile:   {stats['p99']:.3f}s")
        print(f"  Min/Max:           {stats['min']:.3f}s / {stats['max']:.3f}s")

        print("\nPer-Endpoint Analysis:")
        for endpoint, analysis in report["endpoint_analysis"].items():
            if "error" not in analysis:
                print(f"  {endpoint}:")
                print(f"    Requests:        {analysis['total_requests']:,}")
                print(f"    Success Rate:    {analysis['success_rate']:.1f}%")
                print(
                    f"    Avg Response:    {analysis['response_time_stats']['mean']:.3f}s"
                )
                print(
                    f"    P95 Response:    {analysis['response_time_stats']['p95']:.3f}s"
                )

        print("=" * 60)

    def clear_metrics(self):
        """Clear all collected metrics."""
        self.request_metrics.clear()
        self.test_results.clear()
        self.start_time = None
        self.end_time = None
        logger.info("Cleared all performance metrics")
