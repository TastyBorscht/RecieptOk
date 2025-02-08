from api.ingredients.serializers import (
    IngredientAmountSerializer,
    IngredientFullSerializer
)
from api.tags.serializers import TagSerializer
from api.users.serializers import UserRecipieSerializer, UsersListSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Favorite, IngredientInRecipe, Recipe, ShoppingCart
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class RecipesListSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при GET запросах."""

    tags = TagSerializer(many=True, read_only=True)
    author = UsersListSerializer(read_only=True)
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
        ingredients = IngredientInRecipe.objects.filter(recipe=object)
        return IngredientFullSerializer(ingredients, many=True).data

    def get_is_favorited(self, object):
        """Проверка рецепт-избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        request = self.context.get('request')
        return request.user.favoriting.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        """Проверка рецепт-корзина."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при небезопасных запросах."""
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserRecipieSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate_ingredients(self, ingredients):
        """Проверяем, что рецепт содержит уникальные ингредиенты
        и их количество не меньше 1."""
        if not ingredients:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть уникальными'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            if int(ingredient.get('amount')) > 100:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть больше 100'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверяем, что рецепт содержит уникальные теги."""
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    def validate_image(self, image):
        """Проверка на наличие картинки блюда."""
        if image is None:
            raise serializers.ValidationError(
                'Требуется изображение.'
            )
        return image

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        """Добавляет ингредиенты."""
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    # @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    # @transaction.atomic
    def update(self, instance, validated_data):
        if 'ingredients' not in validated_data or 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Необходимо предоставить поля ingredients и tags.'
            )
        recipe = instance
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients_data, recipe)
        instance.save()
        return instance

    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipesListSerializer(recipe)
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для компактного отображения рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в список покупок'
            )
        ]
