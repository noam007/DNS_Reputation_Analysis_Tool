import pytest
from unittest.mock import Mock, AsyncMock
import asyncio

# from dns_reputation_tool import ReputationCache, ReputationEngine

class TestReputationCache:
    def test_cache_operations(self):
        cache = ReputationCache(ttl_seconds=1)
        result = Mock()
        result.domain = "test.com"
        cache.set("test.com", result)
        retrieved = cache.get("test.com")
        assert retrieved == result
        assert retrieved.domain == "test.com"

    def test_cache_expiration(self):
        import time
        cache = ReputationCache(ttl_seconds=0.1)
        result = Mock()
        result.domain = "test.com"
        cache.set("test.com", result)
        time.sleep(0.2)
        assert cache.get("test.com") is None


class TestReputationEngine:
    @pytest.mark.asyncio
    async def test_classify_reputation(self):
        engine = ReputationEngine()
        assert engine.classify_reputation(30) == "Untrusted"
        assert engine.classify_reputation(80) == "Trusted"
        assert engine.classify_reputation(61) == "Trusted"
        assert engine.classify_reputation(60) == "Untrusted"

    @pytest.mark.asyncio
    async def test_lookup_domain_success(self):
        engine = ReputationEngine()
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
