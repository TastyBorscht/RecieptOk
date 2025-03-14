from django.urls import include, path
from rest_framework import routers


api_router = routers.DefaultRouter()

urlpatterns = [
    path('ingredients/', include('api.ingredients.urls')),
    path('recipes/', include('api.recipes.urls')),
    path('tags/', include('api.tags.urls')),
    path('users/', include('api.users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/', include('djoser.urls.authtoken')),
    path('', include(api_router.urls)),
]
