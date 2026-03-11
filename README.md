# Climate Solutions App

Minimal implementation for the Code/Work Challenge: Climate Adaptation Solutions.

Quick start (macOS, python3.11+):

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations and import sample data:

```bash
python manage.py migrate
python manage.py import_solutions
```

3. Run tests:

```bash
pytest -q
```

4. Run server:

```bash
python manage.py runserver
```

API endpoints:
- GET /api/solutions/ - list (supports ?category=&country=&tag=)
- GET /api/solutions/{pk}/ - retrieve
- GET /api/solutions/export_csv/ - export current filtered set as CSV
- POST /api/import-csv/ - multipart upload with 'file' field (CSV)

Data sample: `/data/solutions.csv` (20+ rows)
