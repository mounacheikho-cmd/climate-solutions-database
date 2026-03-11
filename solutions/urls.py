from rest_framework import routers
from django.urls import path, include
from .views_api import ClimateSolutionViewSet, ImportCSVView, AdminFetchSolutionsView

router = routers.DefaultRouter()
router.register(r'solutions', ClimateSolutionViewSet, basename='solution')

urlpatterns = [
    path('', include(router.urls)),
    path('import-csv/', ImportCSVView.as_view(), name='import-csv'),
    path('admin/fetch_solutions/', AdminFetchSolutionsView.as_view(), name='admin-fetch-solutions'),
]
