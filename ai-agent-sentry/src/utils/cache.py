"""
Redis Cache for Enterprise Performance
Handles 10,000+ agents with millisecond response
"""

import redis
import json
import hashlib
from typing import Any, Dict, Optional
from datetime import timedelta
import os
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Enterprise Redis cache manager"""
    
    def __init__(self, redis_url=None):
        """Initialize Redis connection"""
        if not redis_url:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        self.redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Cache settings
        self.ttl_default = 300  # 5 minutes
        self.ttl_short = 60     # 1 minute
        self.ttl_long = 3600    # 1 hour
        
        logger.info(f"✅ Redis connected: {redis_url}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set in cache"""
        try:
            if not ttl:
                ttl = self.ttl_default
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    def delete(self, key: str):
        """Delete from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern failed: {e}")
            return False
    
    # ============================================
    # SPECIFIC CACHE METHODS
    # ============================================
    
    def cache_agent(self, agent_id: str, agent_data: Dict):
        """Cache agent data"""
        key = f"agent:{agent_id}"
        self.set(key, agent_data, self.ttl_short)
    
    def get_cached_agent(self, agent_id: str) -> Optional[Dict]:
        """Get cached agent"""
        key = f"agent:{agent_id}"
        return self.get(key)
    
    def cache_agent_list(self, company_id: str, agents: list):
        """Cache agent list for company"""
        key = f"company:agents:{company_id}"
        self.set(key, agents, self.ttl_short)
    
    def get_cached_agent_list(self, company_id: str) -> Optional[list]:
        """Get cached agent list"""
        key = f"company:agents:{company_id}"
        return self.get(key)
    
    def cache_activity(self, activity_id: str, activity_data: Dict):
        """Cache activity"""
        key = f"activity:{activity_id}"
        self.set(key, activity_data, self.ttl_short)
    
    def cache_stats(self, stats_key: str, stats_data: Dict):
        """Cache statistics"""
        key = f"stats:{stats_key}"
        self.set(key, stats_data, self.ttl_short)
    
    def get_cached_stats(self, stats_key: str) -> Optional[Dict]:
        """Get cached statistics"""
        key = f"stats:{stats_key}"
        return self.get(key)
    
    def invalidate_agent_cache(self, agent_id: str):
        """Invalidate agent cache"""
        self.delete(f"agent:{agent_id}")
        # Also invalidate list caches
        self.clear_pattern("company:agents:*")
    
    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            return self.redis_client.ping()
        except:
            return False