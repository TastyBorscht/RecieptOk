from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import User, UsersListSerializer, UserCreateSerializer, AvatarSerializer, ChangePasswordSerializer


# from .serializers import UserTokenSerializer
# from .mixins import RegistrationAuthMixin
# from .utils import sending_mail


# class UsersListForAll(viewsets.ModelViewSet):
#     """
#     Получение списка пользователей кем угодно
#     по get запросу на api/users.
#     """
#     queryset = User.objects.all()
#     serializer_class = UsersListSerializer
#     permission_classes = (AllowAny,)
#     http_method_names = ['get']

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
            'set_password'
        ]:
            return (IsAuthenticated(),)
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='me/avatar')
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


# class UpdatePasswordView(UpdateAPIView):
#     """
#     An endpoint for changing password.
#     """
#     serializer_class = ChangePasswordSerializer
#     model = User
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['post']
#     def get_object(self, queryset=None):
#         obj = self.request.user
#         return obj
#
#     def update(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             # Check old password
#             if not self.object.check_password(serializer.data.get("current_password")):
#                 return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
#             # set_password also hashes the password that the user will get
#             self.object.set_password(serializer.data.get("new_password"))
#             self.object.save()
#             response = {
#                 'status': 'success',
#                 'code': status.HTTP_200_OK,
#                 'message': 'Password updated successfully',
#                 'data': []
#             }
#
#             return Response(response)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ChangePasswordView(UpdateAPIView):
#     """
#     An endpoint for changing password.
#     """
#     http_method_names = ['post']
#     serializer_class = ChangePasswordSerializer
#     model = User
#     permission_classes = (IsAuthenticated,)
#
#     def get_object(self, queryset=None):
#         obj = self.request.user
#         return obj
#
#     def update(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             # Check old password
#             if not self.object.check_password(serializer.data.get("current_password")):
#                 return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
#             # set_password also hashes the password that the user will get
#             self.object.set_password(serializer.data.get("new_password"))
#             self.object.save()
#             response = {
#                 'status': 'success',
#                 'code': status.HTTP_200_OK,
#                 'message': 'Password updated successfully',
#                 'data': []
#             }
#
#             return Response(response)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            # Check old password
            current_password = serializer.data.get("current_password")
            if not self.object.check_password(current_password):
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # @action(methods=['patch'], detail=False, url_path='me/set_password')
    # def set_password(self, request):
    #     user = request.user


    # def perform_create(self, serializer):
    #     return serializer.save()
# class UsersForAdminViewSet(viewsets.ModelViewSet):
#     """
#     Создание, редактирование, удаление, список от лица Админа.
#     При запросе обычного пользователя на me, возвращает страницу автора.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (IsAdminUser,)
#     http_method_names = ['get', 'post', 'patch', 'delete']
#     filter_backends = (filters.SearchFilter,)
#     lookup_field = 'username'
#     search_fields = ('username',)
#
#     def get_serializer_context(self):
#         """Дополнительные данные в сериализатор."""
#         context = super().get_serializer_context()
#         context.update({
#             'creator': self.request.user
#         })
#         return context
#
#     def get_user(self, username):
#         return User.objects.get(username=username)
#
#     @action(methods=['get'], detail=False, url_path='me',
#             permission_classes=(IsAuthenticated,))
#     def owner_get(self, request):
#         """
#         Страница пользователя, можно только смотреть.
#         """
#         user = self.get_user(self.request.user)
#         serializer = self.get_serializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @owner_get.mapping.patch
#     def owner_patch(self, request):
#         """
#         Страница пользователя, можно только менять.
#         """
#         user = self.get_user(self.request.user)
#         serializer = self.get_serializer(
#             user, data=request.data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class RegistrationAuthViewSet(RegistrationAuthMixin):
#     """
#     Создание пользователя собственноручно, от лица анонима.
#     """
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = UserSerializer
#     pagination_class = None
#
#     def get_user(self, username):
#         return get_object_or_404(User, username=username)
#
#     def get_serializer_context(self):
#         """Дополнительные данные в сериализатор."""
#         context = super().get_serializer_context()
#         context.update({
#             'creator': self.request.user
#         })
#         return context
#
#     @action(methods=['post'], detail=False, url_path='signup')
#     def user_create(self, request):
#         """
#         Создаёт пользователя или высылает письмо
#         с кодом для токена повторно.
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = request.data['username']
#         email = request.data['email']
#         if User.objects.filter(username=username, email=email).exists():
#             sending_mail(self.get_user(username))
#             return Response(
#                 ['Письмо выслано повторно'], status=status.HTTP_200_OK
#             )
#         serializer.save()
#         sending_mail(self.get_user(username))
#         return Response(request.data, status=status.HTTP_200_OK)
#
#     @action(
#         methods=['post'], detail=False, url_path='token',
#         serializer_class=UserTokenSerializer)
#     def token(self, request):
#         """
#         Возвращает токен при верных данных илиразличные ошибки:
#         неверный код, не существует username, неверные вводные.
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = self.get_user(request.data['username'])
#         return Response(user.user_token, status=status.HTTP_200_OK)
