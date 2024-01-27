import requests
import logging 
from caches import AbstractCache
from datetime import datetime, timedelta

class Fetcher:
    def __init__(self, cache: AbstractCache):
        self.cache = cache
        self.request_count = {}
    
    def _increment_request_count(self):
        current_minute = datetime.now().replace(second=0, microsecond=0)
        self.request_count[current_minute] = self.request_count.get(current_minute, 0) + 1
        # Clean up request counts that are older than 60 minutes
        oldest_time_allowed = current_minute - timedelta(minutes=60)
        keys_to_delete = [key for key in self.request_count if key < oldest_time_allowed]
        for key in keys_to_delete:
            del self.request_count[key]

    def get_num_requests(self, time_period):
        assert time_period % 60 == 0, "Time period should be in full minutes"
        current_minute = datetime.now().replace(second=0, microsecond=0)
        count = sum(count for minute, count in self.request_count.items() 
                    if current_minute - minute < timedelta(minutes=time_period))
        return count

    def get(self, url):
        self._increment_request_count()
        logging.info(f"Request #{self.get_num_requests(60)} in the last minute: {url}")
        return requests.get(url)
