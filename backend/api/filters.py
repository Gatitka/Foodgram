from django_filters import FilterSet, filters
from recipe.models import Recipe


class CharFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
