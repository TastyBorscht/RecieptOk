from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from .constants import VERSION_ONE_PREFIX
# from .views import CustomTokenCreateView, CustomTokenDestroyView

# from .titles.views import TitleViewSet, CategoryViewSet, GenreViewSet

api_router = routers.DefaultRouter()
# v1_router.register('titles', TitleViewSet)
# v1_router.register('categories', CategoryViewSet)
# v1_router.register('genres', GenreViewSet)


urlpatterns = [
    path('tags/', include('api.tags.urls')),
    path('users/', include('api.users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/', include('djoser.urls.authtoken')),
    path('', include(api_router.urls)),
    # path('api/auth/token/login/', CustomTokenCreateView.as_view(), name='token_login'),
    # path('api/auth/token/logout/', CustomTokenDestroyView.as_view(), name='token_logout'),
    # path('auth/', include('djoser.urls.authtoken')),
    # path(f'{VERSION_ONE_PREFIX}/titles/', include('api.reviews.urls')),
    ]