#  эти странные импорты, как ни странно, результат работы isort.
from rest_framework import serializers

from recipes.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """ Сериалиазтор для модели TagViewSet. """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = fields
