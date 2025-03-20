import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def is_valid_url(url):
    """Simple check to ensure the URL has a valid scheme and network location."""
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def get_page_text_and_links(url):
    """
    Given a URL, fetch its content and return the page's text and
    a list of valid, absolute URLs found on the page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, []

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the visible text from the page
    text = soup.get_text(separator=" ", strip=True)

    # Extract all anchor tags with href attributes
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")
        # Build absolute URL
        full_url = urljoin(url, href)
        # Only consider valid HTTP URLs
        if is_valid_url(full_url):
            links.add(full_url)

    return text, list(links)


def crawl_website(start_url, max_depth=2, delay=1):
    """
    Crawl the website starting at `start_url` up to `max_depth`.
    Returns a dictionary mapping URLs to their extracted text content.
    `delay` adds a pause (in seconds) between requests to be polite.
    """
    visited = set()
    url_text_mapping = {}

    # Use a deque to perform BFS; each item is a tuple (url, current_depth)
    queue = deque([(start_url, 0)])

    # Get the domain of the start_url to restrict crawling within the site
    domain = urlparse(start_url).netloc

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        print(f"Crawling: {current_url} (depth {depth})")
        text, links = get_page_text_and_links(current_url)
        if text is not None:
            url_text_mapping[current_url] = text
        print(set(links))
        # If we haven't reached max depth, add new links to the queue
        if depth < max_depth:
            for link in links:
                # Restrict crawling to the same domain
                if urlparse(link).netloc == domain and link not in visited:
                    queue.append((link, depth + 1))

        # Respectful crawling: wait a bit between requests
        time.sleep(delay)

    return url_text_mapping


# if __name__ == "__main__":
#     # Example usage
#     start_url = "https://www.ldsinfotech.com/it-service-detail/education-and-government"  # Replace with your target URL
#     max_depth = 0  # Adjust depth as needed
#     crawled_data = crawl_website(start_url, max_depth)

#     # Print the URLs and a snippet of their content
#     for url, text in crawled_data.items():
#         print(f"\nURL: {url}\nContent snippet: {text}...\n")
