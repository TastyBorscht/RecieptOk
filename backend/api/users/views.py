from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscription
from .serializers import User, UsersListSerializer, UserCreateSerializer, AvatarSerializer, ChangePasswordSerializer,\
    SubscribeSerializer
from ..recipes.permissions import AnonimOrAuthenticatedReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    Получение списка пользователей по GET-запросу на '/api/users',
    Получение данных о пользователе по GET-запросу на '/api/users/{id}/',
    Получение данных о пользователе по GET-запросу на '/api/users/me/',
    Добавление пользователя по POST-запросу на '/api/users/'.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer
    http_method_names = ['get', 'post', 'delete', 'put']

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return UsersListSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
            status=status.HTTP_201_CREATED
        )

    def get_permissions(self):
        if self.action in [
            'update_avatar',
            'delete_avatar',
            'set_password',
            'get_subscribe',
            'get_me',
        ]:
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me/')
    def get_me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, subscriber=user)
                return Response({'Подписка успешно создана': serializer.data},
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if Subscription.objects.filter(author=author, subscriber=user).exists():
            Subscription.objects.get(author=author).delete()
            return Response('Успешная отписка',
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_404_NOT_FOUND)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        follows = Subscription.objects.filter(subscriber=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = SubscribeSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)


class LegendAvatarView(APIView):
    """Вью-класс управляющий Аватаром."""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    def put(self, request):
        user = request.user
        if 'avatar' not in request.data:
            return Response(
                {"detail": "Field 'avatar' is required."}, status=status.HTTP_400_BAD_REQUEST
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
        return Response({"detail": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND)


class UpdatePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (IsAuthenticated, )
    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.data.get("current_password")
            if not self.object.check_password(current_password):
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
