import requests
import logging 
from caches import AbstractCache
from datetime import datetime, timedelta
import pickle

class Fetcher:
    def __init__(self, request_count_cache: AbstractCache, url_cache: AbstractCache = None):
        self.request_count_cache = request_count_cache
        self.url_cache = url_cache
    
    def _increment_request_count(self):
        current_minute = datetime.now().replace(second=0, microsecond=0)
        current_count = self.request_count_cache.get(str(current_minute))[0] or 0
        new_count = current_count + 1
        self.request_count_cache.set(str(current_minute), new_count)
        # Clean up request counts that are older than 60 minutes
        oldest_time_allowed = current_minute - timedelta(minutes=60)
        for key, _ in self.request_count_cache.get_all():
            minute = datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
            if minute < oldest_time_allowed:
                self.request_count_cache.remove(key)

    def get_num_requests(self, time_period):
        assert time_period % 60 == 0, "Time period should be in full minutes"
        current_minute = datetime.now().replace(second=0, microsecond=0)
        count = 0
        for key, (value, time) in self.request_count_cache.get_all():
            minute = datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
            if current_minute - minute < timedelta(minutes=time_period):
                count += value
        return count

    def get(self, url, use_url_cache=False):
        cache_key = self.url_to_cache_key(url)
        if use_url_cache and self.url_cache:
            cached_response, timestamp = self.url_cache.get(cache_key)
            if cached_response:
                return pickle.loads(cached_response)
        self._increment_request_count()
        logging.info(f"Request #{self.get_num_requests(60)} in the last minute: {url}")
        response = requests.get(url)
        if use_url_cache and self.url_cache:
            self.url_cache.set(cache_key, pickle.dumps(response))
        return response
        
    @staticmethod
    def url_to_cache_key(url):
        return f"{url.replace('http://', '').replace('https://', '').replace('/', '_')}.pdf"
