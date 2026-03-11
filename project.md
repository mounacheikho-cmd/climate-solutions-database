# Code / Work Challenge: Climate Adaptation Solutions

## Overview
Build a data-driven application and supporting artifacts to discover, store, and filter climate adaptation solutions. The deliverables include a normalized dataset, automation for data collection, and a web application (backend + frontend) that enables filtering and analysis.

## Goals
- Collect and normalize at least 20 climate adaptation solutions.
- Produce a reusable, filterable dataset (Google Sheet / CSV).
- Implement an automation pipeline to gather and/or validate solution data.
- Build a production-ready backend and a frontend that supports filtering and ingestion of the dataset.
- Demonstrate enterprise-grade code quality, tests, and documentation.

## Scope & Requirements
- Data
    - Minimum 20 distinct solutions following provided guidelines.
    - Normalized schema suitable for filtering (e.g., id, name, category, scale, cost_estimate, climate_hazards_targeted, geographic_applicability, evidence_level, implementation_complexity, co-benefits, source_url, last_updated).
    - Deliver dataset as a Google Sheet and as CSV.

- Automation
    - Provide a script or small ETL pipeline that automates part of data collection or validation (e.g., web scraping, API calls, or structured prompts).
    - Include instructions to run the automation locally.

- Application
    - Backend: Python (Flask, FastAPI, or Django) that exposes endpoints to upload CSV or connect to the Google Sheet and provides filtered queries.
    - Frontend: Any modern framework (React, Vue, Svelte) or server-rendered templates if using Django. Provide a simple UI for filtering, paging, and exporting results.
    - Security: basic input validation, safe handling of uploaded files, and environment-based configuration for secrets.

- Quality & Best Practices
    - Code organized into logical modules/packages.
    - Configuration via environment variables and documented setup.
    - Logging and error handling.
    - Automated tests (unit + integration where appropriate).
    - CI configuration example (GitHub Actions or equivalent).
    - README with setup, run, and deployment instructions.

## Suggested Normalized Schema (example)
- id (string)
- name (string)
- category (string) — e.g., Nature-based, Infrastructure, Policy
- scale (string) — e.g., Local, Regional, National
- cost_estimate (string/number)
- climate_hazards_targeted (array/string) — e.g., sea-level rise, drought
- geographic_applicability (string)
- evidence_level (string) — e.g., pilot, proven, modeled
- implementation_complexity (string)
- co_benefits (string)
- source_url (string)
- last_updated (date)

## Deliverables
- Normalized Google Sheet URL (or shared file) and CSV export.
- Automation scripts and instructions (README).
- Backend repository with API docs and tests.
- Frontend repository or integrated app with filtering UI.
- Test suite and CI example.
- Short demo guide (how to run, key endpoints, example queries).

## Acceptance Criteria
- Data: ≥20 well-documented solutions in the normalized sheet.
- Automation: runnable script with clear inputs/outputs.
- App: ability to ingest CSV or connect to the Google Sheet and perform filtered queries via UI and API.
- Code Quality: tests passing, linting configured, and README covers setup and usage.
- Security & Stability: basic validations and configuration via environment variables.

## Evaluation Checklist
- [ ] Dataset normalized and complete (≥20 items)
- [ ] Automation works as documented
- [ ] Backend exposes filtering endpoints and accepts uploads
- [ ] Frontend provides usable filters and export
- [ ] Tests included and runnable
- [ ] CI and deployment notes provided
- [ ] README and demo instructions present

## Hints & Recommended Tech Stack
- Backend: Python + FastAPI or Django Rest Framework
- Frontend: React + Vite or Next.js (or simple server-side templates)
- Data automation: Python scripts (requests + BeautifulSoup, or relevant APIs)
- Testing: pytest, requests for integration tests
- CI: GitHub Actions
- Storage: Google Sheets API or cloud storage for CSVs

## Submission
- Provide a link to the repository (or zipped project) containing:
    - /data (CSV and sample Google Sheet export)
    - /scripts (automation)
    - /backend
    - /frontend (if separate)
    - README.md with run & test instructions

Keep artifacts minimal but reproducible; emphasize clarity, security, and test coverage.