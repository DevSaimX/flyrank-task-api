import argparse
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
RETRY_DELAY = 1.0
MAX_CATALOGUE_PAGES = 3

SCRAPER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = SCRAPER_DIR / "cache"
OUTPUT_DIR = SCRAPER_DIR / "output"

BOOKS_FILE = OUTPUT_DIR / "books.json"
ERRORS_FILE = OUTPUT_DIR / "errors.json"
REPORT_FILE = OUTPUT_DIR / "run-report.json"


RUN_STATS = {
    "pages_fetched": 0,
    "cache_hits": 0,
}


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

    @field_validator("product_url", "source_page")
    @classmethod
    def validate_url(cls, value):
        if not value.startswith("https://"):
            raise ValueError("URL must start with https://")
        return value

    @field_validator("price_gbp")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError("price cannot be negative")
        return value


def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat().replace("+00:00", "Z")


def timestamp_from_file(path: Path):
    return datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    ).isoformat().replace("+00:00", "Z")


def fetch_html(url: str, cache_name: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / cache_name

    if cache_file.exists():
        content = cache_file.read_bytes()

        RUN_STATS["cache_hits"] += 1

        print(
            f"CACHE HIT url={url} "
            f"response_size={len(content)} bytes"
        )

        return (
            content.decode("utf-8", errors="replace"),
            timestamp_from_file(cache_file),
        )

    for attempt in range(1, 3):
        try:
            print(
                f"FETCH url={url} attempt={attempt}"
            )

            response = requests.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                },
                timeout=TIMEOUT,
            )

            # Polite delay after every real request
            time.sleep(REQUEST_DELAY)

            if response.status_code == 200:
                cache_file.write_bytes(
                    response.content
                )

                RUN_STATS["pages_fetched"] += 1

                print(
                    f"status=200 "
                    f"response_size="
                    f"{len(response.content)} bytes"
                )

                return (
                    response.content.decode(
                        "utf-8",
                        errors="replace",
                    ),
                    timestamp_from_file(cache_file),
                )

            # Never retry 403 or 404
            if response.status_code in (403, 404):
                raise RuntimeError(
                    f"HTTP {response.status_code}"
                )

            # Retry server failures once
            if 500 <= response.status_code <= 599:
                if attempt == 1:
                    print(
                        f"RETRY status="
                        f"{response.status_code}"
                    )
                    time.sleep(RETRY_DELAY)
                    continue

                raise RuntimeError(
                    f"HTTP {response.status_code}"
                )

            raise RuntimeError(
                f"HTTP {response.status_code}"
            )

        except requests.Timeout:
            if attempt == 1:
                print("RETRY timeout")
                time.sleep(RETRY_DELAY)
                continue

            raise RuntimeError(
                "Request timeout"
            )

        except requests.RequestException as error:
            raise RuntimeError(
                f"Request failed: {error}"
            )

    raise RuntimeError(
        f"Unable to fetch {url}"
    )


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

        html, _ = fetch_html(
            current_url,
            f"catalogue-page-{catalogue_pages}.html",
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for link in soup.select(
            "article.product_pod h3 a"
        ):
            href = link.get("href")

            if not href:
                continue

            product_url = urljoin(
                current_url,
                href,
            )

            discovered_urls.append(product_url)

            source_pages.setdefault(
                product_url,
                current_url,
            )

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

    unique_urls = list(
        dict.fromkeys(discovered_urls)
    )

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return (
        unique_urls,
        source_pages,
        catalogue_pages,
        len(discovered_urls),
    )


def detail_cache_name(product_url: str):
    url_hash = hashlib.sha256(
        product_url.encode("utf-8")
    ).hexdigest()[:16]

    return f"book-{url_hash}.html"


def extract_book(
    product_url: str,
    source_page: str,
):
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
            "Product area not found"
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
        rating_text = next(
            (
                value
                for value in rating_element.get(
                    "class",
                    [],
                )
                if value != "star-rating"
            ),
            None,
        )

    description = None

    if description_element:
        description = (
            description_element.get_text(
                " ",
                strip=True,
            )
        )

    return {
        "title": (
            title_element.get_text(strip=True)
            if title_element
            else None
        ),
        "product_url": product_url,
        "price_text": (
            price_element.get_text(strip=True)
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


def normalize_price(price_text: str):
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
            f"Invalid price: {price_text}"
        )

    return float(match.group())


def normalize_record(raw_record: dict):
    normalized = raw_record.copy()

    normalized["price_gbp"] = (
        normalize_price(
            raw_record["price_text"]
        )
    )

    return normalized


def validate_records(raw_records: list):
    unique_records = {}
    errors = []

    for raw_record in raw_records:
        try:
            normalized = normalize_record(
                raw_record
            )

            validated = BookRecord(
                **normalized
            )

            unique_records[
                validated.product_url
            ] = validated.model_dump()

        except (
            ValidationError,
            ValueError,
        ) as error:
            errors.append(
                {
                    "product_url":
                        raw_record.get(
                            "product_url"
                        ),
                    "reason": str(error),
                }
            )

    return (
        list(unique_records.values()),
        errors,
    )


def save_output(records, errors):
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


def save_report(report):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--test-failure",
        action="store_true",
        help="Add one fake URL to prove failure handling.",
    )

    args = parser.parse_args()

    started_at = utc_now()
    start_time = time.perf_counter()

    failed_urls = []

    (
        book_urls,
        source_pages,
        catalogue_pages,
        discovered_count,
    ) = discover_books()

    # Deliberately broken URL for Stage 5 checkpoint
    if args.test_failure:
        fake_url = (
            "https://books.toscrape.com/"
            "catalogue/this-book-does-not-exist/"
            "index.html"
        )

        book_urls.append(fake_url)
        source_pages[fake_url] = START_URL

        print()
        print(
            f"TEST FAILURE URL ADDED: {fake_url}"
        )

    raw_records = []

    print()
    print("Extracting book details...")

    for product_url in book_urls:
        try:
            raw_record = extract_book(
                product_url,
                source_pages[product_url],
            )

            raw_records.append(
                raw_record
            )

        except Exception as error:
            print(
                f"SKIPPED url={product_url} "
                f"reason={error}"
            )

            failed_urls.append(
                {
                    "url": product_url,
                    "reason": str(error),
                }
            )

    valid_records, errors = validate_records(
        raw_records
    )

    save_output(
        valid_records,
        errors,
    )

    duration = round(
        time.perf_counter() - start_time,
        2,
    )

    report = {
        "started_at": started_at,
        "duration_seconds": duration,
        "catalogue_pages": catalogue_pages,
        "discovered_urls": discovered_count,
        "pages_fetched":
            RUN_STATS["pages_fetched"],
        "cache_hits":
            RUN_STATS["cache_hits"],
        "valid_records":
            len(valid_records),
        "invalid_records":
            len(errors),
        "failed_pages":
            len(failed_urls),
        "failed_urls":
            failed_urls,
    }

    save_report(report)

    print()
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(failed_urls)}")
    print(
        f"pages_fetched="
        f"{RUN_STATS['pages_fetched']}"
    )
    print(
        f"cache_hits="
        f"{RUN_STATS['cache_hits']}"
    )
    print(
        f"duration_seconds={duration}"
    )

    print()
    print(f"books_file={BOOKS_FILE}")
    print(f"errors_file={ERRORS_FILE}")
    print(f"report_file={REPORT_FILE}")


if __name__ == "__main__":
    main()