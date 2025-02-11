from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscription

from .serializers import (
    AvatarSerializer,
    SubscribeSerializer,
    User, CustomUserSerializer
)


class CustomUserViewSet(UserViewSet):
    """Вью-сет для обрабтки запросов на 'api/users/'."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
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
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me(self, request):
        """Позволяет пользователю получить подробную информацию о себе
        и редактировать её."""
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False,
    #         methods=['put'],
    #         permission_classes=[IsAuthenticated],
    #         url_path='me/avatar')
    # def update_avatar(self, request):
    #     """Обновление аватара пользователя."""
    #     user = request.user
    #     if 'avatar' not in request.data:
    #         return Response(
    #             {"detail": "Field 'avatar' is required."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     serializer = AvatarSerializer(user, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors,
    #     status=status.HTTP_400_BAD_REQUEST)
    #
    # @action(detail=False,
    #         methods=['delete'],
    #         permission_classes=[IsAuthenticated],
    #         url_path='me/avatar')
    # def delete_avatar(self, request):
    #     user = request.user
    #     if user.avatar:
    #         user.avatar.delete()
    #         user.avatar = None
    #         user.save()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(
    #         {"detail": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND
    #     )

#  При попытке уйти от отдельного Вью для аватара я
#  неизбежно получаю ошибку Method \PUT\   not allowed либо 500,
#  свои попытки закомментил. Сразу пытался делать всё в одном классе,
#  LegendAvatarView это костыль ((


class LegendAvatarView(APIView):
    """Вью-класс управляющий Аватаром."""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def put(self, request):
        user = request.user
        if 'avatar' not in request.data:
            return Response(
                {"detail": "Field 'avatar' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND
        )
