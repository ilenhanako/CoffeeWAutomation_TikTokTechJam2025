"""
Caching utilities for performance optimization
"""

import streamlit as st
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json
import time
from utils.logging_config import logger
from config.settings import settings

class CacheManager:
    """Manages application caching with TTL support"""
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate a cache key from function arguments"""
        try:
            # Create a string representation of all arguments
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            
            # Create hash of the key string
            return hashlib.md5(key_string.encode()).hexdigest()
        
        except Exception as e:
            logger.warning(f"Error generating cache key: {e}")
            return f"fallback_key_{int(time.time())}"
    
    @staticmethod
    def get_cached_value(key: str) -> tuple[bool, Any]:
        """
        Get a cached value with TTL check
        
        Args:
            key: Cache key
            
        Returns:
            Tuple of (found, value)
        """
        try:
            cache_key = f"cache_{key}"
            timestamp_key = f"cache_timestamp_{key}"
            
            if cache_key in st.session_state and timestamp_key in st.session_state:
                # Check if cache is still valid
                cached_time = st.session_state[timestamp_key]
                current_time = time.time()
                
                if (current_time - cached_time) < settings.app.cache_ttl:
                    logger.debug(f"Cache hit for key: {key}")
                    return True, st.session_state[cache_key]
                else:
                    # Cache expired, remove it
                    logger.debug(f"Cache expired for key: {key}")
                    CacheManager.clear_cache_key(key)
            
            return False, None
            
        except Exception as e:
            logger.warning(f"Error getting cached value: {e}")
            return False, None
    
    @staticmethod
    def set_cached_value(key: str, value: Any) -> None:
        """Set a cached value with timestamp"""
        try:
            cache_key = f"cache_{key}"
            timestamp_key = f"cache_timestamp_{key}"
            
            st.session_state[cache_key] = value
            st.session_state[timestamp_key] = time.time()
            
            logger.debug(f"Cached value for key: {key}")
            
        except Exception as e:
            logger.warning(f"Error setting cached value: {e}")
    
    @staticmethod
    def clear_cache_key(key: str) -> None:
        """Clear a specific cache key"""
        try:
            cache_key = f"cache_{key}"
            timestamp_key = f"cache_timestamp_{key}"
            
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            if timestamp_key in st.session_state:
                del st.session_state[timestamp_key]
                
            logger.debug(f"Cleared cache for key: {key}")
            
        except Exception as e:
            logger.warning(f"Error clearing cache key: {e}")
    
    @staticmethod
    def clear_all_cache() -> None:
        """Clear all cached values"""
        try:
            keys_to_remove = [
                key for key in st.session_state.keys() 
                if key.startswith('cache_')
            ]
            
            for key in keys_to_remove:
                del st.session_state[key]
            
            logger.info(f"Cleared {len(keys_to_remove)} cache entries")
            
        except Exception as e:
            logger.warning(f"Error clearing all cache: {e}")

def cached_function(ttl: Optional[int] = None):
    """
    Decorator to cache function results with TTL
    
    Args:
        ttl: Time to live in seconds (uses app default if not specified)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}_{CacheManager.generate_cache_key(*args, **kwargs)}"
            
            # Try to get cached result
            found, result = CacheManager.get_cached_value(cache_key)
            
            if found:
                return result
            
            # Execute function and cache result
            try:
                logger.debug(f"Executing and caching: {func.__name__}")
                result = func(*args, **kwargs)
                CacheManager.set_cached_value(cache_key, result)
                return result
                
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

# Streamlit-specific caching decorators
@st.cache_data(ttl=settings.app.cache_ttl, show_spinner=False)
def cached_data_function(func: Callable) -> Callable:
    """Streamlit cache_data decorator with app settings"""
    return func

@st.cache_resource(show_spinner=False)
def cached_resource_function(func: Callable) -> Callable:
    """Streamlit cache_resource decorator"""
    return func

# Pre-configured cached functions for common operations
@cached_function(ttl=300)  # 5 minutes
def get_scenarios_with_cache():
    """Cached version of get_all_business_scenarios"""
    try:
        from services.scenario_service import ScenarioService
        return ScenarioService.get_filter_options()
    except Exception as e:
        logger.error(f"Error getting cached scenarios: {e}")
        return {"features": [], "types": [], "tags": []}

@cached_function(ttl=60)  # 1 minute
def get_database_stats_cached():
    """Cached version of database statistics"""
    try:
        from services.database_manager import DatabaseManager
        return DatabaseManager.get_database_stats()
    except Exception as e:
        logger.error(f"Error getting cached database stats: {e}")
        return {}

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    @staticmethod
    def time_function(func_name: str = None):
        """Decorator to time function execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                name = func_name or func.__name__
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    if execution_time > 1.0:  # Log slow functions
                        logger.warning(f"Slow function '{name}': {execution_time:.2f}s")
                    else:
                        logger.debug(f"Function '{name}': {execution_time:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    logger.error(f"Function '{name}' failed after {execution_time:.2f}s: {e}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def log_memory_usage():
        """Log current memory usage (if psutil is available)"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 500:  # Log high memory usage
                logger.warning(f"High memory usage: {memory_mb:.1f} MB")
            else:
                logger.debug(f"Memory usage: {memory_mb:.1f} MB")
                
        except ImportError:
            logger.debug("psutil not available for memory monitoring")
        except Exception as e:
            logger.debug(f"Error monitoring memory: {e}")

# Batch processing utilities
class BatchProcessor:
    """Utilities for efficient batch processing"""
    
    @staticmethod
    def process_in_batches(items: list, batch_size: int = 10, progress_callback=None):
        """Process items in batches with optional progress callback"""
        total_items = len(items)
        
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            
            if progress_callback:
                progress = (i + len(batch)) / total_items
                progress_callback(progress)
            
            yield batch
    
    @staticmethod
    def lazy_load_scenarios(scenarios: list, page_size: int = 20):
        """Lazy load scenarios for better performance"""
        for i in range(0, len(scenarios), page_size):
            yield scenarios[i:i + page_size]