import pyshorteners
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.recipes.filters import RecipeFilter
from api.recipes.permissions import AuthorOrReadOnly
from api.recipes.serializers import (
    FavoriteSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipesListSerializer,
    ShoppingCartSerializer,
)
from api.recipes.utils import create_shopping_cart
from api.tags.serializers import TagSerializer
from recipes.models import (
    Favorite,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


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
    """Вьюсет для создания объектов класса Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def _handle_post_delete_action(self, request, pk, model, serializer_class):
        """Общий метод для обработки добавления и удаления объектов."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = serializer_class(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            short_serializer = RecipeShortSerializer(recipe)
            return Response(
                short_serializer.data, status=status.HTTP_201_CREATED
            )
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            model.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def get_post_favorite(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты в избранное."""
        return self._handle_post_delete_action(
            request, pk, Favorite, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Позволяет текущему пользователю
        добавлять рецепты в список покупок."""
        return self._handle_post_delete_action(
            request, pk, ShoppingCart, ShoppingCartSerializer
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет текущему пользователю загрузить список покупок."""
        ingredients_cart = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)

    def get_serializer_class(self):
        """Определяет, какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return RecipesListSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get_link',
        permission_classes=(permissions.AllowAny,)
    )
    def get_link(self, request, pk):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        long_url = request.build_absolute_uri(reverse(
            'recipe-detail', args=[recipe.id]
        ))
        s = pyshorteners.Shortener()
        short_link = s.tinyurl.short(long_url)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
