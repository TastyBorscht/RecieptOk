from django.contrib import admin

from .models import Tag, Ingredient, Recipe

admin.site.register(
    (Tag, Ingredient, Recipe)
)