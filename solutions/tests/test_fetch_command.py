import os
import csv
import shutil
import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_fetch_solutions_import(tmp_path):
    """Write a temporary curated CSV, run fetch_solutions and import into DB."""
    project_root = os.getcwd()
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    curated_path = os.path.join(data_dir, "curated_solutions.csv")
    backup_path = None
    if os.path.exists(curated_path):
        backup_path = curated_path + ".bak"
        shutil.copy(curated_path, backup_path)

    try:
        headers = [
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
        rows = [
            [
                "Mgmt Test Solution 1",
                "TestCat",
                "Testland",
                "A test solution",
                "Benefit",
                "Low",
                "Short-term",
                "https://example.org/test1",
                "test,import",
            ],
            [
                "Mgmt Test Solution 2",
                "TestCat2",
                "Testland",
                "Another test solution",
                "Benefit2",
                "Medium",
                "Short-term",
                "https://example.org/test2",
                "test,import",
            ],
        ]
        with open(curated_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)

        out_path = os.path.join(data_dir, "test_combined.csv")
        # run management command to merge and import
        call_command("fetch_solutions", f"--out={out_path}", "--import-to-db")

        # assert DB has at least 2 new solutions
        from solutions.models import ClimateSolution

        count = ClimateSolution.objects.filter(name__icontains="Mgmt Test Solution").count()
        assert count >= 2
    finally:
        # restore backup
        if backup_path and os.path.exists(backup_path):
            shutil.move(backup_path, curated_path)
        else:
            try:
                os.remove(curated_path)
            except Exception:
                pass
*** End Patch