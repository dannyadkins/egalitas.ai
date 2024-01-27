import argparse
import os
import pickle
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import logging
import logging.config

import pdfplumber
from io import BytesIO

from caches import AbstractCache, LocalCache

from langchain_community.document_loaders import PyPDFLoader
from fetch import Fetcher

def extract_text_from_pdf(file_stream):
    text = ""
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def strip_extraneous_content(page_content):
    for script in page_content(["script", "style"]):
        script.extract()  # Remove script and style elements
    for tag in page_content.find_all(True):
        if tag.name == 'a':
            # Preserve only href attribute for anchor tags
            tag.attrs = {key: value for key, value in tag.attrs.items() if key == 'href'}
        else:
            # Remove all attributes for non-anchor tags
            tag.attrs = {}
        if tag.string:  # Check if the tag has a string attribute
            # Replace multiple spaces with a single space
            tag.string.replace_with(' '.join(tag.get_text().split()))

    return page_content


def pull_hearing_page(url, use_cache=False):
    response = fetcher.get(url, use_cache)
    if response.status_code == 200:
        page_content = BeautifulSoup(response.text, 'html.parser')
        stripped_content = strip_extraneous_content(page_content)
        logging.info(stripped_content)
    else:
        logging.error(f"Failed to retrieve the page. Status code: {response.status_code}")

def pull_testimony_page(url, use_cache=False):
    response = fetcher.get(url, use_cache)
    stream = BytesIO(response.content)
    text = extract_text_from_pdf(stream)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a senate subcommittee testimony page.')
    parser.add_argument('-hu', '--hearing_url', type=str, help='The URL of the senate subcommittee hearing page to scrape', default=None)
    parser.add_argument('-tu', '--testimony_url', type=str, help='The URL of the senate subcommittee testimony page to scrape', default=None)
    parser.add_argument('-c', '--use_cache', action='store_true', help='Use cached responses if available')
    parser.add_argument('-l', '--log_level', type=str, help='Set the logging level', default='INFO')
    parser.add_argument('-r', '--reset_cache', action='store_true', help='Reset the cache')
    args = parser.parse_args()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': args.log_level,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': args.log_level,
        },
    })

    if args.reset_cache:
        if os.path.exists("request_cache"):
            os.system("rm -rf request_cache")
        if os.path.exists("url_cache"):
            os.system("rm -rf url_cache")
    
    url_cache = LocalCache(cache_dir="url_cache", max_size=10000, ttl=3600)
    request_cache = LocalCache(cache_dir="request_cache", max_size=60, ttl=60)
    fetcher = Fetcher(request_cache, url_cache=url_cache)

    if args.hearing_url:
        pull_hearing_page(args.hearing_url, args.use_cache)
    if args.testimony_url:
        pull_testimony_page(args.testimony_url, args.use_cache)
