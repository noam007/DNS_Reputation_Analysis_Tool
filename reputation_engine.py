# import aiohttp
import asyncio
import time
import requests
# from monitor import Monitor, Result
# from utils import RateLimiter
# from config import SETTINGS

# API_URL = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/{domain}"
# HEADERS = {"Authorization": "Token I_am_under_stress_when_I_test"}

async def Reputation(session, domain):
    """Query VirusTotal asynchronously for domain reputation."""
    API_KEY = '02bd7bce541256f6642dad26bbee71a4271b64d772a181e3e92393c755ac8d32'

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": API_KEY}

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "domain": domain,
                    "reputation": data["data"]["attributes"].get("reputation"),
                    "categories": data["data"]["attributes"].get("categories"),
                    "stats": data["data"]["attributes"].get("last_analysis_stats")
                }
            elif response.status == 429:
                # Rate limit hit → wait and retry
                print(f"Rate limit hit for {domain}, retrying in 15s...")
                await asyncio.sleep(15)
                return await Reputation(session, domain)
            else:
                return {"domain": domain, "error": response.status}
    except Exception as e:
        return {"domain": domain, "error": str(e)}




# def Reputation(domain):
#     API_KEY = '02bd7bce541256f6642dad26bbee71a4271b64d772a181e3e92393c755ac8d32'
#     url = f"https://www.virustotal.com/api/v3/domains/{domain}"
#     headers = {
#         "x-apikey": API_KEY
#     }
#
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         data = response.json()
#         print(f"Domain: {domain}")
#         print("Reputation:", data["data"]["attributes"].get("reputation"))
#         print("Categories:", data["data"]["attributes"].get("categories"))
#         print("Last analysis stats:", data["data"]["attributes"].get("last_analysis_stats"))
#     else:
#         print("Error:", response.status_code, response.text)



    # response = requests.get(f"https://api.reputation.com/v1/domain/{domain}?apikey=YOUR_API_KEY")
    # print(response)
    # data = response.json()
    # print(domain, data["reputation"], data["category"])


# class AsyncReputationClient:
#     # def __init__(self):
#     #     base_url = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/{DOMAIN}"
#
#     def Reputation(self,domain):
#         response = requests.get(f"https://api.reputation.com/v1/domain/{domain}?apikey=YOUR_API_KEY")
#         data = response.json()
#         print(domain, data["reputation"], data["category"])



# here all the ASYC options !!
