import pytest
from unittest.mock import Mock

import solutions.services.google_sheets as gs


def test_import_sheet_to_db_with_mock(monkeypatch, db):
    # prepare fake sheet values: header + one row
    values = [[
        "name",
        "category",
        "geographic_applicability",
        "description",
        "co_benefits",
        "cost_estimate",
        "implementation_complexity",
        "source_url",
        "tags",
    ], [
        "Mocked Solution",
        "MockCat",
        "Mockland",
        "A mocked description",
        "benefit",
        "Low",
        "Short-term",
        "https://example.org/mocked",
        "mock"
    ]]

    fake_service = Mock()
    fake_values = Mock()
    fake_values.get.return_value.execute.return_value = {"values": values}
    fake_service.spreadsheets.return_value = fake_values

    monkeypatch.setattr(gs, "get_sheets_service", lambda: fake_service)

    # run importer
    created = gs.import_sheet_to_db("dummy_id")
    assert created >= 1


def test_update_sheet_from_csv_calls_api(monkeypatch, tmp_path):
    # create a small CSV
    csv_path = tmp_path / "small.csv"
    csv_path.write_text("name,category\nA,Cat\n")

    # create fake service that records update calls
    fake_service = Mock()
    fake_sheets = Mock()
    fake_sheets.values.return_value.update.return_value.execute.return_value = {"updatedCells": 2}
    fake_sheets.values.return_value.clear.return_value.execute.return_value = {}
    fake_service.spreadsheets.return_value = fake_sheets

    monkeypatch.setattr(gs, "get_sheets_service", lambda: fake_service)

    # should not raise
    gs.update_sheet_from_csv("dummy_id", str(csv_path), sheet_name="Sheet1")
    # verify update called
    assert fake_sheets.values.return_value.update.called
*** End Patch