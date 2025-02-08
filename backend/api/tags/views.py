from api.tags.serializers import TagSerializer
from recipes.models import Tag
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


class TagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']
