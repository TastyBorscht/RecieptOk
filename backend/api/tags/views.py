from api.tags.serializers import TagSerializer
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Tag. """
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
