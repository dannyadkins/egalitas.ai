import argparse
from bs4 import BeautifulSoup
import requests

import pdfplumber
from io import BytesIO

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

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

def pull_hearing_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = BeautifulSoup(response.text, 'html.parser')
        stripped_content = strip_extraneous_content(page_content)
        print(stripped_content)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def pull_testimony_page(url):
    stream = download_pdf(url)
    text = extract_text_from_pdf(stream)
    print(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a senate subcommittee testimony page.')
    parser.add_argument('-hu', '--hearing_url', type=str, help='The URL of the senate subcommittee hearing page to scrape', default=None)
    parser.add_argument('-tu', '--testimony_url', type=str, help='The URL of the senate subcommittee testimony page to scrape', default=None)
    args = parser.parse_args()
    
    if args.hearing_url:
        pull_hearing_page(args.hearing_url)
    if args.testimony_url:
        pull_testimony_page(args.testimony_url)
