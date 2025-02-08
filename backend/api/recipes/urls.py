from api.recipes.views import RecipeViewSet
from django.urls import include, path
from rest_framework import routers

recipes_router = routers.DefaultRouter()
recipes_router.register('', RecipeViewSet)

urlpatterns = [
    path('', include(recipes_router.urls)),
]
