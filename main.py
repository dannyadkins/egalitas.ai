import argparse
import os
import pickle
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import logging

import pdfplumber
from io import BytesIO
import nltk
from nltk.tokenize import sent_tokenize

from caches import AbstractCache, LocalCache

from langchain_community.document_loaders import PyPDFLoader
from fetch import Fetcher

def url_to_cache_key(url):
    return f"{url.replace('http://', '').replace('https://', '').replace('/', '_')}.pdf"

def download_pdf(url, use_cache=False):
    cache_key = url_to_cache_key(url)
    if use_cache:
        cached_content = cache.get(cache_key)
        if cached_content:
            return BytesIO(cached_content)
    response = fetcher.get(url)
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
    response = fetcher.get(url)
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
    print("Text: ", text)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a senate subcommittee testimony page.')
    parser.add_argument('-hu', '--hearing_url', type=str, help='The URL of the senate subcommittee hearing page to scrape', default=None)
    parser.add_argument('-tu', '--testimony_url', type=str, help='The URL of the senate subcommittee testimony page to scrape', default=None)
    parser.add_argument('-c', '--use_cache', action='store_true', help='Use cached responses if available')
    args = parser.parse_args()

    print("args.use_cache: ", args.use_cache)
    
    cache = LocalCache()
    fetcher = Fetcher(cache)

    if args.hearing_url:
        pull_hearing_page(args.hearing_url, args.use_cache)
    if args.testimony_url:
        pull_testimony_page(args.testimony_url, args.use_cache)
