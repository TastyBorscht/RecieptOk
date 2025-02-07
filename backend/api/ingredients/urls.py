from django.urls import include, path
from rest_framework import routers

from api.ingredients.views import IngredientViewSet

ingredient_router = routers.DefaultRouter()
ingredient_router.register('', IngredientViewSet)

urlpatterns = [
    path('', include(ingredient_router.urls)),
]
