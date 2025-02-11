from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.response import Response

from recipes.models import Recipe
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from users.constants import (
    LENGTH_CHARFIELDS,
    LENGTH_EMAIL,
    UNIQUE_EMAIL,
    UNIQUE_USERNAME
)
from users.models import Subscription

User = get_user_model()


# class CustomUserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для создания объекта класса User."""
#
#     avatar = Base64ImageField()
#
#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'password',
#             'avatar',
#         )
#         extra_kwargs = {"password": {"write_only": True}}
#
#     def validate(self, data):
#         """Запрещает пользователям присваивать себе username me
#         и использовать повторные username и email."""
#         if data.get('username') == 'me':
#             raise serializers.ValidationError(
#                 'Использовать имя me запрещено'
#             )
#         if User.objects.filter(username=data.get('username')):
#             raise serializers.ValidationError(
#                 'Пользователь с таким username уже существует'
#             )
#         if User.objects.filter(email=data.get('email')):
#             raise serializers.ValidationError(
#                 'Пользователь с таким email уже существует'
#             )
#         return data
#
#     def create(self, validated_data):
#         """Создаёт пользователя с учётом поля avatar."""
#         avatar = validated_data.pop('avatar', None)  # Извлекаем avatar из данных
#         user = super().create(validated_data)  # Создаём пользователя
#         if avatar:
#             user.avatar = avatar  # Присваиваем avatar, если он был передан
#             user.save()
#         return user

class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
        }

    def validate(self, data):
        """Запрещает пользователям присваивать себе username me
        и использовать повторные username и email.
        Также проверяет наличие полей first_name и last_name."""

        if 'first_name' not in data or not data['first_name']:
            raise serializers.ValidationError(
                {"first_name": "Это поле обязательно."}
            )

        if 'last_name' not in data or not data['last_name']:
            raise serializers.ValidationError(
                {"last_name": "Это поле обязательно."}
            )

        if data.get('username') == 'me':
            raise serializers.ValidationError(
                {"username": "Использовать имя me запрещено"}
            )

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError(
                {"username": "Пользователь с таким username уже существует"}
            )

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )

        return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def validate(self, data):
        """Запрещает пользователям изменять себе username на me."""
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscribeRecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор предназначен для вывода рецептом в FollowSerializer."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class UserRecipieSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полей ApiUser при создании рецепта."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscriber'
        )

    def validate(self, data):
        """Запрещает пользователям изменять себе username на me."""
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Serializer для модели Subscription."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return (Subscription.objects.filter(
                subscriber=obj.subscriber,
                author=obj.author
            ).exists())
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return SubscribeRecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar.url
        return None

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        request_method = self.context.get('request').method

        # Проверка на существующую подписку для POST-запроса
        if request_method == 'POST':
            if Subscription.objects.filter(author=author, subscriber=user).exists():
                raise ValidationError(
                    detail='Вы уже подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                raise ValidationError(
                    detail='Невозможно подписаться на себя!',
                    code=status.HTTP_400_BAD_REQUEST
                )

        if request_method == 'DELETE':
            if not Subscription.objects.filter(author=author, subscriber=user).exists():
                raise ValidationError(
                    detail='Вы не подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST
                )

        return data


