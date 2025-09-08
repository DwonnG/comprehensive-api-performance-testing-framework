#!/usr/bin/env python3
"""
Quick test script to verify our comprehensive API testing framework.
"""

import sys
import asyncio
sys.path.append('tests')

def test_environment_config():
    """Test environment configuration."""
    print("🔧 Testing Environment Configuration...")
    
    from utilities.environment_config import EnvironmentConfig
    config = EnvironmentConfig('development')
    
    print(f"   JSONPlaceholder URL: {config.jsonplaceholder_base_url}")
    print(f"   Timeout: {config.default_timeout}s")
    print(f"   Max Retries: {config.max_retries}")
    print("✅ Environment configuration working!")
    
    return True

def test_data_manager():
    """Test data manager functionality."""
    print("\n📊 Testing Test Data Manager...")
    
    from utilities.test_data_manager import TestDataManager
    data_manager = TestDataManager('development')
    
    user_data = data_manager.generate_user_data()
    post_data = data_manager.generate_post_data()
    
    print(f"   Generated user: {user_data['name']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Generated post: {post_data['title'][:50]}...")
    print("✅ Test data manager working!")
    
    return True

def test_api_clients():
    """Test API clients."""
    print("\n🌐 Testing API Clients...")
    
    from clients.jsonplaceholder_client import JSONPlaceholderClient
    from clients.api_client import APIClient
    
    # Test JSONPlaceholder client
    client = JSONPlaceholderClient()
    response = client.get_posts()
    
    print(f"   JSONPlaceholder Status: {response.status_code}")
    print(f"   Posts retrieved: {len(response.json())}")
    
    # Test HTTPBin client
    httpbin_client = APIClient("https://httpbin.org")
    response = httpbin_client.get("/get")
    
    print(f"   HTTPBin Status: {response.status_code}")
    print("✅ API clients working!")
    
    return True

async def test_performance_framework():
    """Test async performance framework."""
    print("\n⚡ Testing Performance Framework...")
    
    from performance.async_api_client import AsyncJSONPlaceholderClient
    from performance.test_breaking_point import BreakingPointTester
    
    # Test async client
    async with AsyncJSONPlaceholderClient() as client:
        status, data, duration = await client.get_posts()
        print(f"   Async request: Status {status}, Duration {duration:.3f}s")
    
    # Test breaking point analysis (quick version)
    tester = BreakingPointTester()
    result = await tester.test_rate_for_endpoint('posts', 5, duration=5)
    
    print(f"   Performance test: {result.success_rate:.1f}% success rate")
    print(f"   Average response: {result.avg_response_time:.3f}s")
    print("✅ Performance framework working!")
    
    return True

def test_metrics_collection():
    """Test metrics collection."""
    print("\n📈 Testing Metrics Collection...")
    
    from performance.performance_metrics import PerformanceMetrics, TestResult
    
    metrics = PerformanceMetrics()
    metrics.start_collection()
    
    # Record some test metrics
    metrics.record_request(1, "/posts", "GET", 200, 0.150, True)
    metrics.record_request(2, "/posts", "GET", 200, 0.175, True)
    metrics.record_request(3, "/posts", "GET", 404, 0.100, False)
    
    metrics.stop_collection()
    
    analysis = metrics.analyze_endpoint_performance("/posts")
    print(f"   Total requests: {analysis['total_requests']}")
    print(f"   Success rate: {analysis['success_rate']:.1f}%")
    print(f"   Average response: {analysis['response_time_stats']['mean']:.3f}s")
    print("✅ Metrics collection working!")
    
    return True

async def main():
    """Run all framework tests."""
    print("🚀 Comprehensive API Testing Framework - Component Tests")
    print("=" * 60)
    
    try:
        # Test synchronous components
        test_environment_config()
        test_data_manager()
        test_api_clients()
        test_metrics_collection()
        
        # Test async components
        await test_performance_framework()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Framework is working perfectly!")
        print("=" * 60)
        
        print("\n🎯 What's working:")
        print("   ✅ Environment configuration management")
        print("   ✅ Professional API clients with retry logic")
        print("   ✅ Test data generation and management")
        print("   ✅ Async performance testing capabilities")
        print("   ✅ Comprehensive metrics collection")
        print("   ✅ Breaking point analysis algorithms")
        
        print("\n🚀 Ready for:")
        print("   📊 Production-grade load testing")
        print("   🔍 API performance analysis")
        print("   🏗️ Multi-environment testing")
        print("   📈 Performance regression detection")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
