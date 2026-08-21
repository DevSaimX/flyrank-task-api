Now finish **Stage 6 — Publish the evidence**. This is the final required stage. The PDF requires a runnable README, one sample output, `cache/` ignored, a real `run-report.json` shown in the README, politeness rules, one limitation, and a public GitHub repo with 7+ meaningful commits. 

### 1. Make sure cache is ignored

Your `scraper\.gitignore` should contain:

```gitignore
__pycache__/
*.pyc
.venv/
cache/
```

Check:

```powershell
git check-ignore scraper\cache\catalogue-page-1.html
```

It should print the cache path.

---

## 2. Replace `scraper\README.md`

Use this short final README:

````md
# BE-05 — The Polite Scraper

Backend AI Engineering — Week 5

A polite Python scraper that collects the first 3 catalogue pages from Books to Scrape and converts 60 books into validated JSON.

## ✅ Assignment Status — COMPLETED

- 3 catalogue pages processed
- 60 unique books discovered
- 60 detail pages processed
- Prices normalized to numbers
- Records validated with Pydantic
- HTML cached locally
- Broken pages skipped safely
- Run report generated
- No duplicate records on rerun

---

## Target Classification

**Target:** https://books.toscrape.com/

Books to Scrape is a public sandbox designed for practising web scraping.

**Scope:** First 3 catalogue pages only.

**Data collected:**

- title
- product URL
- price
- availability
- rating
- description
- source page
- fetch time

**robots.txt:** no robots file found.

I will not reuse this code on another site without checking its rules and terms first.

---

## Python Lane

Uses:

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic

Install:

```powershell
python -m pip install -r scraper\requirements.txt
````

---

## Run

From the repository root:

```powershell
python scraper\src\main.py
```

Failure-handling test:

```powershell
python scraper\src\main.py --test-failure
```

---

## Output

The scraper produces:

```text
scraper/output/books.json
scraper/output/errors.json
scraper/output/run-report.json
```

A successful run contains exactly **60 unique validated books**.

---

## Record Schema

Each stored book contains:

```json
{
  "title": "string",
  "product_url": "https://...",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "string or null",
  "source_page": "https://...",
  "fetched_at": "ISO timestamp"
}
```

---

## Politeness Rules

Every real request:

* sends an identifying User-Agent
* uses a timeout
* checks the HTTP status
* waits at least 500 ms
* uses cached HTML during development

`404` and `403` responses are not retried.

Timeouts and `5xx` failures may be retried once.

---

## Failure Handling

One deliberately fake book URL was added during testing.

The scraper skipped it instead of crashing.

The 60 valid books remained in `books.json`, while the failure was recorded in `run-report.json`.

---

## Run Report

The actual report from the latest test run is included in:

```text
scraper/output/run-report.json
```

---

## Why No Browser?

This assignment does not need a browser because the required book data is already present in the HTML returned by the server. Using a browser would only add unnecessary time and resource cost.

---

## Limitation

The scraper depends on the current HTML structure and CSS selectors of Books to Scrape. If the site's markup changes, the selectors may need updating.

---

## Ethics

Use an official API when one exists. Never bypass authentication, paywalls, access controls, or site blocks. Collect only the data needed and always check a site's rules before scraping it.

---

## Assignment Commits

* Stage 0: classify scraping target
* Stage 1: fetch and cache HTML
* Stage 2: discover three catalogue pages
* Stage 3: extract book details
* Stage 4: validate normalized records
* Stage 5: survive failures, report the run
* Stage 6: publish scraper evidence

---

## Author

Saim Iftikhar

