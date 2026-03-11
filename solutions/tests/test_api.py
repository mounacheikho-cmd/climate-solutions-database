import io
import csv
import pytest


@pytest.mark.django_db
def test_import_csv_api(client):
	# prepare a small CSV in memory matching the expected headers
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
			"API Test Solution",
			"TestCat",
			"Testland",
			"A test solution",
			"Benefit",
			"Low",
			"Short-term",
			"https://example.org/test",
			"test,api",
		]
	]
	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow(headers)
	w.writerows(rows)
	buf.seek(0)

	response = client.post("/api/import-csv/", {"file": io.BytesIO(buf.getvalue().encode("utf-8"))}, format="multipart")
	assert response.status_code == 200
	data = response.json()
	assert data.get("created") == 1


def test_export_csv_endpoint(client, db):
	# ensure the export endpoint responds (no auth required)
	resp = client.get("/api/solutions/export_csv/")
	assert resp.status_code in (200, 302)  # 200 or redirect depending on config
