from __future__ import annotations

import os
import csv
import argparse
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Local imports deferred to runtime

DEFAULT_AUTO_CSV = "data/auto_solutions.csv"
DEFAULT_CURATED = "data/curated_solutions.csv"
DEFAULT_COMBINED = "data/solutions_combined.csv"


class Command(BaseCommand):
    help = "Fetch solutions using the scraper automation and/or curated file, normalize and optionally import or upload to Google Sheets."

    def add_arguments(self, parser):
        parser.add_argument("--out", default=DEFAULT_COMBINED, help="Path to write combined normalized CSV")
        parser.add_argument("--run-scraper", action="store_true", help="Run local scraper to fetch candidates from web sources")
        parser.add_argument("--import-to-db", action="store_true", help="After building combined CSV, import rows into the Django DB")
        parser.add_argument("--upload-to-sheet", action="store_true", help="Upload the combined CSV to the Google Sheet specified by --sheet-id")
        parser.add_argument("--sheet-id", help="Spreadsheet ID when using --upload-to-sheet")
        parser.add_argument("--sheet-name", help="Optional target sheet/tab name when uploading")

    def handle(self, *args, **options):
        out_path = options["out"]
        run_scraper = options["run_scraper"]
        import_to_db = options["import_to_db"]
        upload_to_sheet = options["upload_to_sheet"]
        sheet_id = options.get("sheet_id")
        sheet_name = options.get("sheet_name")

        # Step 1: optionally run scraper to produce auto CSV
        auto_csv = DEFAULT_AUTO_CSV
        if run_scraper:
            logger.info("Running scraper to generate %s", auto_csv)
            # Prefer Selenium-backed scraper when available
            try:
                try:
                    from scraper import selenium_scraper as selenium_scraper_module

                    selenium_scraper_module.main()
                except Exception:
                    # fallback to simple scraper
                    from scraper import scraper_automation

                    scraper_automation.main()
            except Exception as e:
                logger.error("Failed to run scraper: %s", e)
                # continue; we may still have curated data

        # Step 2: read curated CSV (if exists) and auto CSV and merge
        rows = []
        headers = None
        for p in [DEFAULT_CURATED, auto_csv]:
            if not os.path.exists(p):
                logger.info("File not found, skipping: %s", p)
                continue
            with open(p, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                h = next(reader, None)
                if h is None:
                    continue
                if headers is None:
                    headers = h
                # assume same header ordering
                for r in reader:
                    if not any(r):
                        continue
                    rows.append(r)

        if headers is None:
            logger.error("No input CSVs found. Place a curated file at %s or run with --run-scraper", DEFAULT_CURATED)
            return

        # write combined CSV
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in rows:
                w.writerow(r)
        logger.info("Wrote combined CSV with %d rows to %s", len(rows), out_path)

        # Step 3: optionally import to DB
        if import_to_db:
            logger.info("Importing combined CSV into DB")
            try:
                # reuse google_sheets import logic which expects a sheet; instead read CSV and import rows
                import django

                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "climate_solutions.settings")
                django.setup()
                from solutions.models import Location, Category, CostLevel, Timeframe, SolutionType, ClimateSolution

                # normalize header names (lower_snake) similar to google_sheets.normalize_header
                norm_headers = [h.strip().lower().replace(" ", "_") for h in headers]
                with open(out_path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    created = 0
                    for r in reader:
                        data = {h: (r[i] if i < len(r) else "") for i, h in enumerate(norm_headers)}
                        country = data.get("geographic_applicability") or data.get("country") or "Unknown"
                        loc, _ = Location.objects.get_or_create(country=country, region="")
                        cat, _ = Category.objects.get_or_create(name=data.get("category", "Other"))
                        cost, _ = CostLevel.objects.get_or_create(level=str(data.get("cost_estimate", "Unknown")))
                        tf, _ = Timeframe.objects.get_or_create(period=data.get("implementation_complexity", "Unknown"))
                        st, _ = SolutionType.objects.get_or_create(name=data.get("category", "Other"))

                        sol, created_flag = ClimateSolution.objects.get_or_create(
                            name=data.get("name"),
                            defaults={
                                "location": loc,
                                "category": cat,
                                "description": data.get("description", ""),
                                "benefits": data.get("co_benefits", ""),
                                "cost": cost,
                                "timeframe": tf,
                                "solution_type": st,
                                "source_url": data.get("source_url", ""),
                                "tags": [t.strip() for t in data.get("tags", "").split(",") if t.strip()] if data.get("tags") else [],
                            },
                        )
                        if created_flag:
                            created += 1
                logger.info("Imported %d new solutions into DB", created)
            except Exception as e:
                logger.error("Failed to import CSV to DB: %s", e)

        # Step 4: optionally upload to Google Sheet
        if upload_to_sheet:
            if not sheet_id:
                logger.error("--sheet-id is required when using --upload-to-sheet")
                return
            try:
                from solutions.services.google_sheets import update_sheet_from_csv

                update_sheet_from_csv(sheet_id, out_path, sheet_name)
                logger.info("Uploaded combined CSV to sheet %s (tab=%s)", sheet_id, sheet_name)
            except Exception as e:
                logger.error("Failed to upload to Google Sheet: %s", e)
