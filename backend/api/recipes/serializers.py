from rest_framework import serializers

from api.users.serializers import UsersListSerializer
from recipes.models import Tag, Recipe


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения списка тэгов рецептов.
    """

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'id',)
        read_only_fields = fields


# class RecipeSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Recipe
#         fields = ('__all__',)

class RecipesListSerializer(serializers.ModelSerializer):
    """
    Сериалзатор обратки GET-запросов на 'api/recipes'.
    """

    author = UsersListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @staticmethod
    def get_ingredients(object):
        """
        Получает ингредиенты и их количество из модели RecipeIngredientAmount.

        """

    def get_is_favorited(self, object):
        """Проверяет, добавил ли текущий пользователь рецепт в избанное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favoriting.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        """Проверяет, добавил ли текущий пользователь
        рецепт в список покупок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()