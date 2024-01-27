from abc import ABC, abstractmethod
import os
import pickle
import time
from collections import OrderedDict

class AbstractCache(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def remove(self, key):
        pass

class LocalCache(AbstractCache):
    def __init__(self, cache_dir=".cache", max_size=100, ttl=3600):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get(self, key):
        try:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                self.remove(key)
                return None
        except KeyError:
            return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, time.time())
        if len(self.cache) > self.max_size:
            oldest = next(iter(self.cache))
            self.remove(oldest)

    def remove(self, key):
        del self.cache[key]
        os.remove(os.path.join(self.cache_dir, key))
