import csv
from django.core.management.base import BaseCommand
from solutions.models import Location, Category, CostLevel, Timeframe, SolutionType, ClimateSolution
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Import solutions from data/solutions.csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to CSV file', default=os.path.join(settings.BASE_DIR, 'data', 'solutions.csv'))

    def handle(self, *args, **options):
        path = options['path']
        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f'File not found: {path}'))
            return
        created = 0
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # conservative mapping: geographic_applicability -> country
                country = row.get('geographic_applicability') or row.get('country') or 'Unknown'
                loc, _ = Location.objects.get_or_create(country=country, region='')
                cat, _ = Category.objects.get_or_create(name=row.get('category', 'Other'))
                cost, _ = CostLevel.objects.get_or_create(level=str(row.get('cost_estimate', 'Unknown')))
                tf, _ = Timeframe.objects.get_or_create(period=row.get('implementation_complexity', 'Unknown'))
                st, _ = SolutionType.objects.get_or_create(name=row.get('category', 'Other'))
                sol, created_flag = ClimateSolution.objects.get_or_create(
                    name=row.get('name'),
                    defaults={
                        'location': loc,
                        'category': cat,
                        'description': row.get('description', ''),
                        'benefits': row.get('co_benefits', ''),
                        'cost': cost,
                        'timeframe': tf,
                        'solution_type': st,
                        'source_url': row.get('source_url', ''),
                    }
                )
                if created_flag:
                    created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {created} solutions'))
