import pytest


@pytest.mark.django_db
def test_create_solution_models():
	from solutions.models import (
		Location,
		Category,
		CostLevel,
		Timeframe,
		SolutionType,
		ClimateSolution,
	)

	loc = Location.objects.create(country="Testland", region="Region A", climate_zone="Tropical")
	cat = Category.objects.create(name="Nature-based", description="NbS")
	cost = CostLevel.objects.create(level="Low", description="Low cost")
	tf = Timeframe.objects.create(period="Short-term", description="1-2 years")
	st = SolutionType.objects.create(name="Ecosystem", description="Nature-based")

	sol = ClimateSolution.objects.create(
		name="Test Mangrove Restoration",
		location=loc,
		category=cat,
		description="Restore mangroves",
		benefits="Coastal protection",
		cost=cost,
		timeframe=tf,
		solution_type=st,
		source_url="https://example.org/mangrove",
		tags=["mangrove", "coastal"],
	)

	assert sol.id is not None
	assert str(sol.location) == "Testland, Region A"
	assert sol.tags == ["mangrove", "coastal"]
	assert sol.category.name == "Nature-based"
