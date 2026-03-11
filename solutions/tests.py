from django.test import TestCase, Client
from django.core.management import call_command
from django.conf import settings
import os
from .models import ClimateSolution


class ImportCommandTest(TestCase):
	def test_import_creates_solutions(self):
		path = os.path.join(settings.BASE_DIR, 'data', 'solutions.csv')
		call_command('import_solutions', path=path)
		self.assertGreaterEqual(ClimateSolution.objects.count(), 20)


class APITest(TestCase):
	def setUp(self):
		path = os.path.join(settings.BASE_DIR, 'data', 'solutions.csv')
		call_command('import_solutions', path=path)
		self.client = Client()

	def test_list_solutions(self):
		resp = self.client.get('/api/solutions/')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		# paginated response
		self.assertIn('results', data)
		self.assertGreaterEqual(len(data['results']), 1)
