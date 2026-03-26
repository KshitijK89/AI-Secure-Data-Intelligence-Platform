"""
Performance monitoring and optimization utilities
Provides decorators and helpers for monitoring and improving performance
"""

import time
import functools
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    Works with both sync and async functions
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        elapsed = end_time - start_time
        logger.info(f"{func.__name__} took {elapsed:.4f} seconds")
        
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        elapsed = end_time - start_time
        logger.info(f"{func.__name__} took {elapsed:.4f} seconds")
        
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class PerformanceMonitor:
    """
    Monitor and track performance metrics
    """
    
    def __init__(self):
        self.metrics = {}
        self.call_counts = {}
    
    def record(self, operation: str, duration: float):
        """Record the duration of an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []
            self.call_counts[operation] = 0
        
        self.metrics[operation].append(duration)
        self.call_counts[operation] += 1
    
    def get_stats(self, operation: str = None):
        """Get statistics for operations"""
        if operation:
            if operation not in self.metrics:
                return None
            
            durations = self.metrics[operation]
            return {
                "operation": operation,
                "count": self.call_counts[operation],
                "avg": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
                "total": sum(durations)
            }
        else:
            # Return stats for all operations
            return {
                op: self.get_stats(op) 
                for op in self.metrics.keys()
            }
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.call_counts.clear()


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


class BatchProcessor:
    """
    Efficiently process items in batches with async support
    """
    
    def __init__(self, batch_size: int = 100, max_concurrent: int = 4):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
    
    async def process_async(self, items: list, processor: Callable) -> list:
        """
        Process items in batches asynchronously
        
        Args:
            items: List of items to process
            processor: Async function to process each item
        
        Returns:
            List of results
        """
        results = []
        
        # Create batches
        batches = [
            items[i:i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]
        
        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_batch(batch):
            async with semaphore:
                batch_results = []
                for item in batch:
                    result = await processor(item)
                    batch_results.append(result)
                return batch_results
        
        # Process all batches
        all_batch_results = await asyncio.gather(
            *[process_batch(batch) for batch in batches]
        )
        
        # Flatten results
        for batch_results in all_batch_results:
            results.extend(batch_results)
        
        return results


def optimize_regex_patterns(patterns: dict) -> dict:
    """
    Optimize regex patterns for better performance
    Returns compiled patterns
    """
    import re
    
    compiled = {}
    for name, pattern_info in patterns.items():
        if isinstance(pattern_info, dict) and 'regex' in pattern_info:
            compiled[name] = {
                **pattern_info,
                'compiled': re.compile(pattern_info['regex'])
            }
        else:
            # Legacy format - just compile the regex string
            compiled[name] = re.compile(pattern_info)
    
    return compiled


class MemoryCache:
    """
    Simple in-memory cache with TTL support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Any:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        # Check if expired
        if time.time() - self._timestamps[key] > self.default_ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with optional TTL"""
        # Evict oldest entry if cache is full
        if len(self._cache) >= self.max_size:
            oldest = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
            del self._cache[oldest]
            del self._timestamps[oldest]
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)


# Global cache instance
global_cache = MemoryCache()
