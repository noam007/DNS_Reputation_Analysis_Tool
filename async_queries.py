import asyncio
import time

import aiohttp
from asynciolimiter import Limiter

from reputation_engine import Reputation


class AsyncQueryManager:
    def __init__(self, rps):
        """
        Initializes the AsyncQueryManager.
        - rps: requests per second (used by Limiter to control request rate).
        - cache: stores domain query results to avoid duplicate lookups.
        """
        self.cache = {}
        self.limiter = Limiter(rps)

    async def query_domain_with_retry(self, session, domain, retries=3, timeout=10):
        """
        Queries the reputation of a single domain with retry logic.
        - Uses cache if the domain was already queried.
        - Retries up to 'retries' times if the request fails.
        - Applies a timeout for each query.
        - Records the response time for performance tracking.
        - Returns a dict with domain reputation data or error details.
        """
        if domain in self.cache:
            print(f"[Cache] {domain} -> {self.cache[domain]}")
            return self.cache[domain]

        attempt = 0
        while attempt < retries:
            try:
                await self.limiter.wait()
                start = time.time()
                result = await asyncio.wait_for(Reputation(session, domain), timeout=timeout)
                end = time.time()
                result["response_time"] = end - start  # add response time for each domain
                self.cache[domain] = result
                await asyncio.sleep(self.delay)  # ← wait between requests
                return result
            except Exception as e:
                attempt += 1
                print(f"[Retry {attempt}] Domain {domain} failed: {e}")
                if attempt >= retries:
                    result = {"domain": domain, "error": str(e), "response_time": None}
                    self.cache[domain] = result
                    return result
        return None

    async def query_domains(self, domains):
        """
        Queries reputation for a list of domains concurrently.
        - Creates async tasks for each domain.
        - Gathers all results (or exceptions if they occur).
        - Prints results to the console.
        - Returns a list of results for further processing.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.query_domain_with_retry(session, d) for d in domains]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            print("\n--- Reputation Results ---")
            for r in results:
                print(r if not isinstance(r, Exception) else f"Error: {r}")

            return results  # ← important! returns all results

    @staticmethod
    def cancel_all_tasks():
        """
        Cancels all currently running asyncio tasks.
        Useful for graceful shutdown (e.g., when receiving Ctrl+C).
        """
        # get all tasks
        tasks = asyncio.all_tasks()
        # cancel all tasks
        for task in tasks:
            # request the task cancel
            task.cancel()
