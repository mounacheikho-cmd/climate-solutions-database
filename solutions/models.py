from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField

class Location(models.Model):
    """Location lookup table"""
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    climate_zone = models.CharField(max_length=50)
    
    class Meta:
        indexes = [
            models.Index(fields=['country', 'region']),
        ]
    
    def __str__(self):
        return f"{self.country}, {self.region}"

class Category(models.Model):
    """Solution category lookup"""
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class CostLevel(models.Model):
    """Implementation cost levels"""
    level = models.CharField(max_length=20, unique=True)  # Low, Medium, High
    description = models.CharField(max_length=200)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.level

class Timeframe(models.Model):
    """Implementation timeframe"""
    period = models.CharField(max_length=20, unique=True)  # Short-term, Medium-term, Long-term
    description = models.CharField(max_length=200)
    min_years = models.IntegerField(null=True, blank=True)
    max_years = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.period

class SolutionType(models.Model):
    """Type of solution (Nature-based, Technology-based, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class ClimateSolution(models.Model):
    """Main solution model"""
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField()
    benefits = models.TextField()
    cost = models.ForeignKey(CostLevel, on_delete=models.PROTECT)
    timeframe = models.ForeignKey(Timeframe, on_delete=models.PROTECT)
    solution_type = models.ForeignKey(SolutionType, on_delete=models.PROTECT)
    source_url = models.URLField(validators=[URLValidator()])
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'location']),
            models.Index(fields=['cost', 'timeframe']),
        ]
    
    def __str__(self):
        return self.name