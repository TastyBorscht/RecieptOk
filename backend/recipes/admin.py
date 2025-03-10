from django.contrib import admin

from .constants import MIN_NUM_INGREDIENTS
from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    """ Добавляет ингредиенты в рецепты в админке."""

    model = IngredientInRecipe
    min_num = MIN_NUM_INGREDIENTS


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'favorites_count',
        'get_ingredients',
        'cooking_time',
        'get_author',
        'name',
        'image',
        'text',
        'cooking_time',
        'created',
        'get_tags',
        'pk',
    )
    readonly_fields = ('favorites_count',)
    inlines = [
        IngredientAmountInline,
    ]
    search_fields = ('author', 'name')

    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.short_description = 'Количество добавлений в избранное'
    favorites_count.admin_order_field = 'favorites_count'

    def get_author(self, obj):
        """Возвращает автора рецепта."""
        return obj.author.username

    get_author.short_description = 'Автор'

    def get_ingredients(self, obj):
        """Возвращает список ингредиентов."""
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        """Возвращает список тегов."""
        return ", ".join([tag.name for tag in obj.tags.all()])

    get_tags.short_description = 'Теги'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register([Tag, Ingredient])
