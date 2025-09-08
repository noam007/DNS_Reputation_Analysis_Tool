# DNS reputation checker for all domains

# this file is reputation_engine.py
# import aiohttp
import asyncio
import time
import requests
import json

# from monitor import Monitor, Result
# from utils import RateLimiter
# from config import SETTINGS

# API_URL = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/{domain}"
# HEADERS = {"Authorization": "Token I_am_under_stress_when_I_test"}


all_results = []  # global list to store all results

def append_result(result):
    """Add a single dict to the list of all results"""
    all_results.append(result)
    print(f"all_results ******************   {all_results}")


def save_results_json(json_file="results.json"):
    """Save all results to a JSON file"""
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    print(f"Results saved to '{json_file}'")


async def Reputation(session, domain):
    """Query VirusTotal asynchronously for domain reputation."""
    API_KEY = '02bd7bce541256f6642dad26bbee71a4271b64d772a181e3e92393c755ac8d32'
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": API_KEY}

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                result = {
                    "domain": domain,
                    "reputation": data["data"]["attributes"].get("reputation"),
                    "categories": data["data"]["attributes"].get("categories"),
                    "stats": data["data"]["attributes"].get("last_analysis_stats"),
                          }

                append_result(result)
                return result

            elif response.status == 429:
                # Rate limit hit → wait and retry
                print(f"Rate limit hit for {domain}, retrying in 15s...")
                await asyncio.sleep(15)
                return await Reputation(session, domain)
            else:
                return {"domain": domain, "error": response.status}
    except Exception as e:
        return {"domain": domain, "error": str(e)}
