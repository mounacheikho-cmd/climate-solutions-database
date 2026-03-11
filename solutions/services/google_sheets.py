"""Google Sheets helper for fetching/exporting/importing the solutions sheet.

This module supports two main workflows:

- export_sheet_to_csv(spreadsheet_id, sheet_name=None, output_path)
  -> writes a CSV file from the first sheet (or named sheet) of the spreadsheet.

- import_sheet_to_db(spreadsheet_id, sheet_name=None)
  -> fetches the sheet and imports rows into the Django models (Location, Category, etc.).

Authentication:
- Prefer a service account JSON key file pointed to by the environment
  variable `GOOGLE_SERVICE_ACCOUNT_FILE`.
- If that is not present, the code will attempt Application Default Credentials.

Security: do NOT commit service account keys. Keep credentials out of the repo.

Usage (example):

  # export CSV
  python -m solutions.services.google_sheets --sheet-id <SHEET_ID> --export --out data/solutions_from_sheets.csv

  # import into Django DB
  export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/key.json
  python -m solutions.services.google_sheets --sheet-id <SHEET_ID> --import

"""
from __future__ import annotations

import os
import csv
import logging
import argparse
from typing import List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_sheets_service():
    """Build and return an authorized Google Sheets API service object.

    Looks for `GOOGLE_SERVICE_ACCOUNT_FILE` env var. If present, uses
    service-account credentials. Otherwise tries ADC (Application Default
    Credentials).
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception as e:
        logger.error("Google client libraries are required: pip install google-api-python-client google-auth")
        raise

    # Need read/write when updating the sheet from CSV
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",  # read/write
    ]

    sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    creds = None
    if sa_path and os.path.exists(sa_path):
        creds = service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
        logger.info("Using service account credentials from %s", sa_path)
    else:
        # fallback to default credentials
        try:
            import google.auth

            creds, _ = google.auth.default(scopes=scopes)
            logger.info("Using application default credentials")
        except Exception:
            logger.error("No credentials found. Set GOOGLE_SERVICE_ACCOUNT_FILE or configure ADC.")
            raise

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return service


def fetch_sheet_values(spreadsheet_id: str, sheet_name: Optional[str] = None) -> List[List[str]]:
    """Return the raw values from a sheet as a list of rows (each row is a list of strings).

    If `sheet_name` is None, fetches the first sheet by using the range 'A:Z'.
    """
    service = get_sheets_service()
    range_name = f"{sheet_name}" if sheet_name else "A:Z"
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get("values", [])
    logger.info("Fetched %d rows from sheet %s", len(values), sheet_name or '(first range)')
    return values


def export_sheet_to_csv(spreadsheet_id: str, sheet_name: Optional[str] = None, output_path: str = "data/solutions_from_sheets.csv") -> str:
    """Fetch a sheet and write it to a CSV file. Returns the path to the CSV.

    The function will create parent directories if needed.
    """
    values = fetch_sheet_values(spreadsheet_id, sheet_name)
    if not values:
        raise ValueError("Sheet is empty or not accessible")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in values:
            writer.writerow(row)
    logger.info("Wrote sheet to %s", output_path)
    return output_path


def update_sheet_from_csv(spreadsheet_id: str, csv_path: str, sheet_name: Optional[str] = None, clear_first: bool = True) -> None:
    """Replace the contents of a sheet with the CSV at `csv_path`.

    If `sheet_name` is None the first sheet will be targeted.
    This function performs a value update over the sheet's A1 range.
    """
    try:
        from googleapiclient.errors import HttpError
    except Exception:
        logger.error("googleapiclient is required to update sheets")
        raise

    service = get_sheets_service()
    sheets = service.spreadsheets()

    # Read CSV values
    values = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            values.append(row)

    if not values:
        raise ValueError("CSV is empty")

    # If sheet_name unspecified attempt to write to the first sheet by using A1 notation
    range_name = f"{sheet_name}!A1" if sheet_name else "A1"

    body = {"values": values}

    try:
        if clear_first and sheet_name:
            # clear the full sheet before writing
            sheets.values().clear(spreadsheetId=spreadsheet_id, range=sheet_name).execute()

        result = sheets.values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption="RAW", body=body).execute()
        logger.info("Updated sheet %s with %d cells", spreadsheet_id, result.get("updatedCells"))
    except HttpError as e:
        logger.error("Failed to update sheet: %s", e)
        raise


def normalize_header(headers: List[str]) -> List[str]:
    """Normalize header names to lower_snake (basic)."""
    norm = []
    for h in headers:
        h2 = h.strip().lower().replace(" ", "_")
        norm.append(h2)
    return norm


def import_sheet_to_db(spreadsheet_id: str, sheet_name: Optional[str] = None) -> int:
    """Import rows from a Google Sheet into the Django database.

    Returns the number of created ClimateSolution objects.
    """
    # Import Django ORM lazily so the module can also be used without Django
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "climate_solutions.settings")
    django.setup()

    from solutions.models import Location, Category, CostLevel, Timeframe, SolutionType, ClimateSolution

    values = fetch_sheet_values(spreadsheet_id, sheet_name)
    if not values:
        logger.warning("No data found in sheet %s", spreadsheet_id)
        return 0

    headers = normalize_header(values[0])
    rows = values[1:]

    # Required minimal headers
    required = {"name", "category"}
    if not required.issubset(set(headers)):
        raise ValueError(f"Sheet must contain headers including: {required}. Found: {headers}")

    created = 0
    for r in rows:
        # create a dict mapping header->value, safely handling missing columns
        data = {h: (r[i] if i < len(r) else "") for i, h in enumerate(headers)}

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

    logger.info("Imported %d new solutions from sheet %s", created, spreadsheet_id)
    return created


def _parse_args():
    p = argparse.ArgumentParser(description="Fetch or import a Google Sheet of climate solutions")
    p.add_argument("--sheet-id", required=True, help="Google Sheets spreadsheet ID")
    p.add_argument("--sheet-name", help="Optional sheet/tab name")
    p.add_argument("--export", action="store_true", help="Export sheet to CSV")
    p.add_argument("--out", default="data/solutions_from_sheets.csv", help="Output CSV path when exporting")
    p.add_argument("--import", dest="do_import", action="store_true", help="Import sheet rows into the Django DB")
    return p.parse_args()


def main():
    args = _parse_args()
    if args.export:
        export_sheet_to_csv(args.sheet_id, args.sheet_name, args.out)
        return
    if args.do_import:
        count = import_sheet_to_db(args.sheet_id, args.sheet_name)
        logger.info("Imported rows: %d", count)
        return
    logger.error("No action specified. Use --export or --import")


if __name__ == "__main__":
    main()
