import pytest

def test_import_csv_no_file(client):
	resp = client.post('/api/import-csv/', {}, format='multipart')
	assert resp.status_code == 400
	data = resp.json()
	assert 'detail' in data

def test_admin_fetch_endpoint_starts(client):
	# Admin fetch endpoint is currently AllowAny; ensure POST returns started
	resp = client.post('/api/admin/fetch_solutions/', data={})
	assert resp.status_code == 200
	assert resp.json().get('status') == 'started'
