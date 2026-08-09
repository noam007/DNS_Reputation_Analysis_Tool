# AsyncReputationClient
# Asynchronous client for querying the Reputation API. 
# It sends domain reputation requests concurrently using aiohttp, while using rate limiting and configuration settings to control API access and performance. 
# It also integrates monitoring and result handling for tracking API responses and request status.


import aiohttp
import asyncio
import time
from monitor import Monitor, Result
from utils import RateLimiter
from config import SETTINGS

API_URL = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/{domain}"
HEADERS = {"Authorization": "Token I_am_under_stress_when_I_test"}

class AsyncReputationClient:
    def __init__(self):
        base_url = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/{DOMAIN}"


# here all the ASYC options !!
