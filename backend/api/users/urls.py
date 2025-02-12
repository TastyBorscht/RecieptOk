from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers

from .views import CustomUserViewSet


user_router = routers.DefaultRouter()
user_router.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    path('me/', UserViewSet.as_view({
        'get': 'me',
    }), name='user-me'),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/', include('djoser.urls')),
    path('', include(user_router.urls)),
]
