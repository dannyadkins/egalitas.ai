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
            with open(os.path.join(self.cache_dir, key), 'rb') as f:
                value, timestamp = pickle.load(f)
            if time.time() - timestamp < self.ttl:
                return value
            else:
                self.remove(key)
                return None
        except (KeyError, FileNotFoundError):
            return None

    def set(self, key, value):
        with open(os.path.join(self.cache_dir, key), 'wb') as f:
            pickle.dump((value, time.time()), f)
        self.cache[key] = (value, time.time())
        if len(self.cache) > self.max_size:
            oldest = next(iter(self.cache))
            self.remove(oldest)

    def remove(self, key):
        del self.cache[key]
        os.remove(os.path.join(self.cache_dir, key))
