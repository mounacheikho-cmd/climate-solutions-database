"""Selenium-backed scraper that extracts candidate climate adaptation solutions.

Features:
- Uses Selenium WebDriver (Chrome) when available; falls back to requests.
- Parses pages with BeautifulSoup.
- Rate-limited network calls using `ratelimit`.
- Saves normalized CSV using pandas.

Usage:
    pip install -r requirements.txt  # includes selenium, webdriver-manager, pandas, ratelimit
    python -m scraper.selenium_scraper --out data/auto_solutions.csv

Notes:
- webdriver-manager will download a ChromeDriver automatically. Chrome must be installed.
- For headless runs in CI, ensure Chrome is available in the environment (or set USE_REQUESTS=1 to force requests fallback).
"""
from __future__ import annotations

import argparse
import logging
import csv
import time
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DEFAULT_HEADERS = [
    "name",
    "category",
    "geographic_applicability",
    "description",
    "co_benefits",
    "cost_estimate",
    "implementation_complexity",
    "source_url",
    "tags",
]

# default sources (these are conservative trusted sources; add more URLs as needed)
SOURCES = [
    "https://www.ipcc.ch/srccl/chapter/chapter-4/",
    "https://www.fao.org/climate-change/resources/what-we-do/en/",
    "https://www.worldbank.org/en/topic/climate-adaptation",
    "https://unfccc.int/topics/adaptation-and-resilience/the-big-picture/what-do-we-mean-by-adaptation",
]


def _use_selenium() -> bool:
    # allow user to force requests fallback by setting env var
    import os

    if os.getenv("USE_REQUESTS", ""):
        return False
    try:
        import selenium  # noqa: F401
        return True
    except Exception:
        return False


def init_selenium_driver(headless: bool = True):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception as e:
        logger.warning("Selenium or webdriver-manager not available: %s", e)
        return None

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    # create driver
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        return driver
    except Exception as e:
        logger.warning("Failed to start Chrome WebDriver: %s", e)
        return None


# rate-limited fetch (1 call every 2 seconds)
try:
    from ratelimit import limits, sleep_and_retry

    @sleep_and_retry
    @limits(calls=1, period=2)
    def fetch_url_requests(url: str, session=None) -> str:
        import requests

        s = session or requests
        r = s.get(url, timeout=15)
        r.raise_for_status()
        return r.text
except Exception:
    def fetch_url_requests(url: str, session=None) -> str:
        import requests

        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text


def fetch_with_selenium(driver, url: str) -> str:
    # selenium calls are not decorated with ratelimit but we add a sleep
    try:
        driver.get(url)
        time.sleep(1.0)  # small wait for JS to render
        return driver.page_source
    except Exception as e:
        logger.warning("Selenium failed to fetch %s: %s", url, e)
        return ""


def extract_candidates(html: str, source_url: str) -> List[dict]:
    try:
        from bs4 import BeautifulSoup
    except Exception:
        raise RuntimeError("beautifulsoup4 is required")

    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for h in soup.find_all(["h2", "h3"], limit=40):
        name = h.get_text(strip=True)
        if not name or len(name) < 5:
            continue
        p = h.find_next_sibling("p")
        desc = p.get_text(strip=True) if p else ""
        candidates.append(
            {
                "name": name,
                "category": "Adaptation",
                "geographic_applicability": "Global",
                "description": desc,
                "co_benefits": "",
                "cost_estimate": "",
                "implementation_complexity": "Medium",
                "source_url": source_url,
                "tags": "",
            }
        )
    return candidates


def run(urls: List[str], out_path: str = "data/auto_solutions.csv") -> int:
    rows = []
    driver = None
    use_selenium = _use_selenium()
    if use_selenium:
        driver = init_selenium_driver(headless=True)
        if driver is None:
            logger.info("Selenium requested but not available; falling back to requests")
            use_selenium = False

    session = None
    for url in urls:
        logger.info("Fetching %s (selenium=%s)", url, use_selenium)
        try:
            if use_selenium and driver:
                html = fetch_with_selenium(driver, url)
            else:
                html = fetch_url_requests(url)
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", url, e)
            continue
        candidates = extract_candidates(html, url)
        logger.info("Found %d candidates on %s", len(candidates), url)
        rows.extend(candidates)

    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    # save to CSV using pandas if available
    try:
        import pandas as pd

        df = pd.DataFrame(rows)
        if df.empty:
            logger.info("No rows to write")
            return 0
        # ensure column ordering
        df = df.reindex(columns=DEFAULT_HEADERS)
        df.to_csv(out_path, index=False)
        logger.info("Wrote %d rows to %s (pandas)", len(df), out_path)
        return len(df)
    except Exception:
        # fallback to csv.writer
        import os
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(DEFAULT_HEADERS)
            for r in rows:
                w.writerow([r.get(h, "") for h in DEFAULT_HEADERS])
        logger.info("Wrote %d rows to %s", len(rows), out_path)
        return len(rows)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/auto_solutions.csv")
    p.add_argument("--sources", nargs="*", help="override default sources")
    return p.parse_args()


def main():
    args = _parse_args()
    urls = args.sources if args.sources else SOURCES
    run(urls, args.out)


if __name__ == "__main__":
    main()
