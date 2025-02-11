from django.urls import include, path
from rest_framework import routers

from api.tags.views import TagViewSet


tag_router = routers.DefaultRouter()
tag_router.register('', TagViewSet)

urlpatterns = [
    path('', include(tag_router.urls)),
]
