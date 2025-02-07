from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscription
from .serializers import User, UsersListSerializer, UserCreateSerializer, AvatarSerializer, ChangePasswordSerializer, \
    SubscriptionSerializer, SubscriptionShowSerializer


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
    http_method_names = ['get', 'post', 'delete']

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
            'retrieve',
            'update_avatar',
            'delete_avatar',
            'set_password',
            'get_subscribe',
        ]:
            return (IsAuthenticated(),)
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(instance=user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=False, url_path='me/avatar')
    def update_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
    )
    def get_subscribe(self, request, id):
        """Позволяет текущему пользователю подписываться/отписываться от
        от автора контента, чей профиль он просматривает."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
