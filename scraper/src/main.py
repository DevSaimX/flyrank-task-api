from pathlib import Path

import requests


PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

USER_AGENT = (
    "FlyRankInternship-BE05/1.0 "
    "(+https://github.com/DevSaimX/flyrank-task-api)"
)

TIMEOUT = 10

SCRAPER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = SCRAPER_DIR / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"


def fetch_page():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Use cached HTML if it already exists
    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()

        print("CACHE HIT")
        print(f"url={PAGE_URL}")
        print(f"response_size={len(content)} bytes")
        return content.decode("utf-8")

    print("FETCH")
    print(f"url={PAGE_URL}")

    response = requests.get(
        PAGE_URL,
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=TIMEOUT,
    )

    # Only HTTP 200 is accepted as usable HTML
    if response.status_code != 200:
        raise RuntimeError(
            f"Fetch failed with status {response.status_code}"
        )

    CACHE_FILE.write_bytes(response.content)

    print(f"status={response.status_code}")
    print(f"response_size={len(response.content)} bytes")
    print(f"saved={CACHE_FILE}")

    return response.text


def main():
    fetch_page()


if __name__ == "__main__":
    main()