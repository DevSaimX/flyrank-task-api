import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


START_URL = "https://books.toscrape.com/catalogue/page-1.html"

USER_AGENT = (
    "FlyRankInternship-BE05/1.0 "
    "(+https://github.com/DevSaimX/flyrank-task-api)"
)

TIMEOUT = 10
REQUEST_DELAY = 0.5
MAX_CATALOGUE_PAGES = 3

SCRAPER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = SCRAPER_DIR / "cache"


def fetch_html(url: str, cache_name: str) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / cache_name

    if cache_file.exists():
        content = cache_file.read_bytes()

        print(
            f"CACHE HIT url={url} "
            f"response_size={len(content)} bytes"
        )

        return content.decode(
            "utf-8",
            errors="replace",
        )

    print(f"FETCH url={url}")

    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Fetch failed: "
            f"url={url} "
            f"status={response.status_code}"
        )

    cache_file.write_bytes(
        response.content
    )

    print(
        f"status={response.status_code} "
        f"response_size={len(response.content)} bytes"
    )

    # Be polite after a real network request
    time.sleep(REQUEST_DELAY)

    return response.text


def discover_books():
    current_url = START_URL

    catalogue_pages = 0
    discovered_urls = []
    source_pages = {}

    while (
        current_url
        and catalogue_pages < MAX_CATALOGUE_PAGES
    ):
        catalogue_pages += 1

        cache_name = (
            f"catalogue-page-{catalogue_pages}.html"
        )

        html = fetch_html(
            current_url,
            cache_name,
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        # Find every book on this catalogue page
        book_links = soup.select(
            "article.product_pod h3 a"
        )

        for link in book_links:
            href = link.get("href")

            if not href:
                continue

            product_url = urljoin(
                current_url,
                href,
            )

            discovered_urls.append(
                product_url
            )

            # Keep provenance for Stage 3
            source_pages.setdefault(
                product_url,
                current_url,
            )

        # Follow the site's own next link
        next_link = soup.select_one(
            "li.next a"
        )

        if (
            next_link
            and catalogue_pages < MAX_CATALOGUE_PAGES
        ):
            current_url = urljoin(
                current_url,
                next_link.get("href"),
            )
        else:
            current_url = None

    # Remove duplicates while keeping order
    unique_urls = list(
        dict.fromkeys(discovered_urls)
    )

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls, source_pages


def main():
    discover_books()


if __name__ == "__main__":
    main()