from rest_framework import serializers
from .models import Location, Category, CostLevel, Timeframe, SolutionType, ClimateSolution


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'country', 'region', 'climate_zone']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'description']


class CostLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostLevel
        fields = ['id', 'level', 'description', 'min_amount', 'max_amount']


class TimeframeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeframe
        fields = ['id', 'period', 'description', 'min_years', 'max_years']


class SolutionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionType
        fields = ['id', 'name', 'description']


class ClimateSolutionSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    category = serializers.StringRelatedField()
    cost = serializers.StringRelatedField()
    timeframe = serializers.StringRelatedField()
    solution_type = serializers.StringRelatedField()

    class Meta:
        model = ClimateSolution
        fields = ['id', 'name', 'location', 'category', 'description', 'benefits', 'cost', 'timeframe', 'solution_type', 'source_url', 'tags', 'created_at', 'updated_at']
