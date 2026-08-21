import hashlib
import json
import time
from datetime import datetime, timezone
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


def timestamp_from_file(path: Path) -> str:
    timestamp = path.stat().st_mtime

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat().replace("+00:00", "Z")


def fetch_html(
    url: str,
    cache_name: str,
) -> tuple[str, str]:

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_file = CACHE_DIR / cache_name

    if cache_file.exists():
        content = cache_file.read_bytes()

        print(
            f"CACHE HIT url={url} "
            f"response_size={len(content)} bytes"
        )

        fetched_at = timestamp_from_file(
            cache_file
        )

        return (
            content.decode(
                "utf-8",
                errors="replace",
            ),
            fetched_at,
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

    fetched_at = timestamp_from_file(
        cache_file
    )

    print(
        f"status={response.status_code} "
        f"response_size={len(response.content)} bytes"
    )

    # Delay only after a real request
    time.sleep(REQUEST_DELAY)

    return response.text, fetched_at


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

        html, _ = fetch_html(
            current_url,
            cache_name,
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

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

            source_pages.setdefault(
                product_url,
                current_url,
            )

        next_link = soup.select_one(
            "li.next a"
        )

        if (
            next_link
            and catalogue_pages
            < MAX_CATALOGUE_PAGES
        ):
            current_url = urljoin(
                current_url,
                next_link.get("href"),
            )
        else:
            current_url = None

    unique_urls = list(
        dict.fromkeys(discovered_urls)
    )

    print()
    print(
        f"catalogue_pages={catalogue_pages}"
    )
    print(
        f"discovered={len(discovered_urls)}"
    )
    print(
        f"unique_urls={len(unique_urls)}"
    )

    return unique_urls, source_pages


def detail_cache_name(
    product_url: str,
) -> str:

    url_hash = hashlib.sha256(
        product_url.encode("utf-8")
    ).hexdigest()[:16]

    return f"book-{url_hash}.html"


def extract_book(
    product_url: str,
    source_page: str,
) -> dict:

    html, fetched_at = fetch_html(
        product_url,
        detail_cache_name(product_url),
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    product = soup.select_one(
        "div.product_main"
    )

    if product is None:
        raise ValueError(
            f"Product area not found: {product_url}"
        )

    title_element = product.select_one("h1")
    price_element = product.select_one(
        "p.price_color"
    )
    availability_element = product.select_one(
        "p.instock.availability"
    )
    rating_element = product.select_one(
        "p.star-rating"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    rating_text = None

    if rating_element:
        rating_classes = rating_element.get(
            "class",
            [],
        )

        rating_text = next(
            (
                value
                for value in rating_classes
                if value != "star-rating"
            ),
            None,
        )

    description = None

    if description_element:
        description = (
            description_element
            .get_text(" ", strip=True)
        )

    return {
        "title": (
            title_element.get_text(
                strip=True
            )
            if title_element
            else None
        ),
        "product_url": product_url,
        "price_text": (
            price_element.get_text(
                strip=True
            )
            if price_element
            else None
        ),
        "availability_text": (
            availability_element.get_text(
                " ",
                strip=True,
            )
            if availability_element
            else None
        ),
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def main():
    book_urls, source_pages = (
        discover_books()
    )

    raw_records = []

    print()
    print("Extracting book details...")

    for product_url in book_urls:
        record = extract_book(
            product_url,
            source_pages[product_url],
        )

        raw_records.append(record)

    print()
    print(
        f"detail_pages={len(raw_records)}"
    )

    if raw_records:
        print()
        print("Sample raw record:")

        print(
            json.dumps(
                raw_records[0],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()