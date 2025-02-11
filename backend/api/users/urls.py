from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet

user_router = routers.DefaultRouter()
user_router.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(user_router.urls)),
]
