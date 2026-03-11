from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import csv
from .models import ClimateSolution, Location, Category, CostLevel, Timeframe, SolutionType
from .serializers import ClimateSolutionSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser


class ClimateSolutionViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides list and retrieve endpoints with simple filtering via query params."""
    queryset = ClimateSolution.objects.all().order_by('name')
    serializer_class = ClimateSolutionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # simple filters: category, location, cost, timeframe, tags
        category = self.request.query_params.get('category')
        country = self.request.query_params.get('country')
        tag = self.request.query_params.get('tag')
        if category:
            qs = qs.filter(category__name__icontains=category)
        if country:
            qs = qs.filter(location__country__icontains=country)
        if tag:
            qs = qs.filter(tags__icontains=tag)
        return qs

    @action(detail=False)
    def export_csv(self, request):
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="solutions_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'category', 'country', 'region', 'cost', 'timeframe', 'source_url'])
        for s in qs:
            writer.writerow([s.id, s.name, s.category.name, s.location.country, s.location.region, s.cost.level, s.timeframe.period, s.source_url])
        return response


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class ImportCSVView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """Accept a multipart file 'file' containing a CSV in the normalized schema and import rows."""
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        decoded = f.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        created = 0
        for row in reader:
            # create or get lookup fields conservatively
            loc, _ = Location.objects.get_or_create(country=row.get('geographic_applicability', 'Unknown'), region='')
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
        return Response({'created': created})
