from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import User, UserSerializer, UsersListSerializer
from .serializers import UserTokenSerializer
from .mixins import RegistrationAuthMixin
from .utils import sending_mail


class UsersListForAll(viewsets.ModelViewSet):
    """
    Получение списка пользователей кем угодно
    по get запросу на api/users.
    """
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']


class UsersForAdminViewSet(viewsets.ModelViewSet):
    """
    Создание, редактирование, удаление, список от лица Админа.
    При запросе обычного пользователя на me, возвращает страницу автора.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    def get_serializer_context(self):
        """Дополнительные данные в сериализатор."""
        context = super().get_serializer_context()
        context.update({
            'creator': self.request.user
        })
        return context

    def get_user(self, username):
        return User.objects.get(username=username)

    @action(methods=['get'], detail=False, url_path='me',
            permission_classes=(IsAuthenticated,))
    def owner_get(self, request):
        """
        Страница пользователя, можно только смотреть.
        """
        user = self.get_user(self.request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @owner_get.mapping.patch
    def owner_patch(self, request):
        """
        Страница пользователя, можно только менять.
        """
        user = self.get_user(self.request.user)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationAuthViewSet(RegistrationAuthMixin):
    """
    Создание пользователя собственноручно, от лица анонима.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    pagination_class = None

    def get_user(self, username):
        return get_object_or_404(User, username=username)

    def get_serializer_context(self):
        """Дополнительные данные в сериализатор."""
        context = super().get_serializer_context()
        context.update({
            'creator': self.request.user
        })
        return context

    @action(methods=['post'], detail=False, url_path='signup')
    def user_create(self, request):
        """
        Создаёт пользователя или высылает письмо
        с кодом для токена повторно.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data['username']
        email = request.data['email']
        if User.objects.filter(username=username, email=email).exists():
            sending_mail(self.get_user(username))
            return Response(
                ['Письмо выслано повторно'], status=status.HTTP_200_OK
            )
        serializer.save()
        sending_mail(self.get_user(username))
        return Response(request.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'], detail=False, url_path='token',
        serializer_class=UserTokenSerializer)
    def token(self, request):
        """
        Возвращает токен при верных данных илиразличные ошибки:
        неверный код, не существует username, неверные вводные.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user(request.data['username'])
        return Response(user.user_token, status=status.HTTP_200_OK)
