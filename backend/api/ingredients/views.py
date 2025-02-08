from api.ingredients.serializers import IngredientSerializer
from api.recipes.filters import IngredientSearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientSearchFilter
    search_fields = ('^name', )
