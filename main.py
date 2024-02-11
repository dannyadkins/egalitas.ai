import argparse
import logging
from cache import get_redis_client, use_cache
import requests
from bs4 import BeautifulSoup
# Setup argument parser to accept log level
parser = argparse.ArgumentParser(description='Configure log level for the application.')
parser.add_argument('-l', '--log_level', type=str, help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)', default='INFO')
parser.add_argument('-i', '--invalidate', action='store_true', help='Clear cache')

def run():

    # This is a monolithic run function that performs all steps of the pipeline
    # In the future, we will break this down into smaller functions that interact via a message queue

    # Fetch document from source URL 
    # - This might involve taxonomy/process discovery/function writing
    # - Or just executing the function if we already know how 

    # Extract data from document 

    # Extract metadata from document (e.g. title, author, date, topics.)

    # Perform side effects on document (e.g. create/update other entities like people, cases)
    # - This involves sequences of actions like lookups to see which entities we have already 
    # - Requires knowledge of entire schema 

    print(fetch_website_bs4('https://example.com'))

@use_cache(expiration=60*60)
def fetch_website_bs4(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        raise Exception(f"Failed to fetch website with status code: {response.status_code}")

if __name__ == "__main__":
    args = parser.parse_args()
    
    # set log level 
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level)

    # handle cache setup
    redis_client = get_redis_client()
    if args.invalidate:
        logging.debug("Invalidating cache before running")
        redis_client.flushdb()

    # kick off a run 
    run()