import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError, field_validator


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
OUTPUT_DIR = SCRAPER_DIR / "output"

BOOKS_FILE = OUTPUT_DIR / "books.json"
ERRORS_FILE = OUTPUT_DIR / "errors.json"


# --------------------------------------------------
# Schema
# --------------------------------------------------

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: str
    fetched_at: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value.strip():
            raise ValueError("title cannot be empty")
        return value.strip()

    @field_validator(
        "product_url",
        "source_page",
    )
    @classmethod
    def validate_url(cls, value):
        if not value.startswith("https://"):
            raise ValueError(
                "URL must start with https://"
            )
        return value

    @field_validator("price_gbp")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError(
                "price cannot be negative"
            )
        return value


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def timestamp_from_file(
    path: Path,
) -> str:
    timestamp = path.stat().st_mtime

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat().replace(
        "+00:00",
        "Z",
    )


def fetch_html(
    url: str,
    cache_name: str,
) -> tuple[str, str]:

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_file = (
        CACHE_DIR / cache_name
    )

    if cache_file.exists():
        content = (
            cache_file.read_bytes()
        )

        print(
            f"CACHE HIT url={url} "
            f"response_size={len(content)} bytes"
        )

        return (
            content.decode(
                "utf-8",
                errors="replace",
            ),
            timestamp_from_file(
                cache_file
            ),
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

    fetched_at = (
        timestamp_from_file(
            cache_file
        )
    )

    # Delay only after real request
    time.sleep(
        REQUEST_DELAY
    )

    return (
        response.content.decode(
            "utf-8",
            errors="replace",
        ),
        fetched_at,
    )


# --------------------------------------------------
# Discover catalogue pages
# --------------------------------------------------

def discover_books():
    current_url = START_URL

    catalogue_pages = 0
    discovered_urls = []
    source_pages = {}

    while (
        current_url
        and catalogue_pages
        < MAX_CATALOGUE_PAGES
    ):
        catalogue_pages += 1

        html, _ = fetch_html(
            current_url,
            f"catalogue-page-{catalogue_pages}.html",
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
        dict.fromkeys(
            discovered_urls
        )
    )

    print()
    print(
        f"catalogue_pages="
        f"{catalogue_pages}"
    )
    print(
        f"discovered="
        f"{len(discovered_urls)}"
    )
    print(
        f"unique_urls="
        f"{len(unique_urls)}"
    )

    return (
        unique_urls,
        source_pages,
    )


# --------------------------------------------------
# Detail page extraction
# --------------------------------------------------

def detail_cache_name(
    product_url: str,
) -> str:

    url_hash = hashlib.sha256(
        product_url.encode(
            "utf-8"
        )
    ).hexdigest()[:16]

    return (
        f"book-{url_hash}.html"
    )


def extract_book(
    product_url: str,
    source_page: str,
) -> dict:

    html, fetched_at = (
        fetch_html(
            product_url,
            detail_cache_name(
                product_url
            ),
        )
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
            "Product area not found"
        )

    title_element = (
        product.select_one("h1")
    )

    price_element = (
        product.select_one(
            "p.price_color"
        )
    )

    availability_element = (
        product.select_one(
            "p.instock.availability"
        )
    )

    rating_element = (
        product.select_one(
            "p.star-rating"
        )
    )

    description_element = (
        soup.select_one(
            "#product_description + p"
        )
    )

    rating_text = None

    if rating_element:
        rating_classes = (
            rating_element.get(
                "class",
                [],
            )
        )

        rating_text = next(
            (
                value
                for value
                in rating_classes
                if value
                != "star-rating"
            ),
            None,
        )

    description = None

    if description_element:
        description = (
            description_element
            .get_text(
                " ",
                strip=True,
            )
        )

    return {
        "title": (
            title_element
            .get_text(strip=True)
            if title_element
            else None
        ),
        "product_url":
            product_url,
        "price_text": (
            price_element
            .get_text(strip=True)
            if price_element
            else None
        ),
        "availability_text": (
            availability_element
            .get_text(
                " ",
                strip=True,
            )
            if availability_element
            else None
        ),
        "rating_text":
            rating_text,
        "description":
            description,
        "source_page":
            source_page,
        "fetched_at":
            fetched_at,
    }


# --------------------------------------------------
# Normalize
# --------------------------------------------------

def normalize_price(
    price_text: str,
) -> float:

    if not price_text:
        raise ValueError(
            "price_text is missing"
        )

    match = re.search(
        r"\d+(?:\.\d+)?",
        price_text,
    )

    if not match:
        raise ValueError(
            f"Invalid price: "
            f"{price_text}"
        )

    return float(
        match.group()
    )


def normalize_record(
    raw_record: dict,
) -> dict:

    normalized = (
        raw_record.copy()
    )

    normalized["price_gbp"] = (
        normalize_price(
            raw_record[
                "price_text"
            ]
        )
    )

    return normalized


# --------------------------------------------------
# Validate
# --------------------------------------------------

def validate_records(
    raw_records: list,
):

    valid_records = []
    errors = []

    # Canonical product URL
    # is the identity
    unique_records = {}

    for raw_record in raw_records:
        product_url = (
            raw_record.get(
                "product_url"
            )
        )

        try:
            normalized = (
                normalize_record(
                    raw_record
                )
            )

            validated = (
                BookRecord(
                    **normalized
                )
            )

            unique_records[
                validated.product_url
            ] = (
                validated.model_dump()
            )

        except (
            ValidationError,
            ValueError,
        ) as error:

            errors.append(
                {
                    "product_url":
                        product_url,
                    "reason":
                        str(error),
                }
            )

    valid_records = list(
        unique_records.values()
    )

    return (
        valid_records,
        errors,
    )


# --------------------------------------------------
# Store JSON
# --------------------------------------------------

def save_output(
    records: list,
    errors: list,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    BOOKS_FILE.write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    ERRORS_FILE.write_text(
        json.dumps(
            errors,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    book_urls, source_pages = (
        discover_books()
    )

    raw_records = []

    print()
    print(
        "Extracting book details..."
    )

    for product_url in book_urls:

        raw_record = (
            extract_book(
                product_url,
                source_pages[
                    product_url
                ],
            )
        )

        raw_records.append(
            raw_record
        )

    valid_records, errors = (
        validate_records(
            raw_records
        )
    )

    save_output(
        valid_records,
        errors,
    )

    print()
    print(
        f"detail_pages="
        f"{len(raw_records)}"
    )

    print(
        f"valid_records="
        f"{len(valid_records)}"
    )

    print(
        f"invalid_records="
        f"{len(errors)}"
    )

    print(
        f"books_file="
        f"{BOOKS_FILE}"
    )

    print(
        f"errors_file="
        f"{ERRORS_FILE}"
    )

    if valid_records:
        print()
        print(
            "Sample validated record:"
        )

        print(
            json.dumps(
                valid_records[0],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()