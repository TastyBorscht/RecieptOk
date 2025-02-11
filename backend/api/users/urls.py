from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, LegendAvatarView

user_router = routers.DefaultRouter()
user_router.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    # path('me/avatar/', LegendAvatarView.as_view(), name='avatar'),
    path('', include(user_router.urls)),
]
