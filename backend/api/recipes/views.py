from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.recipes.serializers import RecipeSerializer
from api.tags.serializers import TagSerializer
from recipes.models import Tag, Recipe


class TagViewSet(viewsets.ModelViewSet):
    """
    Отображает список тэгов рецептов по GET-запросу на 'api/tags'.
    """

    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

class RecipeViewSet(viewsets.ModelViewSet):
    """
    Отображает список рецептов по GET-запросу на 'api/recipes'.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get']
    permission_classes = (AllowAny,)
