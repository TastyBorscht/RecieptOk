from django.urls import include, path
from rest_framework import routers

from api.recipes.views import RecipeViewSet


recipes_router = routers.DefaultRouter()
recipes_router.register('', RecipeViewSet)

urlpatterns = [
    path('', include(recipes_router.urls)),
]
