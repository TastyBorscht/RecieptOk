from django.urls import include, path
from rest_framework import routers

from .views import LegendAvatarView, UpdatePasswordView, UserViewSet

user_router = routers.DefaultRouter()
user_router.register('', UserViewSet)

urlpatterns = [
    path('me/avatar/', LegendAvatarView.as_view(), name='avatar'),
    path('me/', UserViewSet.as_view({'get': 'get_me'}), name='user-me'),
    path('set_password/', UpdatePasswordView.as_view(), name='set_password'),
    path('', include(user_router.urls)),
]
