from api.ingredients.views import IngredientViewSet
from django.urls import include, path
from rest_framework import routers

ingredient_router = routers.DefaultRouter()
ingredient_router.register('', IngredientViewSet)

urlpatterns = [
    path('', include(ingredient_router.urls)),
]
