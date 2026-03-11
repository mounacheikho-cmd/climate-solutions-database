# How to run and understand the Climate Solutions app (Beginner-friendly)

This guide explains, step-by-step, how to run the project locally and what each part of the application does. It's written for beginners.

## Overview
This project contains:

- A Django backend that stores climate adaptation solutions and exposes a small REST API.
- A React frontend (Create React App) that can call the API to list and filter solutions.
- A sample dataset at `/data/solutions.csv` and a management command to import it.

There are three main things you will do to run the app locally:

1. Prepare a Python virtual environment and install dependencies.
2. Run Django migrations and import sample data.
3. Start the Django server and (optionally) the React development server.

## Step 0 — Prerequisites
- Python 3.11 installed and available as `python`.
- Node.js and npm (if you want to run the frontend dev server).
- Git (optional but useful).

## Step 1 — Prepare a virtual environment and install Python dependencies

Open a terminal in the project's root directory and run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

What this does:
- `python -m venv .venv` creates an isolated environment named `.venv` so dependencies don't affect your system Python.
- `source .venv/bin/activate` activates that environment.
- `pip install -r requirements.txt` installs the packages the project needs (Django, DRF, etc.).

If you hit errors installing packages, check the error text — often it's because a package requires a certain Python version or system library. Tell us the error and we can help.

## Step 2 — Run migrations and import sample data

Initialize the database and load the sample dataset:

```bash
python manage.py migrate
python manage.py import_solutions
```

What this does:
- `migrate` creates the SQLite database schema based on Django models.
- `import_solutions` is a management script included in `solutions/management/commands/import_solutions.py` that reads `/data/solutions.csv` and creates database records.

You can examine the database file `db.sqlite3` with a GUI SQLite browser or use Django admin.

## Step 3 — Run the backend server

Start the Django development server:

```bash
python manage.py runserver
```

By default this serves at `http://127.0.0.1:8000/`.

API endpoints to try:
- `GET /api/solutions/` — list solutions (supports query params: `?category=...&country=...&tag=...`).
- `GET /api/solutions/export_csv/` — export filtered results as CSV.
- `POST /api/import-csv/` — upload a CSV file via multipart form (field name `file`) to import rows.

You can use `curl` or your browser to explore the GET endpoints.

## Step 4 (optional) — Run the frontend dev server

The frontend is a Create React App project in `frontend/`.

```bash
cd frontend
npm install
npm start
```

This starts a development server at `http://localhost:3000` and will proxy API requests to the Django server if running on the same machine.

## Project structure (simple explanation)

- `climate_solutions/` — Django project settings and URLs.
- `manage.py` — helper script to run Django commands (migrations, runserver, tests, custom commands).
- `solutions/` — the main Django app containing models, views (API), serializers, tests, and management commands.
  - `models.py` — the database schema (Location, Category, ClimateSolution, etc.).
  - `views_api.py` & `urls.py` — the REST API for listing and importing solutions.
  - `management/commands/import_solutions.py` — script to import CSV into the DB.
  - `services/google_sheets.py` — helper to fetch a Google Sheet and either export it as CSV or import rows directly into the DB. Use the environment variable `GOOGLE_SERVICE_ACCOUNT_FILE` to point to a service-account JSON key, then run the module to import/export.
- `frontend/` — React app (UI for filtering and exporting results).
- `data/solutions.csv` — sample CSV dataset with 20+ entries.
- `requirements.txt` — pinned Python dependencies.
- `.github/workflows/ci.yml` — example CI config to run tests in GitHub Actions.

## Running tests

With the virtualenv active:

```bash
python manage.py test
```

This runs Django tests. (If you prefer `pytest`, you can run `pytest -q`.)

## Useful tips if you get stuck
- If `python` points to a different version, use `python3.11` (or your correct interpreter) when creating the venv.
- If `pip install -r requirements.txt` fails on a package, copy the error message and ask — I can help diagnose.
- If the frontend can't reach the backend, ensure both servers are running and check the browser console.

## Next steps you might want
- Add more fields or mapping in the CSV import to populate tags and other columns.
- Wire up authentication and secure configuration for production.
- Improve frontend with pagination controls and better filters.

Enjoy exploring the project. If you want, I can run these steps here (create the venv, install deps, run migrations and tests) and report back any errors.
