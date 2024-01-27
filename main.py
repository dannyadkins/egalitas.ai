import argparse
import os
import pickle
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests

import pdfplumber
from io import BytesIO
import nltk
from nltk.tokenize import sent_tokenize

class Cache(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

class LocalCache(Cache):
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get(self, key):
        try:
            with open(os.path.join(self.cache_dir, key), 'rb') as cache_file:
                return pickle.load(cache_file)
        except FileNotFoundError:
            return None

    def set(self, key, value):
        with open(os.path.join(self.cache_dir, key), 'wb') as cache_file:
            pickle.dump(value, cache_file)

def download_pdf(url, use_cache=False):
    cache_key = f"{url.replace('/', '_')}.pdf"
    if use_cache:
        cached_content = cache.get(cache_key)
        if cached_content:
            return BytesIO(cached_content)
    response = requests.get(url)
    response.raise_for_status()
    content = response.content
    if use_cache:
        cache.set(cache_key, content)
    return BytesIO(content)

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
    cache_key = f"{url.replace('/', '_')}.html"
    if use_cache:
        cached_content = cache.get(cache_key)
        if cached_content:
            page_content = BeautifulSoup(cached_content, 'html.parser')
            print(strip_extraneous_content(page_content))
            return
    response = requests.get(url)
    if response.status_code == 200:
        page_content = BeautifulSoup(response.text, 'html.parser')
        stripped_content = strip_extraneous_content(page_content)
        if use_cache:
            cache.set(cache_key, response.text)
        print(stripped_content)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def pull_testimony_page(url, use_cache=False):
    stream = download_pdf(url, use_cache)
    text = extract_text_from_pdf(stream)
    print(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a senate subcommittee testimony page.')
    parser.add_argument('-hu', '--hearing_url', type=str, help='The URL of the senate subcommittee hearing page to scrape', default=None)
    parser.add_argument('-tu', '--testimony_url', type=str, help='The URL of the senate subcommittee testimony page to scrape', default=None)
    parser.add_argument('-c', '--use_cache', action='store_true', help='Use cached responses if available')
    args = parser.parse_args()
    
    cache = LocalCache()

    if args.hearing_url:
        pull_hearing_page(args.hearing_url, args.use_cache)
    if args.testimony_url:
        pull_testimony_page(args.testimony_url, args.use_cache)
