# Content is user - generated and unverified.
# test_dns_reputation_tool.py
import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import aiohttp


# Import the main components (assuming they're in the same file or properly structured)
# from dns_reputation_tool import DNSExtractor, ReputationEngine, ReputationCache, TrafficReplayManager

class TestReputationCache:
    def test_cache_operations(self):
        """Test basic cache operations"""
        cache = ReputationCache(ttl_seconds=1)

        # Create a mock result
        result = Mock()
        result.domain = "test.com"

        # Test set and get
        cache.set("test.com", result)
        retrieved = cache.get("test.com")

        assert retrieved == result
        assert retrieved.domain == "test.com"

    def test_cache_expiration(self):
        """Test cache expiration"""
        import time
        cache = ReputationCache(ttl_seconds=0.1)  # Very short TTL

        result = Mock()
        result.domain = "test.com"

        cache.set("test.com", result)
        time.sleep(0.2)  # Wait for expiration

        retrieved = cache.get("test.com")
        assert retrieved is None


class TestReputationEngine:
    @pytest.mark.asyncio
    async def test_classify_reputation(self):
        """Test reputation classification"""
        engine = ReputationEngine()

        assert engine.classify_reputation(30) == "Untrusted"
        assert engine.classify_reputation(80) == "Trusted"
        assert engine.classify_reputation(61) == "Trusted"
        assert engine.classify_reputation(60) == "Untrusted"

    @pytest.mark.asyncio
    async def test_lookup_domain_success(self):
        """Test successful domain lookup"""
        engine = ReputationEngine()

        # Mock aiohttp session response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "address": "google.com",
            "reputation": 95,
            "categories": ["general"]
        }

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await engine.lookup_domain(mock_session, "google.com")

        assert result.domain == "google.com"
        assert result.reputation == 95
        assert result.classification == "Trusted"
        assert result.success is True


# example_usage.py
"""
Example usage of the DNS Reputation Analysis Tool
"""

import asyncio
import logging
from pathlib import Path

# Configure logging for example
logging.basicConfig(level=logging.INFO)


async def example_basic_analysis():
    """Example: Basic analysis of a PCAP file"""

    # This would be a real PCAP file in practice
    pcap_file = "sample_dns_traffic.pcap"

    if not Path(pcap_file).exists():
        print(f"PCAP file {pcap_file} not found. Please provide a valid PCAP file.")
        return

    # Create the manager
    manager = TrafficReplayManager(
        pcap_file=pcap_file,
        output_dir="example_output",
        rate_limit=5.0,  # Conservative rate limit
        timeout=120  # 2 minute timeout
    )

    # Run the analysis
    print("Starting DNS reputation analysis...")
    success = await manager.run_analysis()

    if success:
        print("Analysis completed successfully!")
        print("Check the 'example_output' directory for results.")
    else:
        print("Analysis failed. Check the logs for details.")


def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "api": {
            "base_url": "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking",
            "headers": {
                "Authorization": "Token I_am_under_stress_when_I_test"
            },
            "timeout": 5.0,
            "max_retries": 3
        },
        "engine": {
            "rate_limit_rps": 10.0,
            "cache_ttl_seconds": 3600,
            "max_concurrent_requests": 50
        },
        "analysis": {
            "default_timeout": 300,
            "reputation_thresholds": {
                "trusted_min": 61,
                "untrusted_max": 60
            }
        }
    }

    with open("sample_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Sample configuration saved to sample_config.json")


if __name__ == "__main__":
    print("DNS Reputation Analysis Tool - Examples")
    print("1. Creating sample configuration...")
    create_sample_config()

    print("\n2. To run basic analysis:")
    print("   python dns_reputation_tool.py your_pcap_file.pcap")

    # Uncomment the following line to run the example analysis
    # asyncio.run(example_basic_analysis())

# performance_test.py
"""
Performance testing utilities for the DNS Reputation Analysis Tool
"""

