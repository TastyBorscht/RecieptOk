from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from users.models import Subscription
from users.utils import validate_username
from users.constants import (
    LENGTH_CHARFIELDS, LENGTH_EMAIL, UNIQUE_EMAIL, UNIQUE_USERNAME
)
from . import constants


User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    """Сериализатор для выдачи всех пользователей всем
    по api/users."""
    avatar = Base64ImageField()
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields


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
            'is_subscribed'
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


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Вы уже подписывались на этого автора'
            )
        ]

    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data['subscriber'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class SubscriptionRecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionShowSerializer(serializers.ModelSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        author_recipes = object.recipes.all()[:constants.RECIPES_MAX]
        return SubscriptionRecipeShortSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()
