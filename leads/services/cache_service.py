# leads/services/cache_service.py
"""
Cache Service for Lead Finder System.
Provides centralized caching logic with Redis backend.
Improves performance by reducing API calls and database queries.
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from functools import wraps

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('leads')


class CacheService:
    """
    Centralized caching service for the application.
    Handles cache key generation, TTL management, and cache invalidation.
    """
    
    # Cache key prefixes for different data types
    PREFIX_API_RESPONSE = 'api:response'
    PREFIX_LEAD_SEARCH = 'leads:search'
    PREFIX_LEAD_DETAIL = 'leads:detail'
    PREFIX_LIST_DETAIL = 'list:detail'
    PREFIX_LIST_ALL = 'list:all'
    
    @staticmethod
    def generate_key(prefix: str, identifier: Any) -> str:
        """
        Generate a consistent cache key.
        
        Args:
            prefix: Cache key prefix (e.g., 'api:response')
            identifier: Unique identifier (dict, string, int, etc.)
        
        Returns:
            str: Generated cache key
        
        Example:
            >>> CacheService.generate_key('api:response', {'title': 'Engineer'})
            'api:response:a3d5f...'
        """
        if isinstance(identifier, dict):
            # Sort dict to ensure consistent hashing
            identifier_str = json.dumps(identifier, sort_keys=True)
        else:
            identifier_str = str(identifier)
        
        # Generate MD5 hash for long identifiers
        hash_obj = hashlib.md5(identifier_str.encode('utf-8'))
        hash_key = hash_obj.hexdigest()
        
        return f"{prefix}:{hash_key}"
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
        
        Returns:
            Cached value or default
        """
        try:
            value = cache.get(key, default)
            if value is not None:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return default
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: TTL in seconds (None = use default from settings)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if timeout is None:
                timeout = settings.CACHES['default']['TIMEOUT']
            
            cache.set(key, value, timeout)
            logger.debug(f"Cache SET: {key} (TTL: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            bool: True if successful
        """
        try:
            cache.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., 'leads:search:*')
        
        Returns:
            int: Number of keys deleted
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Find all keys matching pattern
            full_pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:{pattern}"
            keys = redis_conn.keys(full_pattern)
            
            if keys:
                count = redis_conn.delete(*keys)
                logger.info(f"Cache PATTERN DELETE: {pattern} ({count} keys)")
                return count
            
            return 0
        except Exception as e:
            logger.error(f"Cache PATTERN DELETE error for {pattern}: {e}")
            return 0
    
    @classmethod
    def cache_api_response(
        cls,
        filters: Dict,
        response_data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache API response data.
        
        Args:
            filters: Search filters used for the API call
            response_data: API response to cache
            ttl: Time to live in seconds
        
        Returns:
            bool: Success status
        """
        if ttl is None:
            ttl = settings.CACHE_TTL_API_RESPONSE
        
        key = cls.generate_key(cls.PREFIX_API_RESPONSE, filters)
        return cls.set(key, response_data, ttl)
    
    @classmethod
    def get_cached_api_response(cls, filters: Dict) -> Optional[Dict]:
        """
        Get cached API response.
        
        Args:
            filters: Search filters
        
        Returns:
            Cached response or None
        """
        key = cls.generate_key(cls.PREFIX_API_RESPONSE, filters)
        return cls.get(key)
    
    @classmethod
    def cache_lead_search(
        cls,
        filters: Dict,
        results: List[Dict],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache lead search results.
        
        Args:
            filters: Search filters
            results: Search results
            ttl: Time to live in seconds
        
        Returns:
            bool: Success status
        """
        if ttl is None:
            ttl = settings.CACHE_TTL_LEADS_SEARCH
        
        key = cls.generate_key(cls.PREFIX_LEAD_SEARCH, filters)
        return cls.set(key, results, ttl)
    
    @classmethod
    def get_cached_lead_search(cls, filters: Dict) -> Optional[List[Dict]]:
        """
        Get cached lead search results.
        
        Args:
            filters: Search filters
        
        Returns:
            Cached results or None
        """
        key = cls.generate_key(cls.PREFIX_LEAD_SEARCH, filters)
        return cls.get(key)
    
    @classmethod
    def invalidate_lead_search_cache(cls) -> int:
        """
        Invalidate all lead search caches.
        Useful when new leads are added or filters change.
        
        Returns:
            int: Number of keys invalidated
        """
        return cls.delete_pattern(f"{cls.PREFIX_LEAD_SEARCH}:*")
    
    @classmethod
    def cache_list_data(cls, list_id: int, data: Dict, ttl: Optional[int] = None) -> bool:
        """
        Cache list data.
        
        Args:
            list_id: LeadList ID
            data: List data to cache
            ttl: Time to live in seconds
        
        Returns:
            bool: Success status
        """
        if ttl is None:
            ttl = settings.CACHE_TTL_LISTS
        
        key = cls.generate_key(cls.PREFIX_LIST_DETAIL, list_id)
        return cls.set(key, data, ttl)
    
    @classmethod
    def get_cached_list_data(cls, list_id: int) -> Optional[Dict]:
        """
        Get cached list data.
        
        Args:
            list_id: LeadList ID
        
        Returns:
            Cached data or None
        """
        key = cls.generate_key(cls.PREFIX_LIST_DETAIL, list_id)
        return cls.get(key)
    
    @classmethod
    def invalidate_list_cache(cls, list_id: Optional[int] = None) -> int:
        """
        Invalidate list caches.
        
        Args:
            list_id: Specific list ID, or None to invalidate all
        
        Returns:
            int: Number of keys invalidated
        """
        if list_id:
            key = cls.generate_key(cls.PREFIX_LIST_DETAIL, list_id)
            return 1 if cls.delete(key) else 0
        else:
            # Invalidate all lists
            count = cls.delete_pattern(f"{cls.PREFIX_LIST_DETAIL}:*")
            count += cls.delete_pattern(f"{cls.PREFIX_LIST_ALL}:*")
            return count


def cache_result(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key from args/kwargs
    
    Example:
        @cache_result('lead:detail', ttl=3600)
        def get_lead_detail(lead_id):
            return Lead.objects.get(id=lead_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function args as identifier
                identifier = {
                    'args': args,
                    'kwargs': kwargs
                }
                cache_key = CacheService.generate_key(key_prefix, identifier)
            
            # Try to get from cache
            cached_value = CacheService.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Function cache HIT: {func.__name__}")
                return cached_value
            
            # Execute function
            logger.debug(f"Function cache MISS: {func.__name__}")
            result = func(*args, **kwargs)
            
            # Cache result
            CacheService.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Convenience function for clearing all application caches
def clear_all_caches() -> Dict[str, int]:
    """
    Clear all application caches.
    
    Returns:
        Dict with counts of cleared keys per category
    """
    results = {
        'api_responses': CacheService.delete_pattern(f"{CacheService.PREFIX_API_RESPONSE}:*"),
        'lead_searches': CacheService.delete_pattern(f"{CacheService.PREFIX_LEAD_SEARCH}:*"),
        'list_details': CacheService.delete_pattern(f"{CacheService.PREFIX_LIST_DETAIL}:*"),
        'list_all': CacheService.delete_pattern(f"{CacheService.PREFIX_LIST_ALL}:*"),
    }
    
    total = sum(results.values())
    logger.info(f"Cleared {total} cache keys: {results}")
    
    return results