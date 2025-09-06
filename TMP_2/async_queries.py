import asyncio
import aiohttp
import time
from reputation_engine import Reputation

class AsyncQueryManager:
    def __init__(self, cache, rps):
        self.cache = cache
        self.rps = rps
        self.delay = 1 / rps  # זמן המתנה בין בקשות

    async def query_domain_with_retry(self, session, domain, retries=3, timeout=10):
        if domain in self.cache:
            print(f"[Cache] {domain} -> {self.cache[domain]}")
            return self.cache[domain]

        attempt = 0
        while attempt < retries:
            try:
                start = time.time()
                result = await asyncio.wait_for(Reputation(session, domain), timeout=timeout)
                end = time.time()
                result["response_time"] = end - start  # הוספת זמן תגובה לכל דומיין
                self.cache[domain] = result
                await asyncio.sleep(self.delay)  # ← מחכה בין בקשות
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
        async with aiohttp.ClientSession() as session:
            tasks = [self.query_domain_with_retry(session, d) for d in domains]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            print("\n--- Reputation Results ---")
            for r in results:
                print(r if not isinstance(r, Exception) else f"Error: {r}")

            return results  # ← חשוב! מחזיר את התוצאות
