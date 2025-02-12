from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from users.models import Subscription
from .serializers import (
    AvatarSerializer,
    SubscribeSerializer,
    User,
    UserProfileMeSerializer,
)


class CustomUserViewSet(UserViewSet):
    """Вью-сет для обрабтки запросов на 'api/users/'."""
    queryset = User.objects.all()
    serializer_class = UserProfileMeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'put']

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = self.request.user
        serializer = SubscribeSerializer(
            data=request.data,
            context={'request': request, 'author': author})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save(author=author, subscriber=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Subscription.objects.get(author=author).delete()
        return Response('Успешная отписка', status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        follows = request.user.subscriber.all()
        pages = self.paginate_queryset(follows)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['put'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        """Добавление или удаление аватара"""
        serializer = self._change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND
        )

    def _change_avatar(self, data):
        instance = self.get_instance()
        serializer = AvatarSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer
