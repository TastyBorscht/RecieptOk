from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters

from recipes.models import Recipe


class IngredientSearchFilter(drf_filters.SearchFilter):
    """Фильтр поиска по названию ингредиента."""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Фильтр выборки рецептов по определенным полям."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favoriting__user=self.request.user)
            return queryset
        return queryset.none()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset
        return queryset.none()
