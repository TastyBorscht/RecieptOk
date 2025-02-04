from django.urls import include, path
from rest_framework import routers

from .constants import VERSION_ONE_PREFIX
# from .titles.views import TitleViewSet, CategoryViewSet, GenreViewSet

api_router = routers.DefaultRouter()
# v1_router.register('titles', TitleViewSet)
# v1_router.register('categories', CategoryViewSet)
# v1_router.register('genres', GenreViewSet)


urlpatterns = [
    path('', include(api_router.urls)),
    path('users/', include('api.users.urls')),
    # path(f'{VERSION_ONE_PREFIX}/titles/', include('api.reviews.urls')),
    ]