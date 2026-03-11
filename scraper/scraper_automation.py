"""Simple automation scraper for collecting climate adaptation solutions.

This is a lightweight, opinionated scraper that fetches a small set of trusted
sources and extracts candidate solutions based on CSS heuristics. It is
meant to be run locally (the host must have network access) and to seed or
augment the curated dataset.

Usage:
    python -m scraper.scraper_automation --out data/auto_solutions.csv

Notes:
- The scraper is conservative and may not find structured data on all pages.
- Add or remove sources in the SOURCES list.
- This script has no third-party JS rendering; it uses requests + BeautifulSoup.
"""
from __future__ import annotations

import csv
import logging
import argparse
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Minimal set of trusted sources to query. These are example pages; adjust as needed.
SOURCES = [
    # These are placeholders for authoritative pages about adaptation practices.
    # Replace or expand with pages you want the scraper to consult.
    "https://www.ipcc.ch/srccl/chapter/chapter-4/",
    "https://www.fao.org/climate-change/resources/what-we-do/en/",
    "https://www.worldbank.org/en/topic/climate-adaptation",
    "https://unfccc.int/topics/adaptation-and-resilience/the-big-picture/what-do-we-mean-by-adaptation",
]

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


def fetch_html(url: str) -> str:
    try:
        import requests
        from requests.exceptions import RequestException
    except Exception:
        raise RuntimeError("requests is required to fetch remote pages. Install via pip install requests")

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except RequestException as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return ""


def extract_candidates_from_html(html: str, source_url: str) -> List[dict]:
    """Heuristic extraction: find <h2> or <h3> headings and nearby paragraphs as candidate solutions.

    Returns a list of dicts matching DEFAULT_HEADERS (some fields may be empty).
    """
    try:
        from bs4 import BeautifulSoup
    except Exception:
        raise RuntimeError("beautifulsoup4 is required for parsing HTML. Install via pip install beautifulsoup4")

    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    # Look for headings that might denote solution names
    for h in soup.find_all(["h2", "h3"], limit=40):
        name = h.get_text(strip=True)
        if not name or len(name) < 5:
            continue
        # find the next paragraph
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


def run_sources(sources: List[str]) -> List[dict]:
    rows = []
    for url in sources:
        logger.info("Fetching %s", url)
        html = fetch_html(url)
        if not html:
            continue
        candidates = extract_candidates_from_html(html, url)
        logger.info("Found %d candidates on %s", len(candidates), url)
        rows.extend(candidates)
    return rows


def write_csv(rows: List[dict], out_path: str):
    if not rows:
        logger.info("No rows to write")
        return

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(DEFAULT_HEADERS)
        for r in rows:
            writer.writerow([r.get(h, "") for h in DEFAULT_HEADERS])
    logger.info("Wrote %d rows to %s", len(rows), out_path)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/auto_solutions.csv", help="Output CSV path")
    p.add_argument("--sources", nargs="*", help="Optional list of source URLs to override defaults")
    return p.parse_args()


def main():
    args = _parse_args()
    sources = args.sources if args.sources else SOURCES
    rows = run_sources(sources)
    write_csv(rows, args.out)


if __name__ == "__main__":
    main()
