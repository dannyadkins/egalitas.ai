from abc import ABC, abstractmethod
import os
import pickle
import time
from collections import OrderedDict
from typing import Any, List, Tuple, Optional, Dict

class AbstractCache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def remove(self, key: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Tuple[str, Tuple[Any, float]]]:
        pass

    @abstractmethod
    def keys(self) -> List[str]:
        pass

class LocalCache(AbstractCache):
    def __init__(self, cache_dir: str = ".cache", max_size: int = 100, ttl: int = 3600) -> None:
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = OrderedDict()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        try:
            with open(os.path.join(self.cache_dir, key), 'rb') as f:
                value, timestamp = pickle.load(f)
            if time.time() - timestamp < self.ttl:
                return value, timestamp
            else:
                self.remove(key)
                return None
        except (KeyError, FileNotFoundError):
            return None

    def set(self, key: str, value: Any) -> None:
        timestamp = time.time()
        with open(os.path.join(self.cache_dir, key), 'wb') as f:
            pickle.dump((value, timestamp), f)
        self.cache[key] = (value, timestamp)
        if len(self.cache) > self.max_size:
            oldest = next(iter(self.cache))
            self.remove(oldest)

    def remove(self, key: str) -> None:
        try:
            del self.cache[key]
            os.remove(os.path.join(self.cache_dir, key))
        except KeyError:
            pass

    def get_all(self) -> List[Tuple[str, Tuple[Any, float]]]:
        return list(self.cache.items())

    def keys(self) -> List[str]:
        return list(self.cache.keys())
