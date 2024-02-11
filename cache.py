import functools
import hashlib
import pickle
import logging

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import os
import pickle
import time
import redis

def get_redis_client():
    return redis.Redis(host='localhost', port=6379, db=0)

def test_local_redis():
    redis_client = get_redis_client()
    redis_client.set('foo', 'bar')
    print(redis_client.get('foo'))  # Outputs: b'bar'

def use_cache(expiration=60*60):

    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on the function's name and arguments
            key = f"{func.__name__}:{hashlib.sha256(pickle.dumps((args, kwargs))).hexdigest()}"
            pretty_name = f"{func.__name__}({args}, {kwargs})"
            # Try to get the cached result
            cached_result = redis_client.get(key)
            if cached_result:
                logging.debug(f"Cache hit for key: {pretty_name}")
                # If found in cache, return the cached result
                return pickle.loads(cached_result)
            else:
                logging.debug(f"Cache miss for key: {pretty_name}")
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            redis_client.setex(key, expiration, pickle.dumps(result))
            logging.debug(f"Result cached for key: {pretty_name}")
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    test_local_redis()