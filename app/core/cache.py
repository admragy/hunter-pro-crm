"""
Hunter Pro CRM Ultimate Enterprise - Cache Module
Version: 7.0.0
Redis caching system with async support
"""

import json
import logging
from typing import Any, Optional
from datetime import timedelta

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Async Redis cache manager"""
    
    def __init__(self):
        self.redis = None
        self.enabled = settings.CACHE_ENABLED and REDIS_AVAILABLE
        self.default_ttl = settings.CACHE_TTL
        
        if not REDIS_AVAILABLE:
            logger.warning("⚠️ Redis not available - caching disabled")
    
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
        
        try:
            self.redis = await aioredis.create_redis_pool(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD or None,
                minsize=5,
                maxsize=settings.REDIS_MAX_CONNECTIONS,
                timeout=settings.REDIS_SOCKET_TIMEOUT,
            )
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.enabled = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("✅ Redis cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in cache"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache get TTL error for key {key}: {e}")
            return None


# Global cache instance
cache = CacheManager()


# Decorator for caching function results
def cached(ttl: int = None, key_prefix: str = "cache"):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=3600, key_prefix="user")
        async def get_user(user_id: int):
            # expensive operation
            return user
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in kwargs.items()])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Helper functions
async def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        await cache.connect()
        if cache.redis:
            await cache.set("test_key", "test_value", 10)
            result = await cache.get("test_key")
            await cache.delete("test_key")
            return result == "test_value"
        return False
    except Exception as e:
        logger.error(f"Redis test failed: {e}")
        return False


# Cache key generators
def user_cache_key(user_id: int) -> str:
    """Generate cache key for user"""
    return f"user:{user_id}"


def customer_cache_key(customer_id: int) -> str:
    """Generate cache key for customer"""
    return f"customer:{customer_id}"


def deal_cache_key(deal_id: int) -> str:
    """Generate cache key for deal"""
    return f"deal:{deal_id}"


def campaign_cache_key(campaign_id: int) -> str:
    """Generate cache key for campaign"""
    return f"campaign:{campaign_id}"


if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test cache functions"""
        print("🧪 Testing cache...")
        
        # Connect
        await cache.connect()
        
        # Set
        await cache.set("test:key", {"name": "Test", "value": 123}, 60)
        print("✅ Set value")
        
        # Get
        result = await cache.get("test:key")
        print(f"✅ Get value: {result}")
        
        # Increment
        await cache.set("test:counter", 0, 60)
        count = await cache.increment("test:counter", 5)
        print(f"✅ Increment: {count}")
        
        # Delete
        await cache.delete("test:key")
        await cache.delete("test:counter")
        print("✅ Deleted keys")
        
        # Disconnect
        await cache.disconnect()
        
        print("✅ Cache tests completed")
    
    asyncio.run(test())