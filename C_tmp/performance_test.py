import asyncio
import time
import statistics
import random
import string
from typing import List
# from dns_reputation_tool import ReputationEngine

class PerformanceTester:
    def __init__(self):
        self.results = []

    def generate_random_domains(self, count: int) -> List[str]:
        domains = []
        tlds = ['.com', '.net', '.org', '.io', '.gov', '.edu']
        for _ in range(count):
            name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15)))
            tld = random.choice(tlds)
            domains.append(f"{name}{tld}")
        return domains

    async def test_reputation_engine_performance(self, domain_count: int = 100):
        print(f"Testing reputation engine with {domain_count} domains...")
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
            total_time = time.time() - start_time
            successful = sum(1 for r in results if r.success)
            response_times = [r.response_time for r in results if r.success]
            stats = engine.get_statistics()

            print("\nPerformance Test Results:")
            print(f"Total time: {total_time:.2f}s, Success: {successful}/{len(domains)}")
            if response_times:
                print(f"Response Avg: {statistics.mean(response_times):.3f}s")
            print(f"Cache hit rate: {stats['cache_hits']/max(stats['total_requests'],1)*100:.1f}%")

        except Exception as e:
            print(f"Performance test failed: {e}")

    async def test_concurrent_load(self, concurrent_batches: int = 3, domains_per_batch: int = 50):
        print(f"Testing {concurrent_batches} batches of {domains_per_batch} domains each")
        async def run_batch(batch_id: int):
            engine = ReputationEngine(rate_limit_rps=15.0)
            domains = set(self.generate_random_domains(domains_per_batch))
            start_time = time.time()
            results = await engine.batch_lookup(domains)
            print(f"Batch {batch_id} done in {time.time()-start_time:.2f}s")
            return results

        start_time = time.time()
        all_results = await asyncio.gather(*[run_batch(i) for i in range(concurrent_batches)])
        total_domains = sum(len(batch) for batch in all_results)
        total_successful = sum(sum(1 for r in batch if r.success) for batch in all_results)
        print(f"\nConcurrent Load Results: {total_successful}/{total_domains} "
              f"({total_successful/total_domains*100:.1f}%) in {time.time()-start_time:.2f}s")

async def run_performance_tests():
    tester = PerformanceTester()
    await tester.test_reputation_engine_performance(100)
    await tester.test_concurrent_load(3, 30)

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