import asyncio
import time
import statistics
from typing import List
import random
import string


class PerformanceTester:
    """Performance testing utilities"""

    def __init__(self):
        self.results = []

    def generate_random_domains(self, count: int) -> List[str]:
        """Generate random domain names for testing"""
        domains = []
        tlds = ['.com', '.net', '.org', '.io', '.gov', '.edu']

        for _ in range(count):
            # Generate random domain name
            length = random.randint(5, 15)
            domain_name = ''.join(random.choices(string.ascii_lowercase, k=length))
            tld = random.choice(tlds)
            domains.append(f"{domain_name}{tld}")

        return domains

    async def test_reputation_engine_performance(self, domain_count: int = 100):
        """Test reputation engine performance with random domains"""
        print(f"Testing reputation engine with {domain_count} domains...")

        # Create engine with higher rate limits for testing
        engine = ReputationEngine(rate_limit_rps=20.0)
        domains = set(self.generate_random_domains(domain_count))

        start_time = time.time()

        def progress_callback(completed, total):
            if completed % 20 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"Progress: {completed}/{total} ({rate:.1f} domains/sec)")

        try:
            results = await engine.batch_lookup(domains, progress_callback)
            end_time = time.time()

            # Analyze results
            total_time = end_time - start_time
            successful = sum(1 for r in results if r.success)
            response_times = [r.response_time for r in results if r.success]

            stats = engine.get_statistics()

            print(f"\nPerformance Test Results:")
            print(f"Total domains: {len(domains)}")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Average rate: {len(domains) / total_time:.2f} domains/sec")
            print(f"Successful lookups: {successful}/{len(domains)} ({successful / len(domains) * 100:.1f}%)")

            if response_times:
                print(f"Response time stats:")
                print(f"  Average: {statistics.mean(response_times):.3f}s")
                print(f"  Median: {statistics.median(response_times):.3f}s")
                print(f"  Min: {min(response_times):.3f}s")
                print(f"  Max: {max(response_times):.3f}s")

            print(f"Cache hit rate: {stats['cache_hits'] / max(stats['total_requests'], 1) * 100:.1f}%")

        except Exception as e:
            print(f"Performance test failed: {e}")

    async def test_concurrent_load(self, concurrent_batches: int = 3, domains_per_batch: int = 50):
        """Test concurrent load handling"""
        print(f"Testing concurrent load: {concurrent_batches} batches of {domains_per_batch} domains each")

        async def run_batch(batch_id: int):
            engine = ReputationEngine(rate_limit_rps=15.0)
            domains = set(self.generate_random_domains(domains_per_batch))

            start_time = time.time()
            results = await engine.batch_lookup(domains)
            end_time = time.time()

            successful = sum(1 for r in results if r.success)
            print(f"Batch {batch_id}: {successful}/{len(domains)} successful in {end_time - start_time:.2f}s")

            return results

        start_time = time.time()
        tasks = [run_batch(i) for i in range(concurrent_batches)]
        all_results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_domains = sum(len(batch) for batch in all_results)
        total_successful = sum(sum(1 for r in batch if r.success) for batch in all_results)

        print(f"\nConcurrent Load Test Results:")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Total domains processed: {total_domains}")
        print(f"Overall success rate: {total_successful / total_domains * 100:.1f}%")
        print(f"Effective throughput: {total_domains / (end_time - start_time):.2f} domains/sec")


async def run_performance_tests():
    """Run all performance tests"""
    tester = PerformanceTester()

    print("=== DNS Reputation Tool Performance Tests ===\n")

    # Test 1: Basic performance
    await tester.test_reputation_engine_performance(100)
    print("\n" + "=" * 50 + "\n")

    # Test 2: Concurrent load
    await tester.test_concurrent_load(3, 30)
    print("\n" + "=" * 50 + "\n")

    print("Performance tests completed!")


if __name__ == "__main__":
    # Run performance tests
    asyncio.run(run_performance_tests())
