from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.constants import (LENGTH_CHARFIELDS, LENGTH_EMAIL, UNIQUE_EMAIL,
                             UNIQUE_USERNAME)
from users.models import Subscription
from users.utils import validate_username

User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    """Сериализатор для выдачи всех пользователей всем
    по api/users."""
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user, author=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления нового пользователя
    по POST-запросу на api/users ."""
    username = serializers.CharField(
        max_length=LENGTH_CHARFIELDS,
        validators=[validate_username]
    )
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(max_length=LENGTH_EMAIL, required=True)
    first_name = serializers.CharField(
        write_only=True,
        required=True,
        max_length=150,
    )
    last_name = serializers.CharField(
        write_only=True,
        required=True,
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password',
        )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user = User.objects.filter(
            username=username,
            email=email,
        )
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if user.exists():
            return data
        if User.objects.filter(username=username).exists():
            raise ValidationError(UNIQUE_USERNAME)
        if User.objects.filter(email=email).exists():
            raise ValidationError(UNIQUE_EMAIL)

        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


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
    """Serializer для модели Follow."""
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
        if obj.author.avatar:  # Check if avatar exists
            return obj.author.avatar.url  # Return the URL if available
        return None

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Subscription.objects.filter(
                author=author,
                subscriber=user
        ).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return data
