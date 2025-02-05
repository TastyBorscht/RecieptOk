from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.tags.serializers import TagSerializer
from tags.models import Tag


class TagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get',]
